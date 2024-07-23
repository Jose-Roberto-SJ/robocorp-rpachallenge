from robocorp.tasks import task
from robocorp import workitems

from dateutil.relativedelta import relativedelta
from config import OUTPUT_FOLDER_PATH
from datetime import datetime as dt
from latimes import LosAngelesTimes
from log import Logger
import shutil
import excel
import os

lat = LosAngelesTimes()
logger = Logger()


@task
def extract_data_from_latimes():

    # 1. Open the site by following the link
    lat.open_browser()

    for item in workitems.inputs:
        try:
            search_phrase = item.payload["Search phrase"]
            topic = item.payload["Topic"]
            months_number = item.payload["Months number"]
            months_number = 0 if months_number <= 1 else (months_number - 1) * -1
            limit_dt = (dt.today() + relativedelta(months=months_number, day=1)).date()

            # 2. Enter a phrase in the search field
            # 3. On the result page, section from the Choose the latest (newest) news
            lat.search_and_order(search_phrase)

            # 3. On the result page, If possible, select a news category
            lat.filter_topic(topic)

            # 4. Get the values: title, date, and description.
            rows = lat.get_news(limit_dt, search_phrase)

            # 5. Store in an Excel file:
            excel.save_news_on_file(rows, search_phrase)

            # Create a zip file
            zip_name = os.path.join(OUTPUT_FOLDER_PATH, search_phrase)
            zip_path = shutil.make_archive(zip_name, 'zip', zip_name)

            # Upload zip file to control room
            item.add_file(zip_path)

            # Save item result
            item.save()
            item.done()
            logger.info(f"Finished searching for '{search_phrase}'.")

        except AssertionError as err:
            item.fail("BUSINESS", message=str(err))
            logger.error()
        except Exception as err:
            item.fail("APPLICATION", message=str(err))
            logger.error()
        finally:
            lat.close_browser()
