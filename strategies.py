import os
import sys

from config import MIN_FOR_30D
from config import MIN_RATE
from services.submitted_funding_service import generate_offer_object
from utils import display_float_value
from utils import get_candles
from utils import get_frr
from utils import get_wall

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from lib.UnofficialBitfinexGateway.bfxg import BitfinexClient


def set_best_rate_small_cascade(
        client: BitfinexClient,
        symbol: str,
        available_balance: float,
        cascade_levels: int,
        strategy: str,
        cs_step: str,
        cascade_vertical_movement: str,
):

    if strategy == "FRR":
        my_rate = get_frr(client=client, symbol=f"f{symbol}")

    else:
        my_rate = get_wall(client=client, symbol=f"f{symbol}")

    if available_balance > cascade_levels*150:
        temp = available_balance // cascade_levels
        temp_balance = available_balance - ((cascade_levels-1)*temp)

        for i in range(cascade_levels-1):
            # step is multiplied by 0.00001, so cs_step=1 => 0.00001, cs_step=3 => 0.00003
            if cascade_vertical_movement == "down":
                my_rate -= int(cs_step) * 0.00001
            elif cascade_vertical_movement == "up":
                my_rate += int(cs_step) * 0.00001
            else:
                raise ValueError(f"Vertical movement value {cascade_vertical_movement} is not valid.")

            _type = "LIMIT"
            _symbol = f"f{symbol}"
            amount = temp
            rate = round(my_rate, 5)

            if rate >= MIN_FOR_30D:
                period = 30
            else:
                period = 2

            _rate = display_float_value(rate)

            resp = client.set_funding_order(_type, _symbol, str(amount), str(_rate), period, flags=0)

            offer = generate_offer_object(resp)
            print(offer)

        # step is multiplied by 0.00001, so cs_step=1 => 0.00001, cs_step=3 => 0.00003
        if cascade_vertical_movement == "down":
            my_rate -= int(cs_step) * 0.00001
        elif cascade_vertical_movement == "up":
            my_rate += int(cs_step) * 0.00001

        _type = "LIMIT"
        _symbol = f"f{symbol}"
        amount = str(temp_balance)
        rate = round(my_rate, 5)

        period = 2

        _rate = display_float_value(rate)

        resp = client.set_funding_order(_type, _symbol, str(amount), str(_rate), period, flags=0)
        offer = generate_offer_object(resp)
        print(offer)
    else:
        set_best_rate(
            client=client,
            symbol=symbol,
            available_balance=available_balance,
            strategy=strategy,
            my_rate=my_rate,
        )


def set_best_rate(
        client: BitfinexClient,
        symbol: str,
        available_balance: float,
        strategy: str,
        my_rate=None,
):

    if strategy == "FRR":
        my_rate = get_frr(client=client, symbol=f"f{symbol}")

    elif strategy == "WALL":
        my_rate = get_wall(
            client=client,
            symbol=f"f{symbol}",
        )

    elif strategy == "mean_daily_high":
        mean_daily_high = get_candles(client=client, symbol=f"f{symbol}")
        my_rate = mean_daily_high

    else:
        raise ValueError(f"Unknown strategy: '{strategy}'")

    my_rate -= 0.00001

    _type = "LIMIT"
    _symbol = f"f{symbol}"
    amount = available_balance
    rate = round(my_rate, 5)

    if rate < MIN_RATE:
        rate = MIN_RATE

    if rate >= MIN_FOR_30D:
        period = 30
    else:
        period = 2

    resp = client.set_funding_order(_type, _symbol, str(amount), str(rate), period, flags=0)
    offer = generate_offer_object(resp)
    print(offer)
