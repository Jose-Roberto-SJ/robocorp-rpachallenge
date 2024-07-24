from selenium.common.exceptions import StaleElementReferenceException
from RPA.Browser.Selenium import By, Selenium
from RPA.HTTP import HTTP

from config import LATIMES_URL, OUTPUT_FOLDER_PATH
from dateutil.relativedelta import relativedelta
from validations import contains_monetary_value
from datetime import datetime as dt
from log import Logger
import os

logger = Logger()


class LosAngelesTimes:

    def __init__(self) -> None:

        self.browser = Selenium()
        self.http = HTTP()

    def open_browser(self):
        
        logger.info("Opening browser.")
        try:
            self.browser.open_chrome_browser(
                url=LATIMES_URL,
                maximized=True,
                headless=False
            )
            self.browser.set_selenium_timeout = 20
        except:
            error_msg = "Failed to open browser."
            logger.error(error_msg)
            raise Exception(error_msg)

    def search_and_order(self, search_phrase: str) -> None:

        logger.info(f"Searching for '{search_phrase}' and sorting by newest news.")
        self.browser.go_to(f"{LATIMES_URL}search?q={search_phrase}&s=1")
        if self.browser.does_page_contain_element("//*[@class='search-results-module-no-results']"):
            raise AssertionError(f"There are not any results that match '{search_phrase}'")

    def filter_topic(self, topic: str) -> None:

        logger.info(f"Filtering by topic '{topic}.'")
        try:
            if self.browser.does_page_contain_element(f"//*[*[text()='Topics']]//*[contains(text(),'{topic}')]"):
                pages_str = self.browser.get_text("//*[@class='search-results-module-page-counts']")
                self.browser.select_checkbox(f"//*[*[text()='Topics']]//*[*[contains(text(),'{topic}')]]/input")
                self.browser.click_element("//*[@class='button submit-button']")
                self.browser.wait_until_element_is_not_visible(f"//*[contains(text(),'{pages_str}')]", 20)
            self.browser.wait_until_element_is_visible("//*[@class='search-results-module-page-counts']", timeout=20)
        except StaleElementReferenceException:
            error_msg = "Failed to filter by '{topic}."
            logger.error(error_msg)
            raise Exception(error_msg)

    def get_news(self, limit_dt: dt.date, search_phrase: str) -> list:
        
        logger.info(f"Capturing news.")
        pictures_folder_path = os.path.join(OUTPUT_FOLDER_PATH, search_phrase, "Pictures")
        os.makedirs(name=OUTPUT_FOLDER_PATH, exist_ok=True)

        try:       
            pages_str = self.browser.get_text("//*[@class='search-results-module-page-counts']")
            pages_nr = int(pages_str.split(" of ")[1].replace(",", ""))
            rows = []
            for p in range(pages_nr):
                elements = self.browser.get_webelements("//*[@class='promo-wrapper']")
                for l, li in enumerate(elements):
                    # Date
                    date_str = li.find_element(By.CLASS_NAME, 'promo-timestamp').text
                    if "ago" in date_str:
                        date_dt = dt.today().date() + relativedelta(day=1)
                    else:
                        date_dt = dt.strptime(date_str, "%B %d, %Y").date() + relativedelta(day=1)

                    if date_dt < limit_dt:
                        return rows

                    # Title
                    title = li.find_element(By.CLASS_NAME, "promo-title").text

                    # Description
                    description = li.find_element(By.CLASS_NAME, "promo-description").text

                    # Picture download
                    picture_name = f"picture_{p}.{l}.png"
                    picture_path = os.path.join(pictures_folder_path, picture_name)  
                    url = li.find_element(By.CLASS_NAME, "image").get_attribute("src")
                    self.http.download(url=url, target_file=picture_path, overwrite=True)

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
                self.browser.scroll_element_into_view("//*[text()='Follow Us']")
                self.browser.click_link("//*[@class='search-results-module-next-page']/a")

        except StaleElementReferenceException:
            error_msg = "Failed to capture news."
            logger.error(error_msg)
            raise Exception(error_msg)
        
        return rows

    def close_browser(self):
        if self.browser:        
            logger.info("Closing browser.")
            self.browser.close_browser()
