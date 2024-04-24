""" @file customlogger.py
    @author Sean Duffie
    @brief Handles the formatting of Logger entries

    Custom logger that standardizes my logging process
"""
import logging
import sys


class LogFormatter(logging.Formatter):
    """ Creates a Custom Logger Formatter that allows colors to be sent to the terminal
    """
    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    fmt = "%(asctime)s | %(levelname)-8s | %(name)s.%(filename)-13s:%(lineno)-4d| %(message)s"

    FORMATS = {
        logging.DEBUG: grey + fmt + reset,
        logging.INFO: grey + fmt + reset,
        logging.WARNING: yellow + fmt + reset,
        logging.ERROR: red + fmt + reset,
        logging.CRITICAL: bold_red + fmt + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(
            fmt=log_fmt,
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        return formatter.format(record)

def format_logs(logger_name: str, file_name: str = None, level: int = logging.INFO):
    """ Generate a formatted custom logger object with colors.

    This logger can be called from anywhere in the stack using `logger = logging.getLogger()`

    Args:
        logger_name (str): Name of the logger to format
        file_name (str, optional): Filename to output the logs to. Defaults to None.
        level (int, optional): Level of detail to output. Defaults to logging.INFO.
    """
    logger = logging.getLogger(logger_name)

    # Configure the default terminal logger
    stdout_handler = logging.StreamHandler(stream=sys.stdout)
    stdout_handler.setFormatter(fmt=LogFormatter())
    logger.addHandler(stdout_handler)

    # Check that the level input is a valid option
    levels = [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL]
    if level not in levels:
        logging.error("Invalid logging level for custom logger")
        level = logging.INFO
    logger.setLevel(level)

    # Determine where to output the log file, if at all
    if file_name is not None:
        file_handler = logging.FileHandler(filename=file_name)
        logger.addHandler(file_handler)
