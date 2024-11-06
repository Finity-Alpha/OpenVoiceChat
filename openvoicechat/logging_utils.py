import logging
import csv
import time
from datetime import datetime
import os
from typing import Dict, Any


class OVCLogger:
    def __init__(self, log_dir: str = "logs", console_log: bool = False):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)

        # Create timestamp for file names
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        self.logger = logging.getLogger("OVC")
        self.logger.setLevel(logging.INFO)

        # File handler
        fh = logging.FileHandler(os.path.join(log_dir, f"ovc_{timestamp}.log"))
        fh.setLevel(logging.INFO)

        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)

        # Formatter
        formatter = logging.Formatter(
            "%(asctime)s,%(name)s,%(levelname)s,%(message)s,%(details)s"
        )
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        self.logger.addHandler(fh)
        if console_log:
            self.logger.addHandler(ch)


# Global logger instance
if __name__ == "__main__":
    logger = OVCLogger()
    logger.logger.info("message", extra={"details": "hi"})
