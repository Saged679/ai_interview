"""
Logging configuration for the GitHub scraper.

Sets up a root logger with:
  - Console handler (INFO level) for live progress
  - File handler (DEBUG level) in `github_scraper.log` for full trace
"""

import logging
import os

LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logger(log_dir: str = ".", log_file: str = "github_scraper.log") -> logging.Logger:
    """
    Configure and return the package-level logger.

    Parameters
    ----------
    log_dir : str
        Directory where the log file will be created.
    log_file : str
        Name of the log file.

    Returns
    -------
    logging.Logger
        The configured root logger for the github_scraper package.
    """
    logger = logging.getLogger("github_scraper")

    # Avoid adding duplicate handlers if called multiple times
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    # ── Console handler (INFO) ──────────────────────────────────────────
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))
    logger.addHandler(console_handler)

    # ── File handler (DEBUG) ────────────────────────────────────────────
    log_path = os.path.join(log_dir, log_file)
    file_handler = logging.FileHandler(log_path, mode="a", encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))
    logger.addHandler(file_handler)

    logger.info("Logger initialised — console=INFO, file=DEBUG → %s", log_path)
    return logger
