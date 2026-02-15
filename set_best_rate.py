import calendar
import logging
import os
import sys
from datetime import datetime
from datetime import timedelta
from pathlib import Path
from time import sleep
from typing import List, Any

from config import SYMBOL
from currencies import CURRENCIES
from input_parser import compose_input_parser
from logger import setup_logger
from services.active_funding_service import get_active_fundings
from services.funding_credit_history_service import get_fundings_credit_history
from services.ticker_object import generate_ticker_object
from strategies import set_best_rate_small_cascade, set_best_rate
from utils import get_cascade_level, get_unix_time

# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# from UnofficialBitfinexGateway.bfxg import BitfinexClient

from lib.UnofficialBitfinexGateway.bfxg import BitfinexClient


def check_amount_of_funds(available_balance: float, cascade_levels: int) -> bool:
    if available_balance > cascade_levels * 150:
        return True
    return False


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


def main(logger):
    api_key, api_secret = get_credentials()
    client = BitfinexClient(key=api_key, secret=api_secret)
    args = compose_input_parser()

    min_amount = get_min_amount(client=client)
    submitted_orders = client.get_submitted_funding_orders(f"f{SYMBOL}")  # actual running fundings
    submitted_orders = client.get_submitted_funding_orders_history(f"f{SYMBOL}")  # history running fundings
    submitted_orders = get_fundings_credit_history(submitted_orders)
    # submitted_orders = client.history_funding_orders(f"f{SYMBOL}")
    for so in submitted_orders:
        print(so)


    # summary max for last 30 days
    # summary_info = client.get_earning_summary()
    # for si in summary_info:
    #     print(si)

    today = datetime.today()

    # Prvý deň aktuálneho mesiaca o 00:00:00
    start_date = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # Posledný deň aktuálneho mesiaca o 23:59:59
    last_day = calendar.monthrange(today.year, today.month)[1]
    end_date = today.replace(day=last_day, hour=23, minute=59, second=59, microsecond=0)

    # start = get_unix_time(date="01-06-2025")
    start = get_unix_time(date=start_date.strftime("%d-%m-%Y"))
    # end = get_unix_time(date="30-06-2025")
    end = get_unix_time(date=end_date.strftime("%d-%m-%Y"))
    payload = {
        'category': 28,  # interest payment
        'limit': 750,  # must be otherwise default 25 will be applied
        'start': start,
        'end': end,
    }
    ledgers = client.get_ledgers("USD", **payload)
    total_sum = 0
    for i, l in enumerate(ledgers):
        total_sum += l[5]
        print(i, l)

    start = datetime.fromtimestamp(int(start) / 1000)
    end = datetime.fromtimestamp(int(end) / 1000)
    print(f"From {start} to {end} customer earns: {round(total_sum, 2)}$.")

    # exit(5)

    # led = client.ledgers(currency="USD", **{'limit': 2})
    # for l in led:
    #     print(l)

    while True:
        list_active_funding_orders = get_active_fundings(get_active_funding_orders(client=client))

        if len(list_active_funding_orders) > 0:
            # print("Currently active funding(s):")
            for row in list_active_funding_orders:
                # print(row)
                now = datetime.today()
                delta = timedelta(hours=4)
                frame = now - delta

                if frame > row.date_created:
                    client.set_cancel_funding_order(row.id)

        wallets = client.get_wallets()
        available_balance = get_available_balance_from_proper_wallet(wallets=wallets, symbol=SYMBOL)
        # available_balance = 10000
        t = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        # print(f"{t}\tThe available balance on the account is: {round(available_balance, 2)} {SYMBOL}")
        logger.info(f"{t}\tThe available balance on the account is: {round(available_balance, 2)} {SYMBOL}")

        if available_balance is not None and available_balance >= min_amount:

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
                        cascade_vertical_movement=args.cascade_vertical_movement,
                    )
                else:
                    # print(
                    #     f"Available amount of funds: {available_balance} is not enough "
                    #     f"for {args.cascade_levels} levels. "
                    #     f"Minimal required amount is: {150 * int(args.cascade_levels)}"
                    # )
                    logger.info(
                        f"Available amount of funds: {available_balance} is not enough "
                        f"for {args.cascade_levels} levels. "
                        f"Minimal required amount is: {150 * int(args.cascade_levels)}"
                    )
                    # TODO: add decreasing cascade levels to fit minimal requirements
                    # args.strategy = "single"
                    cs = get_cascade_level(available_balance=available_balance)
                    set_best_rate_small_cascade(
                        client=client,
                        symbol=SYMBOL,
                        available_balance=available_balance,
                        cascade_levels=int(cs),
                        strategy=args.funding_book_strategy,
                        cs_step=args.cascade_steps,
                        cascade_vertical_movement=args.cascade_vertical_movement,
                    )

            if args.strategy == "single":
                set_best_rate(
                    client=client,
                    symbol=SYMBOL,
                    available_balance=available_balance,
                    strategy=args.funding_book_strategy,
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
    logger = setup_logger(
        name="MyApp",
        log_file=str(Path(__file__).resolve().parent / "app.log"),
        level=logging.DEBUG,
        max_bytes=1024 * 1024 * 5,  # 5 MB
        backup_count=5
    )
    # TODO replace all prints by logger - to console & log file
    main(logger=logger)
