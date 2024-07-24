import traceback
import logging


class Logger:
    def __init__(self) -> None:
        self.filename=r'output/app.log' 
        self.format='%(asctime)s - %(levelname)s - %(message)s'

    def info(self, message: str) -> None:
        logging.basicConfig(
            filename=self.filename, 
            level=logging.INFO, 
            format=self.format
        )
        logging.info(message)    

    def error(self, message: str) -> None:
        logging.basicConfig(
            filename=self.filename, 
            level=logging.ERROR, 
            format=self.format
        )
        logging.error(message)
        logging.error(traceback.format_exc())
