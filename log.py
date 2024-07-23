import logging
import sys


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

    def error(self) -> None:
        logging.basicConfig(
            filename=self.filename, 
            level=logging.ERROR, 
            format=self.format
        )
        exc_type, exc_value, exc_traceback = sys.exc_info()
        def_name = exc_traceback.tb_frame.f_code.co_name
        error_line = exc_traceback.tb_lineno
        error_message = str(exc_value)
        message = f"Def: {def_name} - Line: {error_line} - Message: {error_message}"
        logging.error(message)
