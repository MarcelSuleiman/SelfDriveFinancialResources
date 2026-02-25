from models import TickerTrading, TickerFunding


def generate_ticker_object(data, type_):
    if type_ == "t":
        model_cls = TickerTrading
    elif type_ == "f":
        model_cls = TickerFunding
    else:
        raise TypeError(f"Asked type: '{type_}' is not valid. Choose 't' as trading or 'f' as funding")

    param_names = list(model_cls.model_fields.keys())
    return model_cls(**dict(zip(param_names, data)))
