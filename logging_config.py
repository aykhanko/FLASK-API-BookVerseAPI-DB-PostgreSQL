import logging
import os
import json
from datetime import datetime

LOG_DIR = "Logs"
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "time": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "module": record.name,
            "message": record.getMessage()
        }
        return json.dumps(log_record)

def get_module_logger(module_file):
    module_name = os.path.splitext(os.path.basename(module_file))[0]
    log_path = os.path.join(LOG_DIR, f"{module_name}.log")

    logger = logging.getLogger(module_name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        file_handler = logging.FileHandler(log_path)
        file_handler.setFormatter(JsonFormatter())

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(LOG_FORMAT))
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        logger.propagate = False  

    return logger
