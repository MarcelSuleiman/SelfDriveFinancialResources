from datetime import datetime

from pydantic import BaseModel, field_validator


class TickerTrading(BaseModel):
    bid: float
    bid_size: float
    ask: float
    ask_size: float
    daily_change: float
    daily_change_relative: float
    last_price: float
    volume: float
    high: float
    low: float


class TickerFunding(BaseModel):
    frr: float
    bid: float
    bid_period: int
    bid_size: float
    ask: float
    ask_period: int
    ask_size: float
    daily_change: float
    daily_change_perc: float
    last_price: float
    volume: float
    high: float
    low: float
    none1: None = None
    none2: None = None
    frr_amount_available: float


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
    id: int
    symbol: str
    date_created: datetime
    date_updated: datetime
    amount: float
    amount_symbol: float
    type: str
    none1: None = None
    none2: None = None
    flags: object
    status: str
    none3: None = None
    none4: None = None
    none5: None = None
    rate: float
    period: int
    notify: int
    hidden: int
    none6: None = None
    renew: int

    def __str__(self):
        line = "{:<15}: {} {} {:<10} {} {}".format(
            self.id,
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
