import logging
from datetime import datetime
import os


def make_logger(
    log_dir: str = "logs",
    log_name: str = "ovc",
    log_id: str = "",
    console_log: bool = False,
):
    """
    Make a logger for the openvoicechat library.
    :param log_dir: The directory to save the logs to.
    :param log_name: The name of the log file.
    :param log_id: The id of the log file, if not provided, a timestamp will be used.
    :param console_log: Whether to log to the console.
    :return: A logger object.
    """
    log_dir = log_dir
    os.makedirs(log_dir, exist_ok=True)

    # Create timestamp for file names
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if log_id == "":
        log_id = timestamp

    logger = logging.getLogger(log_name)
    logger.setLevel(logging.INFO)

    # File handler
    fh = logging.FileHandler(os.path.join(log_dir, f"{log_name}_{log_id}.log"))
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
