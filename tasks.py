from RPA.Browser.Selenium import Selenium
from RPA.Excel.Files import Files
from RPA.HTTP import HTTP

from robocorp.tasks import get_output_dir, task
from robocorp import workitems

from dateutil.relativedelta import relativedelta
from datetime import datetime as dt
import shutil
import time
import re
import os

browser = Selenium()
http = HTTP()
output_folder_path = get_output_dir()


@task
def extract_data_from_latimes():

    for item in workitems.inputs:
        try:
            search_phrase = item.payload["Search phrase"]
            topic = item.payload["Topic"]
            months_number = item.payload["Months number"]
            months_number = 0 if months_number <= 1 else (months_number - 1) * -1
            limit_dt = (dt.today() + relativedelta(months=months_number, day=1)).date()
            print(f"Search for: {search_phrase}, {topic}, {months_number}")

            # 1. Open the site by following the link
            # 2. Enter a phrase in the search field
            # 3. On the result page, section from the Choose the latest (newest) news
            open_search_and_order(search_phrase)

            # 3. On the result page, If possible, select a news category
            filter_topic(topic)

            # 4. Get the values: title, date, and description.
            rows = get_news(limit_dt, search_phrase)

            # 5. Store in an Excel file:
            save_data_on_excel(rows, search_phrase)
                        
            # Create a zip file
            zip_path = shutil.make_archive(search_phrase, 'zip', output_folder_path)
            
            # Upload file to control room
            item.add_file(zip_path)
            item.save()
            item.done()

        except AssertionError as err:
            item.fail("BUSINESS", message=str(err))
        except Exception as err:
            item.fail("APPLICATION", message=str(err))

    if browser:
        browser.close_browser()


def open_search_and_order(search_phrase: str):

    browser.open_chrome_browser(
        url=f"https://www.latimes.com/search?q={search_phrase}&s=1",
        maximized=True,
        headless=False,
    )

    browser.set_selenium_timeout = 20

    # browser.wait_until_page_contains_element(f"//*[text()='Topics']")
    if browser.does_page_contain_element("//*[@class='search-results-module-no-results']"):
        raise AssertionError(f"There are not any results that match '{search_phrase}'")


def filter_topic(topic: str):

    if browser.does_page_contain_element(f"//*[*[text()='Topics']]//*[contains(text(),'{topic}')]"):
        browser.select_checkbox(f"//*[*[text()='Topics']]//*[*[contains(text(),'{topic}')]]/input")
        browser.click_element("//*[@class='button submit-button']")
        time.sleep(2)  # This is necessary for page to start loading
    browser.wait_until_page_contains_element("//*[@class='search-results-module-page-counts']")


def get_news(limit_dt: dt.date, search_phrase: str) -> list:

    pictures_folder_path = os.path.join(output_folder_path, search_phrase, "Pictures")
    os.makedirs(name=pictures_folder_path, exist_ok=True)

    pages_str = browser.get_text("//*[@class='search-results-module-page-counts']")
    pages_nr = int(pages_str.split(" of ")[1].replace(",", "")) + 1
    rows = []
    for p in range(1, pages_nr):
        for l in range(1, 11):
            # Date
            xpath = f"//*[@class='search-results-module-results-menu']/li[{l}]"
            date_str = browser.get_text(xpath + "//*[contains(@class,'promo-timestamp')]")
            if "ago" in date_str:
                date_dt = dt.today().date() + relativedelta(day=1)
            else:
                date_dt = dt.strptime(date_str, "%B %d, %Y").date() + relativedelta(day=1)

            if date_dt < limit_dt:
                return rows

            # Title
            title = browser.get_text(xpath + "//*//h3//*[@class='link']")

            # Description
            description = browser.get_text(xpath + "//*[@class='promo-description']")

            # Picture download
            picture_name = f"picture_{p}.{l}.png"
            picture_path = os.path.join(pictures_folder_path, picture_name)
            url = browser.get_element_attribute(xpath + "//*[@class='image']", "src")
            http.download(url=url, target_file=picture_path, overwrite=True)

            # Count search phrases
            count_search_phrases = title.upper().count(search_phrase.upper())
            count_search_phrases += description.upper().count(search_phrase.upper())

            # Contains money?
            contains_money = contains_monetary_value(title + description)

            # Store values
            row = {
                "Title": title,
                "Date": date_str,
                "Description": description,
                "Picture filename": picture_name,
                "Count of search phrases": count_search_phrases,
                "Title or description contains money?": contains_money
            }
            rows.append(row)

        # Randomically a shadow-root appears. Workaround solution to allow click on next page
        browser.scroll_element_into_view("//*[text()='Follow Us']")
        browser.click_link("//*[@class='search-results-module-next-page']/a")
    
    return rows


def save_data_on_excel(rows: list, search_phrase: str):

    excel_folder_path = os.path.join(output_folder_path, search_phrase)
    os.makedirs(name=excel_folder_path, exist_ok=True)

    filename = search_phrase + ".xlsx"
    excel_path = os.path.join(excel_folder_path, filename)

    excel = Files()
    excel.create_workbook(path=excel_path)
    excel.append_rows_to_worksheet(rows, header=True)
    excel.save_workbook()
    excel.close_workbook()


def contains_monetary_value(description: str) -> bool:

    monetary_patterns = [
        r'\$\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?',  # $11.1 or $111,111.11
        r'\b\d+ dollars\b',                     # 11 dollars
        r'\b\d+ USD\b'                          # 11 USD
    ]
    
    combined_pattern = '|'.join(monetary_patterns)
    
    match = re.search(combined_pattern, description, re.IGNORECASE)
    
    # True if monetary values found or False if not
    return match is not None