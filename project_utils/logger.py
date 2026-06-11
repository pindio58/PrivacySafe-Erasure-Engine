import logging
import os
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


def _get_log_dir() -> Path:

    root = Path(__file__).resolve().parent.parent
    return root / "logs"


def get_logger(name: str):
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    logger.propagate = False

    log_dir = _get_log_dir()
    log_dir.mkdir(parents=True, exist_ok=True)

    curr_time = datetime.now(ZoneInfo("Asia/Kolkata")).strftime("%Y%m%d%H%M%S%f")[:-5]
    log_file = log_dir / f"logs-{curr_time}.log"

    file_handler = logging.FileHandler(log_file, delay=True)
    file_handler.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(funcName)s | %(message)s"
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    # logger.addHandler(console_handler)

    return logger
