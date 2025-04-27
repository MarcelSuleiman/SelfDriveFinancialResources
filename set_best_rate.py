import os
import sys
from datetime import datetime
from datetime import timedelta
from time import sleep
from typing import List, Any

from dotenv import load_dotenv
from statistics import mean

from currencies import CURRENCIES
from input_parser import compose_input_parser
from models import ActiveFunding
from models import FundingOfferArray
from models import TickerFunding
from models import TickerTrading
from models import SubmittedFundingOffer
from services.active_funding_service import get_active_fundings

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from UnofficialBitfinexGateway.bfxg import BitfinexClient


script_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(script_dir, "secrets.env"))
load_dotenv(os.path.join(script_dir, "setup.env"))

# load_dotenv("secrets.env")
# load_dotenv("setup.env")

SYMBOL = os.getenv("SYMBOL")

MAX_RATE = float(os.getenv("MAX_RATE"))
MIN_RATE = float(os.getenv("MIN_RATE"))
MIN_FOR_30D = float(os.getenv("MIN_FOR_30D"))

PERCENTAGE_FOR_WALL_LEVEL = int(os.getenv("PERCENTAGE_FOR_WALL_LEVEL"))
MAX_TOTAL_VALUE = int(os.getenv("MAX_TOTAL_VALUE"))


def generate_offer_object(resp: list[str]) -> SubmittedFundingOffer:
    offer = SubmittedFundingOffer(
        mst=resp[0],
        type_=resp[1],
        msg_id=resp[2],
        none1=resp[3],
        funding_offer_array=FundingOfferArray(
            id_=resp[4][0],
            symbol=resp[4][1],
            mts_created=resp[4][2],
            mts_updated=resp[4][3],
            amount=resp[4][4],
            amount_original=resp[4][5],
            offer_type=resp[4][6],
            none1=resp[4][7],
            none2=resp[4][8],
            flags=resp[4][9],
            offer_status=resp[4][10],
            none3=resp[4][11],
            none4=resp[4][12],
            none5=resp[4][13],
            rate=resp[4][14],
            period=resp[4][15],
            notify=resp[4][16],
            hidden=resp[4][17],
            none6=resp[4][18],
            renew=resp[4][19]
        ),
        code=resp[5],
        status=resp[6],
        text=resp[7]
    )

    return offer


def get_average_max_rate(data: list) -> float:
    temp = []
    for r in data:
        temp.append(r[3])

    return mean(temp)


def get_candles(client: BitfinexClient, symbol: str):
    result = client.get_candles(symbol, limit=5)

    print(result)

    result = get_average_max_rate(result)

    print(result)
    return result


def display_float_value(v: float) -> str:
    # v = round(v, 8)
    v = f"{v:.8f}"
    return v


def get_frr(client: BitfinexClient, symbol: str):
    result = client.get_ticker_statistics(symbol)
    return result[0]


def check_amount_of_funds(available_balance: float, cascade_levels: int) -> bool:
    if available_balance > cascade_levels * 150:
        return True
    return False


def set_best_rate_small_cascade(
        client: BitfinexClient,
        symbol: str,
        available_balance: float,
        cascade_levels: int,
        strategy: str,
        cs_step: str,
        cascade_vertical_movement: str
):

    if strategy == "FRR":
        my_rate = get_frr(client=client, symbol=f"f{symbol}")

    else:
        my_rate = get_wall(client=client, symbol=f"f{symbol}")

    if available_balance > cascade_levels*150:
        temp = available_balance // cascade_levels
        temp_balance = available_balance - ((cascade_levels-1)*temp)

        for i in range(cascade_levels-1):
            # mean if step is 1 => 0.00001, if 3 -> 0.00003 etc
            if cascade_vertical_movement == "down":
                my_rate -= float("0.0000"+cs_step)
            elif cascade_vertical_movement == "up":
                my_rate += float("0.0000" + cs_step)
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

        # mean if step is 1 => 0.00001, if 3 -> 0.00003 etc
        if cascade_vertical_movement == "down":
            my_rate -= float("0.0000" + cs_step)
        elif cascade_vertical_movement == "up":
            my_rate += float("0.0000" + cs_step)

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
        set_best_rate(client=client, symbol=symbol, available_balance=available_balance, strategy=strategy, my_rate=my_rate)


def set_best_rate(client: BitfinexClient, symbol: str, available_balance: float, strategy: str, my_rate=None):

    # my_rate = get_frr(f"f{symbol}")
    if strategy == "FRR":
        my_rate = get_frr(client=client, symbol=f"f{symbol}")

    if strategy == "WALL":
        my_rate = get_wall(client=client, symbol=f"f{symbol}")

    if strategy == "mean_daily_high":
        mean_daily_high = get_candles(client=client, symbol=f"f{symbol}")
        my_rate = mean_daily_high

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


def create_cascade(client: BitfinexClient, symbol: str, available_balance: float):
    temp = available_balance // 150
    no_offers = temp - 1 # chcem vyuzit vsetky peniaze preto posledna caskada bude full
    print(temp)
    print(no_offers)

    mean_daily_high = get_candles(f"f{symbol}")

    # my_rate = daily_high
    my_rate = mean_daily_high

    for i in range(int(no_offers)):
        my_rate -= 0.00001

        if my_rate < MIN_RATE:
            my_rate = MIN_RATE

        _type = "LIMIT"
        _symbol = f"f{symbol}"
        amount = "150"
        rate = round(my_rate, 5)

        if rate > MIN_FOR_30D:
            period = 30
        else:
            period = 2

        _rate = display_float_value(rate)

        resp = client.set_funding_order(_type, _symbol, str(amount), str(_rate), period, flags=0)
        offer = generate_offer_object(resp)
        print(offer)

    result = client.get_wallets()
    for r in result:
        if r[0] == "funding" and r[1] == symbol:
            available_balance = float(r[4])
            my_rate -= 0.00001

            _type = "LIMIT"
            _symbol = f"f{symbol}"
            amount = available_balance
            rate = round(my_rate, 5)

            if my_rate > 0.00055:
                period = 30
            else:
                period = 2

            resp = client.set_funding_order(_type, _symbol, str(amount), str(rate), period, flags=0)
            offer = generate_offer_object(resp)
            print(offer)


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
        print(current_level_amount)

        if previous_level_amount * 100 / current_level_amount < PERCENTAGE_FOR_WALL_LEVEL and row[2] > MAX_TOTAL_VALUE:
            wall_level = row[0]
            return wall_level

        previous_level_amount = current_level_amount

    # if in some reason function is not able to set correct wall level, use FRR
    return get_frr(client=client, symbol=symbol)


def generate_ticker_object(data, type_):
    if type_ == "t":
        ticker = TickerTrading(
            bid=data[0],
            bid_size=data[1],
            ask=data[2],
            ask_size=data[3],
            daily_change=data[4],
            daily_change_relative=data[5],
            last_price=data[6],
            volume=data[7],
            high=data[8],
            low=data[9],
        )
        return ticker

    if type_ == "f":
        ticker = TickerFunding(
            frr=data[0],
            bid=data[1],
            bid_period=data[2],
            bid_size=data[3],
            ask=data[4],
            ask_period=data[5],
            ask_size=data[6],
            daily_change=data[7],
            daily_change_perc=data[8],
            last_price=data[9],
            volume=data[10],
            high=data[11],
            low=data[12],
            none1=data[13],
            none2=data[14],
            frr_amount_available=data[15]
        )
        return ticker

    return TypeError(f"Asked type: '{type_}' is not valid. Choose 't' as trading or 'f' as funding")


def get_credentials():
    api_key = os.getenv("API_KEY")
    api_secret = os.getenv("API_SECRET")
    return api_key, api_secret


def get_min_amount(client: BitfinexClient) -> int:
    if SYMBOL in CURRENCIES:
        mim_amount = 150
    else:
        type_ = "t"
        data = client.get_ticker(symbol=SYMBOL, type_=type_)
        ticker = generate_ticker_object(data=data, type_=type_)
        mim_amount = 150 / ticker.last_price

    return mim_amount


def get_active_funding_orders(client: BitfinexClient) -> dict or str:
    while True:
        try:
            active_funding_orders = client.get_active_funding_orders(f"f{SYMBOL}")
            return active_funding_orders
        except ConnectionError as ce:
            print(f"{ce.__class__.__name__} - {str(ce)}")
            print("I will try send request again after 1 second.")
            sleep(1)


def get_available_balance_from_proper_wallet(wallets: List[List[Any]], symbol: str) -> float or None:
    for wallet in wallets:
        if wallet[0] == "funding" and wallet[1] == symbol:
            available_balance = float(wallet[4])
            return available_balance

    return None


def main():
    api_key, api_secret = get_credentials()
    client = BitfinexClient(key=api_key, secret=api_secret)
    args = compose_input_parser()

    mim_amount = get_min_amount(client=client)

    while True:
        active_funding_orders = get_active_funding_orders(client=client)
        list_active_funding_orders = get_active_fundings(active_funding_orders)

        if len(list_active_funding_orders) > 0:
            print("Currently active funding(s):")
            for row in list_active_funding_orders:
                print(row)
                now = datetime.today()
                delta = timedelta(hours=4)
                frame = now - delta

                if frame > row.date_created:
                    client.set_cancel_funding_order(row.id)

        wallets = client.get_wallets()
        available_balance = get_available_balance_from_proper_wallet(wallets=wallets, symbol=SYMBOL)
        t = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        print(f"{t}\tThe available balance on the account is: {round(available_balance, 2)} {SYMBOL}")

        if available_balance is not None and available_balance >= mim_amount:

            if args.strategy == "cascade":
                valid_amount = check_amount_of_funds(available_balance, int(args.cascade_levels))
                if valid_amount:
                    set_best_rate_small_cascade(
                        client=client,
                        symbol=SYMBOL,
                        available_balance=available_balance,
                        cascade_levels=int(args.cascade_levels),
                        strategy=args.funding_book_strategy,
                        cs_step=args.cascade_steps,
                        cascade_vertical_movement=args.cascade_vertical_movement
                    )
                else:
                    print(
                        f"Available amount of funds: {available_balance} is not enough "
                        f"for {args.cascade_levels} levels. "
                        f"Minimal required amount is: {150 * int(args.cascade_levels)}"
                    )
                    # TODO: add decreasing cascade levels to fit minimal requirements
                    args.strategy = "single"

            if args.strategy == "single":
                set_best_rate(
                    client=client,
                    symbol=SYMBOL,
                    available_balance=available_balance,
                    strategy=args.funding_book_strategy
                )

        if available_balance is None:
            print(
                f"No {SYMBOL} wallet found"
            )
            sys.exit(1)

        if args.daemon == "1":
            sleep(5 * 60)  # every 5 minutes...
        else:
            # Býva sa tu dobre, ale žiť sa tu nedá. Source: https://www.instagram.com/p/C6N9ppiAaRm/
            sys.exit(0)


if __name__ == "__main__":
    main()
