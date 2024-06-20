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
load_dotenv("setup.env")

SYMBOL = os.getenv("SYMBOL")

MAX_RATE = float(os.getenv("MAX_RATE"))
MIN_RATE = float(os.getenv("MIN_RATE"))
MIN_FOR_30D = float(os.getenv("MIN_FOR_30D"))

PERCENTAGE_FOR_WALL_LEVEL = int(os.getenv("PERCENTAGE_FOR_WALL_LEVEL"))
MAX_TOTAL_VALUE = int(os.getenv("MAX_TOTAL_VALUE"))


class FundingOfferArray(BaseModel):
    id_: int
    symbol: str
    mts_created: str
    mts_updated: str
    amount: float
    amount_original: float
    offer_type: str
    none1: None = None
    none2: None = None
    flags: int
    offer_status: str
    none3: None = None
    none4: None = None
    none5: None = None
    rate: float
    period: int
    notify: bool
    hidden: int
    none6: None = None
    renew: bool

    def __str__(self):
        line = "{:<15}: {} {} {}".format(self.mts_created, self.symbol, self.amount, self.amount_original)
        return line

    @field_validator("mts_created", "mts_updated", mode="before")
    def convert_timestamp(cls, t: int) -> str:
        # date_ = str(datetime.fromtimestamp(int(t)/1000))
        date_ = datetime.fromtimestamp(t / 1000).strftime("%Y-%m-%d %H:%M:%S")
        return date_


class SubmittedFundingOffer(BaseModel):
    mst: str
    type_: str
    msg_id: int | None
    none1: None = None
    funding_offer_array: FundingOfferArray | None = None
    code: int | None
    status: str
    text: str

    def __str__(self):
        line = "{:<15}: {}".format(self.mst, self.text)
        return line

    @field_validator("mst", mode="before")
    def convert_mst(cls, t: int) -> str:
        date_ = datetime.fromtimestamp(t / 1000).strftime("%Y-%m-%d %H:%M:%S")
        return date_

    @field_validator("msg_id", "code", mode="before")
    def convert_str_to_int(cls, value):
        if value is not None:
            v = int(value)
            return v
        return None


class HistoryFundingOrders(BaseModel):
    order_id: str
    symbol: str
    date_created: str
    date_updated: str
    amount: int
    amount_symbol: int
    _type: str
    # flags: object
    none1: None = None
    none2: None = None
    none3: None = None
    flags: str
    status: str
    none4: None = None
    none5: None = None
    none6: None = None
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
    date_created: datetime
    date_updated: datetime
    amount: float
    amount_symbol: float
    _type: str
    flags: object
    none1: None = None
    none2: None = None
    none3: None = None
    flags: str
    status: str
    none4: None = None
    none5: None = None
    none6: None = None
    rate: float
    period: int

    def __str__(self):
        line = "{:<15}: {} {} {:<10} {} {}".format(
            self.order_id,
            self.date_created,
            self.symbol,
            self.amount_symbol,
            self.rate,
            self.period
        )

        return line

    @field_validator("date_created", "date_updated", mode="before")
    def convert_timestamp(cls, t: str) -> datetime:
        if isinstance(t, datetime):
            return t
        else:
            date_ = datetime.fromtimestamp(int(t)/1000)
            return date_


def generate_offer_object(resp):
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
    return result[0]


def set_best_rate_small_cascade(symbol, available_balance, cascade_levels):
    my_rate = get_wall(f"f{symbol}")

    if available_balance > cascade_levels*150:
        temp = available_balance // cascade_levels
        temp_balance = available_balance - ((cascade_levels-1)*temp)
        
        for i in range(cascade_levels-1):
            my_rate -= 0.00001
            
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

        my_rate -= 0.00001
            
        _type = "LIMIT"
        _symbol = f"f{symbol}"
        amount = str(temp_balance)
        rate = round(my_rate, 5)

        period = 2

        _rate = display_float_value(rate)

        resp = client.set_funding_order(_type, _symbol, str(amount), str(_rate), period, flags = 0)
        offer = generate_offer_object(resp)
        print(offer)
    else:
        set_best_rate(symbol, available_balance, my_rate)


def set_best_rate(symbol, available_balance, my_rate=None):

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

    resp = client.set_funding_order(_type, _symbol, str(amount), str(rate), period, flags = 0)
    offer = generate_offer_object(resp)
    print(offer)


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

        resp = client.set_funding_order(_type, _symbol, str(amount), str(_rate), period, flags = 0)
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

            resp = client.set_funding_order(_type, _symbol, str(amount), str(rate), period, flags = 0)
            offer = generate_offer_object(resp)
            print(offer)


def get_wall(symbol):
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

        if previous_level_amount * 100 / current_level_amount < PERCENTAGE_FOR_WALL_LEVEL and row[2] > MAX_TOTAL_VALUE:
            wall_level = row[0]
            return wall_level

        previous_level_amount = current_level_amount

    # if in some reason function is not able to set correct wall level, use FRR
    return get_frr(symbol)


api_key = os.getenv("API_KEY")
api_secret = os.getenv("API_SECRET")

client = BitfinexClient(key=api_key, secret=api_secret)

if SYMBOL == "USD":
    mim_amount = 150
elif SYMBOL == "LTC":
    mim_amount = 2  # TODO: recalculate every time based on current price
else:
    mim_amount = "sting over int to crash..."  # todo: correct handle min_amounts per symbol - like calculate rate by actual price (?)

while True:

    while True:
        try:
            result = client.get_active_funding_orders(f"f{SYMBOL}")
            break
        except ConnectionError as ce:
            print(f"{ce.__class__.__name__} - {str(ce)}")
            print("I will try send request again after 1 second.")
            sleep(1)

    print("Currently active funding(s):") if len(result) > 0 else None
    for i, r in enumerate(result):
        row = ActiveFunding(
            order_id=r[0],
            symbol=r[1],
            date_created=r[2],
            date_updated=r[3],
            amount=r[4],
            amount_symbol=r[5],
            _type=r[6],
            flags=r[10],
            rate=r[14],
            period=r[15]
        )
        print(row)

        now = datetime.today()
        delta = timedelta(hours=4)
        frame = now - delta

        if frame > row.date_created:
            client.set_cancel_funding_order(row.order_id)

    result = client.get_wallets()
    for r in result:
        if r[0] == "funding" and r[1] == SYMBOL:
            available_balance = float(r[4])

            now = datetime.now()
            t = now.strftime("%d-%m-%Y %H:%M:%S")
            print(f"{t}\tDostupný zostatok na účte je: {round(available_balance, 2)} {SYMBOL}")

            if available_balance >= mim_amount:

                # create_cascade(SYMBOL, available_balance)
                # set_best_rate(SYMBOL, available_balance)
                set_best_rate_small_cascade(SYMBOL, available_balance, cascade_levels=5)
                
    sleep(5*60)  # every 5 minutes... # TODO add argument reader if user want to run as demon or once every X minutes (cronjob, ...)
