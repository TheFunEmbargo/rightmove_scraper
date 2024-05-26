import pytest
from src.rightmove import RightMoveAPI, Property


@pytest.mark.parametrize(
    "response_fixture, parse_map, photos_count",
    [("scrape_search", "search", 10), ("scrape_urls", "url", 3)],
)
def test_parser(response_fixture, parse_map, photos_count, request):
    """
    GIVEN a response from rightmove
    WHEN  json is parsed into a Property
    THEN  all photos are retrieved
    """
    data = request.getfixturevalue(response_fixture)[0]

    right_move_api = RightMoveAPI()
    property: Property = right_move_api._parse_property(
        data=data,
        parse_map=RightMoveAPI.parse_map[parse_map],
    )
    assert (
        len(property["photos"]) == photos_count
    ), """Parsed Property should have the correct number of photos"""
