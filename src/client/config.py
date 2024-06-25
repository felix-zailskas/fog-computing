import os

from dotenv import load_dotenv

load_dotenv()

HOST = os.getenv("HOST")
PORT = int(os.getenv("PORT", 0))

GOAL_TEMP = float(os.getenv("GOAL_TEMP", 20.0))
STARTING_TEMP = float(os.getenv("STARTING_TEMP", 19.0))
AC_START_TEMP = float(os.getenv("AC_START_TEMP", 20.0))
INSIDE_FACTOR = float(os.getenv("INSIDE_FACTOR", 0.8))
OUTSIDE_FACTOR = float(os.getenv("OUTSIDE_FACTOR", 0.5))
SECONDS_PER_ROUND = int(os.getenv("SECONDS_PER_ROUND", 5))
