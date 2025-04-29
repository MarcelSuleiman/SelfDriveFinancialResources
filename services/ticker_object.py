from models import TickerTrading, TickerFunding


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