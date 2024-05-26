import logging
import os
import sys
from logging.handlers import RotatingFileHandler


class Logger:
    """Global logger factory

    Usage:
        from src.log import logger

        log = logger.get(__name__)
    """

    log_folder = "log"

    def __init__(
        self, log_file: str = "rightmove_scraper.log", level: int = logging.DEBUG
    ):
        self.log_file = self._init_log_file(log_file)
        self.level = level
        self._loggers = {}

    def _init_log_file(self, log_file: str):
        """logs live in a log folder"""
        log_dir = os.path.join(os.getcwd(), self.log_folder)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        return os.path.join(self.log_folder, log_file)

    def _setup_logger(self, name: str):
        """setup logger configuration, currently logs to both stdout and a file"""
        logger = logging.getLogger(name)
        logger.setLevel(self.level)

        # if the logger has handlers, do not duplicate them
        if not logger.handlers:
            # handlers
            console_handler = logging.StreamHandler(sys.stdout)
            file_handler = RotatingFileHandler(
                self.log_file, maxBytes=1024 * 1024 * 5, backupCount=5
            )

            # format handlers
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            console_handler.setFormatter(formatter)
            file_handler.setFormatter(formatter)

            # add handlers to the logger
            logger.addHandler(console_handler)
            logger.addHandler(file_handler)

        return logger

    def get(self, module_name: str):
        """get a module specific logger"""
        if module_name not in self._loggers:
            self._loggers[module_name] = self._setup_logger(module_name)
        return self._loggers[module_name]


logger = Logger()
