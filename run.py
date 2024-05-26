from src.rightmove import RightMoveAPI
from src.utils import haversine, Point
from src.db import db
import src.config as config
from src.log import logger

log = logger.get(__name__)


def transform(properties):
    # calculate distance to center
    log.info("transforming")
    for property in properties:
        property_point = Point(
            property["location"]["longitude"], property["location"]["latitude"]
        )
        property["distanceToCityCenter"] = haversine(property_point, config.CITY_CENTRE)

    # filter those too far out
    properties = [
        p
        for p in properties
        if p["distanceToCityCenter"] < config.MAX_DISTANCE_FROM_CENTER_MILES
    ]

    # sort by price
    properties = sorted(properties, key=lambda p: p["price"]["amount"], reverse=False)
    return properties


def run():
    # extract
    location_id = "REGION^93829"
    right_move_api = RightMoveAPI()
    properties = right_move_api.scrape_search(location_id)

    properties = transform(properties)

    # load into database
    db.insert(properties)


if __name__ == "__main__":
    run()
