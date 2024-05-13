from math import radians, cos, sin, asin, sqrt
from dataclasses import dataclass


@dataclass
class Point:
    """Reminder class to enforce lon, lat. Equally valid as list[float, float]"""

    longitude: float
    latitude: float

    def __iter__(self):
        yield self.longitude
        yield self.latitude

    def __getitem__(self, index):
        if index == 0:
            return self.longitude
        elif index == 1:
            return self.latitude
        else:
            raise IndexError("Index out of range")


def haversine(point1: Point, point2: Point) -> float:
    """Calculate the great circle distance in miles between two points on the earth (specified in decimal degrees)"""

    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [*point1, *point2])

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    # Radius of earth units determine return units
    # 3956 for miles
    # 6371 kilometers
    r = 6371
    return c * r
