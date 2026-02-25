import os

from dotenv import load_dotenv

script_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(script_dir, "secrets.env"))
load_dotenv(os.path.join(script_dir, "setup.env"))

_REQUIRED = {
    "SYMBOL": str,
    "MAX_RATE": float,
    "MIN_RATE": float,
    "MIN_FOR_30D": float,
    "PERCENTAGE_FOR_WALL_LEVEL": int,
    "MAX_TOTAL_VALUE": int,
}

_missing = [k for k in _REQUIRED if os.getenv(k) is None]
if _missing:
    raise EnvironmentError(
        f"Missing required environment variables: {', '.join(_missing)}. "
        f"Check your secrets.env and setup.env files."
    )

SYMBOL: str = os.getenv("SYMBOL")

MAX_RATE: float = float(os.getenv("MAX_RATE"))
MIN_RATE: float = float(os.getenv("MIN_RATE"))
MIN_FOR_30D: float = float(os.getenv("MIN_FOR_30D"))

PERCENTAGE_FOR_WALL_LEVEL: int = int(os.getenv("PERCENTAGE_FOR_WALL_LEVEL"))
MAX_TOTAL_VALUE: int = int(os.getenv("MAX_TOTAL_VALUE"))
