import os
from dotenv import load_dotenv

load_dotenv()

try:
    CITY_CENTRE = eval(os.getenv("CITY_CENTRE"))
    MAX_DISTANCE_FROM_CENTER_MILES = float(os.getenv("MAX_DISTANCE_FROM_CENTER_MILES"))
except Exception:
    raise EnvironmentError(
        "Please set valid values (see .env.example) for enviornment variables CITY_CENTRE, MAX_DISTANCE_FROM_CENTER_MILES"
    )
