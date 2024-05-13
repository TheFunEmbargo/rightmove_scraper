"""conftest automagic imports fixtures"""

import pytest
from pathlib import Path
import json


def load_json(path: str):
    with open(path, "r") as f:
        return json.load(f)


@pytest.fixture()
def scrape_search() -> dict:
    return load_json(Path.cwd() / "tests" / "data" / "scrape_search_response.json")


@pytest.fixture()
def scrape_urls() -> dict:
    return load_json(Path.cwd() / "tests" / "data" / "scrape_urls_response.json")
