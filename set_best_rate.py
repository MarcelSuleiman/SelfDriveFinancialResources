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

MAX_RATE = float(os.getenv("MAX_RATE"))
MIN_RATE = float(os.getenv("MIN_RATE"))
MIN_FOR_30D = float(os.getenv("MIN_FOR_30D"))


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
    date_created: datetime
    date_updated: datetime
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
    # mean_daily_high = get_candles(f"f{symbol}")
    # mean_daily_high = float(get_frr(f"f{symbol}"))
    # my_rate = mean_daily_high

    my_rate = get_wall(f"f{symbol}")

    # print(my_rate)

    if available_balance > cascade_levels*150:
        temp = available_balance // cascade_levels
        temp_zostatok = available_balance - ((cascade_levels-1)*temp)

        # print(temp)
        # print(temp_zostatok)
        
        for i in range(cascade_levels-1):
            my_rate -= 0.00001

            # print(mean_daily_high)
            # print(my_rate)
            
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

            offer = generate_offer_object(resp)

            # offer = SubmittedFundingOffer(mst=resp[0], _type=resp[1], msg_id=resp[2], funding_offer_array=FundingOfferArray(*resp[4]), code=resp[5], status=resp[6], text=resp[7])
            # offer = SubmittedFundingOffer(
            #     mst=resp[0],
            #     type_=resp[1],
            #     msg_id=resp[2],
            #     none1=resp[3],
            #     funding_offer_array=FundingOfferArray(
            #         id_=resp[4][0],
            #         symbol=resp[4][1],
            #         mts_created=resp[4][2],
            #         mts_updated=resp[4][3],
            #         amount=resp[4][4],
            #         amount_original=resp[4][5],
            #         offer_type=resp[4][6],
            #         none1=resp[4][7],
            #         none2=resp[4][8],
            #         flags=resp[4][9],
            #         offer_status=resp[4][10],
            #         none3=resp[4][11],
            #         none4=resp[4][12],
            #         none5=resp[4][13],
            #         rate=resp[4][14],
            #         period=resp[4][15],
            #         notify=resp[4][16],
            #         hidden=resp[4][17],
            #         none6=resp[4][18],
            #         renew=resp[4][19]
            #     ),
            #     code=resp[5],
            #     status=resp[6],
            #     text=resp[7]
            # )
            # offer = SubmittedFundingOffer(
            #     **{key: resp[i] for i, key in enumerate(SubmittedFundingOffer.__fields__.keys())}
            # )
            print(offer)

        my_rate -= 0.00001
            
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
        offer = generate_offer_object(resp)
        print(offer)
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

        # print(rate, type(rate))
        # print(_rate, type(_rate))
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

        # d = previous_level_amount * 100 / current_level_amount
        # print(d)

        if previous_level_amount * 100 / current_level_amount < 15 and row[2] > 100000000:
            wall_level = row[0]
            return wall_level

        previous_level_amount = current_level_amount

    # if in some reason function is not able to set correct wall level, use FRR
    return get_frr(symbol)


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

    # print("Currently active funding(s):") if len(result) > 0 else print("Currently we doesn't have any active funding.")
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
        if r[0] == "funding" and r[1] == symbol:
            available_balance = float(r[4])

            now = datetime.now()
            t = now.strftime("%d-%m-%Y %H:%M:%S")
            print(f"{t}\tDostupný zostatok na účte je: {round(available_balance, 2)} {symbol}")

            if available_balance >= mim_amount:

                # create_cascade(symbol, available_balance)
                # set_best_rate(symbol, available_balance)
                set_best_rate_small_cascade(symbol, available_balance, cascade_levels=5)
                
    sleep(5*60)  # every 5 minutes...
