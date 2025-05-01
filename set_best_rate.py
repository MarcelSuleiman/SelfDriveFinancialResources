import os
import sys
from datetime import datetime
from datetime import timedelta
from time import sleep
from typing import List, Any

from config import SYMBOL
from currencies import CURRENCIES
from input_parser import compose_input_parser
from services.active_funding_service import get_active_fundings
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
                        cascade_vertical_movement=args.cascade_vertical_movement,
                    )
                else:
                    print(
                        f"Available amount of funds: {available_balance} is not enough "
                        f"for {args.cascade_levels} levels. "
                        f"Minimal required amount is: {150 * int(args.cascade_levels)}"
                    )

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
    # TODO replace all prints by logger - to console & log file
    main()
