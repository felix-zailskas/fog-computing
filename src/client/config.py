import os

from dotenv import load_dotenv

load_dotenv()

HOST = os.getenv("HOST")
PORT = int(os.getenv("PORT", 0))

GOAL_TEMP = 21.0
STARTING_TEMP = 19.0
OUTSIDE_FACTOR = 0.5
INSIDE_FACTOR = 0.8

SECONDS_PER_ROUND = 5
