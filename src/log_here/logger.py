import logging
from logging.handlers import RotatingFileHandler

class SafeFormatter(logging.Formatter):
    def format(self, record):
        if not hasattr(record, "student_id"):
            record.student_id = "N/A"
        return super().format(record)

logger = logging.getLogger("app_logger")
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = RotatingFileHandler(
        "app.log", maxBytes=5*1024*1024, backupCount=3
    )

    formatter = SafeFormatter(
        "%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - line:%(lineno)d - student_id=%(student_id)s - %(message)s"
    )

    handler.setFormatter(formatter)
    logger.addHandler(handler)