import os
import sys
from statistics import mean

from config import PERCENTAGE_FOR_WALL_LEVEL, MAX_TOTAL_VALUE

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from UnofficialBitfinexGateway.bfxg import BitfinexClient


def get_frr(client: BitfinexClient, symbol: str):
    result = client.get_ticker_statistics(symbol)
    return result[0]


def get_wall(client: BitfinexClient, symbol: str):
    data = client.get_order_book(symbol)

    # find a wall
    # The wall is when next rate level include incredibly amount of money then previous level
    # 0.1 - 1234
    # 0.2 - 2345
    # 0.3 - 3456
    # 0.4 - 852963 <- Wall
    # 0.5 - 869999
    previous_level_amount = 0
    for i, row in enumerate(data):
        if i == 0:
            previous_level_amount = row[2]
            continue

        current_level_amount = row[2]
        # print(current_level_amount)

        if previous_level_amount * 100 / current_level_amount < PERCENTAGE_FOR_WALL_LEVEL and row[2] > MAX_TOTAL_VALUE:
            wall_level = row[0]
            return wall_level

        previous_level_amount = current_level_amount

    # if in some reason function is not able to set correct wall level, use FRR
    return get_frr(client=client, symbol=symbol)


def display_float_value(v: float) -> str:
    # v = round(v, 8)
    v = f"{v:.8f}"
    return v


def get_candles(client: BitfinexClient, symbol: str):
    result = client.get_candles(symbol, limit=5)

    print(result)

    result = get_average_max_rate(result)

    print(result)
    return result


def get_average_max_rate(data: list) -> float:
    temp = []
    for r in data:
        temp.append(r[3])

    return mean(temp)

