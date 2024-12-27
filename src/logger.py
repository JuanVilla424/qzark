"""
logger.py
~~~~~~~~~

Provides a global logger for the Qzark-like application.
Logs to stdout with a consistent format.
"""

import logging
import sys


def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Configures and returns a logger with the specified name and level.
    The logger writes to stdout with a specific format and date format.

    Args:
        name (str): The name of the logger.
        level (int): The logging level (e.g., logging.INFO or logging.DEBUG).

    Returns:
        logging.Logger: The configured logger instance.
    """
    logger_instance = logging.getLogger(name)
    logger_instance.setLevel(level)

    if not logger_instance.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger_instance.addHandler(handler)

    logger_instance.propagate = False
    return logger_instance


#: Root logger for the entire Qzark-like system
logger = setup_logger("qzark", level=logging.DEBUG)
