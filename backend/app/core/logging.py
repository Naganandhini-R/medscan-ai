import logging
import sys
from app.core.config import settings

def setup_logging():
    """
    Configure logging for the application.
    """
    logger = logging.getLogger()
    logger.setLevel(settings.LOG_LEVEL)

    # Console Handler
    c_handler = logging.StreamHandler(sys.stdout)
    c_format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    c_handler.setFormatter(c_format)
    logger.addHandler(c_handler)

    # File Handler (Optional, only if LOG_FILE is set or needed)
    # f_handler = logging.FileHandler('backend/logs/app.log')
    # f_handler.setFormatter(c_format)
    # logger.addHandler(f_handler)

    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)  # Reduce noise

    return logger

logger = setup_logging()
