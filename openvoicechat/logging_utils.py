import logging
import csv
import time
from datetime import datetime
import os
from typing import Dict, Any


def make_logger(log_dir: str = "logs", console_log: bool = False):
    log_dir = log_dir
    os.makedirs(log_dir, exist_ok=True)

    # Create timestamp for file names
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    print(timestamp)

    logger = logging.getLogger("OVC")
    logger.setLevel(logging.INFO)

    # File handler
    fh = logging.FileHandler(os.path.join(log_dir, f"ovc_{timestamp}.log"))
    fh.setLevel(logging.INFO)

    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    # Formatter
    # Time format: YYYY-MM-DD HH:MM:SS:mmm (e.g. 2024-11-07 04:08:55:383)
    formatter = logging.Formatter(
        "%(asctime)s,%(name)s,%(levelname)s,%(message)s,%(details)s,%(further)s",
    )
    formatter.default_msec_format = "%s.%03d"
    fh.setFormatter(
        formatter
    )  # weird hack to get milliseconds after a period instead of comma
    formatter = logging.Formatter(
        "%(asctime)s,%(name)s,%(levelname)s,%(message)s,%(details)s,%(further)s",
    )
    ch.setFormatter(formatter)

    logger.addHandler(fh)
    if console_log:
        logger.addHandler(ch)

    return logger


# Global logger instance
if __name__ == "__main__":
    logger = make_logger(console_log=True)

    logger.info("message", extra={"details": "hi", "further": "more"})
