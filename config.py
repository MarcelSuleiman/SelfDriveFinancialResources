import os

from dotenv import load_dotenv

script_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(script_dir, "secrets.env"))
load_dotenv(os.path.join(script_dir, "setup.env"))

SYMBOL = os.getenv("SYMBOL")

MAX_RATE = float(os.getenv("MAX_RATE"))
MIN_RATE = float(os.getenv("MIN_RATE"))
MIN_FOR_30D = float(os.getenv("MIN_FOR_30D"))

PERCENTAGE_FOR_WALL_LEVEL = int(os.getenv("PERCENTAGE_FOR_WALL_LEVEL"))
MAX_TOTAL_VALUE = int(os.getenv("MAX_TOTAL_VALUE"))
