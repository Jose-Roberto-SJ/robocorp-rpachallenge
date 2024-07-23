from RPA.Excel.Files import Files

from config import OUTPUT_FOLDER_PATH
from log import Logger
import os

logger = Logger()


def save_news_on_file(rows: list, search_phrase: str) -> None:

    logger.info(f"Saving news into Excel file.")
    
    excel_folder_path = os.path.join(OUTPUT_FOLDER_PATH, search_phrase)
    os.makedirs(name=excel_folder_path, exist_ok=True)

    filename = search_phrase + ".xlsx"
    excel_path = os.path.join(excel_folder_path, filename)

    excel = Files()
    excel.create_workbook(path=excel_path)
    excel.append_rows_to_worksheet(rows, header=True)
    excel.save_workbook()
    excel.close_workbook()
    