import os
from dotenv import load_dotenv

load_dotenv()

CITY_CENTRE = os.getenv("CITY_CENTRE")
MAX_DISTANCE_FROM_CENTER_MILES = os.getenv("MAX_DISTANCE_FROM_CENTER_MILES")
