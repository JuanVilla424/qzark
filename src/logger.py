"""
logger.py
~~~~~~~~~

Provides a global logger for the Qzark-like application.
Logs to both stdout and a file with a consistent format.
"""

import logging
import sys
from typing import Optional


def setup_logger(
    name: str, level: int = logging.INFO, log_file: Optional[str] = None
) -> logging.Logger:
    """
    Configures and returns a logger with the specified name and level.
    The logger writes to stdout with a specific format and date format,
    and optionally logs to a specified file.

    Args:
        name (str): The name of the logger.
        level (int, optional): The logging level (e.g., logging.INFO or logging.DEBUG).
            Defaults to logging.INFO.
        log_file (Optional[str], optional): The path to a file where logs should
            also be written. If None, no file logs are created.

    Returns:
        logging.Logger: The configured logger instance.
    """
    logger_instance = logging.getLogger(name)
    logger_instance.setLevel(level)

    # Only configure handlers if none exist yet
    if not logger_instance.handlers:
        # 1. StreamHandler for stdout
        stream_handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        stream_handler.setFormatter(formatter)
        logger_instance.addHandler(stream_handler)

        # 2. Optional FileHandler
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            # You could set a different level here if desired
            # file_handler.setLevel(logging.WARNING)
            logger_instance.addHandler(file_handler)

    logger_instance.propagate = False
    return logger_instance


# Root logger for the entire Qzark-like system
# You can specify a log file if you want, e.g. `log_file="qzark.log"`.
logger = setup_logger("qzark", level=logging.DEBUG, log_file="logs/qzark.log")
