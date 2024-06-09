import os
import sys

sys.path.insert(0, '..')
from UnofficialBitfinexGateway.bfxg import BitfinexClient

from dotenv import load_dotenv
from pydantic import BaseModel
from pydantic import Field
from pydantic import field_validator
from statistics import mean
from datetime import datetime
from datetime import timedelta
from time import sleep

load_dotenv("secrets.env")

MAX_RATE = 0.001
MIN_RATE = 0.00020
MIN_FOR_30D = 0.00040


class HistoryFundingOrders(BaseModel):
    order_id: str
    symbol: str
    date_created: str
    date_updated: str
    amount: int
    amount_symbol: int
    _type: str
    # flags: object
    # none1: None
    # none2: None
    # none3: None
    flags: str
    # status: str
    # none4: None
    # none5: None
    # none6: None
    rate: float
    period: int

    @field_validator("date_created", "date_updated")
    def convert_timestamp(cls, t: str) -> datetime:
        # date_ = str(datetime.fromtimestamp(int(t)/1000))
        date_ = datetime.fromtimestamp(int(t)/1000)
        return date_


class ActiveFunding(BaseModel):
    order_id: int
    symbol: str
    date_created: str
    date_updated: str
    amount: float
    amount_symbol: float
    _type: str
    # flags: object
    # none1: None
    # none2: None
    # none3: None
    flags: str
    # status: str
    # none4: None
    # none5: None
    # none6: None
    rate: float
    period: int

    @field_validator("date_created", "date_updated")
    def convert_timestamp(cls, t: str) -> datetime:
        date_ = datetime.fromtimestamp(int(t)/1000)
        return date_


def get_average_max_rate(data: list) -> float:
    temp = []
    for r in data:
        temp.append(r[3])

    return mean(temp)


def get_candles(symbol):
    result = client.get_candles(symbol, limit=5)

    print(result)

    result = get_average_max_rate(result)

    print(result)
    return result


def display_float_value(v: float) -> str:
    # v = round(v, 8)
    v = f"{v:.8f}"
    return v


def get_frr(symbol):
    result = client.get_ticker_statistics(symbol)
    print(result)
    return result[0]


def set_best_rate_small_cascade(symbol, available_balance, cascade_levels):
    # mean_daily_high = get_candles(f"f{symbol}")
    mean_daily_high = float(get_frr(f"f{symbol}"))
    my_rate = mean_daily_high

    my_rate = get_wall(symbol)

    print(my_rate)

    if available_balance > cascade_levels*150:
        temp = available_balance // cascade_levels
        temp_zostatok = available_balance - ((cascade_levels-1)*temp)

        # if temp <= 150 or temp_zostatok <= 150:
        #     temp = 150

        print(temp)
        print(temp_zostatok)
        
        for i in range(cascade_levels-1):
            my_rate -= 0.00001

            print(mean_daily_high)
            print(my_rate)
            
            _type = "LIMIT"
            _symbol = f"f{symbol}"
            amount = temp
            rate = round(my_rate, 5)

            if rate >= MIN_FOR_30D:
                period = 30
            else:
                period = 2

            _rate = display_float_value(rate)

            # print(rate, type(rate))
            # print(_rate, type(_rate))
            resp = client.set_funding_order(_type, _symbol, str(amount), str(_rate), period, flags = 0)
            print(resp)
            
        my_rate += 0.00001
            
        _type = "LIMIT"
        _symbol = f"f{symbol}"
        amount = str(temp_zostatok)
        rate = round(my_rate, 5)

        # if rate > 0.00058:
        #     period = 30
        # else:
        #     period = 2

        period = 2

        _rate = display_float_value(rate)

        # print(rate, type(rate))
        # print(_rate, type(_rate))
        resp = client.set_funding_order(_type, _symbol, str(amount), str(_rate), period, flags = 0)
    else:
        set_best_rate(symbol, available_balance, my_rate)


def set_best_rate(symbol, available_balance, my_rate=None):
    # ticker_stat = client.get_ticker_statistics(f"f{symbol}")
    # daily_high = ticker_stat[11]
    # print(daily_high)
    # my_rate = daily_high

    if my_rate is None:
        mean_daily_high = get_candles(f"f{symbol}")
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

    # period = 2

    resp = client.set_funding_order(_type, _symbol, str(amount), str(rate), period, flags = 0)
    print(resp)


def create_cascade(symbol, available_balance):
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

        if rate > 0.00055:
            period = 30
        else:
            period = 2

        _rate = display_float_value(rate)

        # print(rate, type(rate))
        # print(_rate, type(_rate))
        resp = client.set_funding_order(_type, _symbol, str(amount), str(_rate), period, flags = 0)
        print(resp)

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

            resp = client.set_funding_order(_type, _symbol, str(amount), str(rate), period, flags = 0)
            print(resp)


    # my_rate = daily_high - 0.00002 # test, v skutocnosti by to mal byt -
    # # my_rate = daily_high + 0.00005 # test, v skutocnosti by to mal byt -

    # # my_rate = 0.0006

    # _type = "LIMIT"
    # symbol = "fUSD"
    # amount = available_ltc_balance
    # rate = round(my_rate, 6)
    # period = 2

    # print(amount)
    # print(type(amount))

    # resp = client.set_funding_order(_type, symbol, str(amount), str(rate), period, flags = 0)
    # print(resp)


def get_wall(symbol):
    data = client.get_order_book(symbol)
    final_rate = 0
    for row in data:
        actual_rate = row[0]
        if row[2] < 10000000:  # ten million
            final_rate = actual_rate


    # find a wall
    # wall is when next rate level include incredibly amount of money then previous level
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

        # print(previous_level_amount, current_level_amount)
        # d = previous_level_amount * 100 / current_level_amount
        # print(d)
        if previous_level_amount * 100 / current_level_amount < 10 and row[2] > 10000000:
            wall_level = row[0]
            break

        previous_level_amount = current_level_amount

    # print(wall_level)
    # print(previous_level_amount)

    return wall_level


api_key = os.getenv("API_KEY")
api_secret = os.getenv("API_SECRET")

client = BitfinexClient(key=api_key, secret=api_secret)

symbol = "USD"

if symbol == "USD":
    mim_amount = 150
elif symbol == "LTC":
    mim_amount = 2  # TODO: recalculate every time based on current price
else:
    mim_amount = "sting over int to crash..."  # todo: correct handle min_amounts per symbol - like calculate rate by actual price (?)

while True:

    while True:
        try:
            result = client.get_active_funding_orders(f"f{symbol}")
            break
        except ConnectionError as ce:
            print(f"{ce.__class__.__name__} - {str(ce)}")
            print("I will try send request again after 1 second.")
            sleep(1)

    for i, r in enumerate(result):
        print(r)
        row = ActiveFunding(order_id=r[0], symbol=r[1], date_created=str(r[2]), date_updated=str(r[3]), amount=r[4], amount_symbol=r[5], _type=r[6], flags=r[10], rate=r[14], period=r[15])
        print("{:<15}: {} {} {} {:<10} {} {}".format(row.order_id, row.date_created, row.date_updated, row.symbol, round(float(row.amount_symbol), 2), row.rate, row.period))

        now = datetime.today()
        # delta = timedelta(seconds=60)
        delta = timedelta(hours=4)
        frame = now - delta

        # print(row.date_created)
        # print(delta)
        # print(frame)

        if frame > row.date_created:
            client.set_cancel_funding_order(row.order_id)

    result = client.get_wallets()
    for r in result:
        # print(r)
        if r[0] == "funding" and r[1] == symbol:
            available_balance = float(r[4])

            now = datetime.now()
            t = now.strftime("%d-%m-%Y %H:%M:%S")
            print(f"{t}\tDostupný zostatok na účte je: {round(available_balance, 2)} {symbol}")

            if available_balance >= mim_amount:

                # create_cascade(symbol, available_balance)
                # set_best_rate(symbol, available_balance)
                set_best_rate_small_cascade(symbol, available_balance, cascade_levels=5)
                
    sleep(5*60) # every 5 minutes...
