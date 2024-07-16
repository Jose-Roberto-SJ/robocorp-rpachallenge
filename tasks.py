from robocorp.tasks import task
from RPA.Browser.Selenium import Selenium, By

browser = Selenium()
search_phrase = 'Trump'
topic = 'California'

@task
def extracting_data_from_latimes():
    """
    Extracte data from 'Los Angeles Times'
    """
    try:
        browser.open_chrome_browser(f"https://www.latimes.com/search?q={search_phrase}")
        browser.maximize_browser_window()
        browser.set_selenium_timeout = 15
        browser.wait_until_page_contains_element(f"//*[text()='Topics']", timeout=20)
        if browser.does_page_contain_element(f"//*[*[text()='Topics']]//*[contains(text(),'{topic}')]"):
            browser.select_checkbox(f"//*[*[text()='Topics']]//*[*[contains(text(),'{topic}')]]/input")
            browser.click_element("//*[@class='button submit-button']")
        browser.wait_until_page_contains_element("//*[@class='search-results-module-page-counts']", timeout=20)
        page_ammount = browser.get_text("//*[@class='search-results-module-page-counts']")
        num_pages = int(str(page_ammount).split(" of ")[1].replace(",", "")) + 1
        for p in range(1, num_pages):
            for l in range(1, 10):
                xpath = f"//*[@class='search-results-module-results-menu']/li[{l}]"
                title = browser.get_text(xpath + "//*//h3//*[@class='link']")
                date = browser.get_text(xpath + "//*[@class='promo-description']")
                description = browser.get_text(xpath + "//*[@class='promo-timestamp']")
                print(title + '\n' + description + '\n' + date)
            browser.click_element("//*[@class='search-results-module-next-page']")

    finally:
        # Place for teardown and cleanups
        # Playwright handles browser closing
        print('Done')