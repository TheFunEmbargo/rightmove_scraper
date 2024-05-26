"""conftest automagic imports fixtures"""

import pytest
from pathlib import Path
import json

import os
import tempfile

from src.log import logger


def load_json(path: str):
    with open(path, "r") as f:
        return json.load(f)


@pytest.fixture()
def scrape_search() -> dict:
    return load_json(Path.cwd() / "tests" / "data" / "scrape_search_response.json")


@pytest.fixture()
def scrape_urls() -> dict:
    return load_json(Path.cwd() / "tests" / "data" / "scrape_urls_response.json")


@pytest.fixture
def temp_logger():
    # set up
    temp_dir = tempfile.mkdtemp()
    logger.log_file = os.path.join(temp_dir, "app.log")
    yield logger

    # clean up
    # close all file handlers to release the lock on the log file
    for logger_instance in logger._loggers.values():
        for handler in logger_instance.handlers:
            handler.close()
    os.remove(logger.log_file)
    os.rmdir(temp_dir)
