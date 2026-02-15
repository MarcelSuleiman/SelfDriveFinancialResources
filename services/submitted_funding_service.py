import inspect
from typing import Any, get_origin, Union, get_args, Type

from pydantic import BaseModel

from models import FundingOfferArray
from models import SubmittedFundingOffer


def generate_offer_object(resp: list[Any]) -> SubmittedFundingOffer or BaseModel:
    # # vytvor dict pre vnorený objekt
    # funding_fields = FundingOfferArray.__fields__.keys()
    # funding_dict = dict(zip(funding_fields, resp[4]))
    #
    # funding_offer = FundingOfferArray(**funding_dict)
    #
    # # vytvor dict pre hlavný objekt
    # main_fields = ['mst', 'type_', 'msg_id', 'none1', 'funding_offer_array', 'code', 'status', 'text']
    # main_values = [resp[0], resp[1], resp[2], resp[3], funding_offer, resp[5], resp[6], resp[7]]
    # return SubmittedFundingOffer(**dict(zip(main_fields, main_values)))
    return from_list(SubmittedFundingOffer, resp)


def from_list(model_cls: Type[BaseModel], values: list[Any]) -> BaseModel:
    """
    Automaticky namapuje list hodnôt na Pydantic model (vrátane vnorených).
    """
    field_names = list(model_cls.__fields__.keys())
    kwargs = {}

    value_idx = 0

    for field_name in field_names:
        if value_idx >= len(values):
            break

        field = model_cls.__fields__[field_name]
        field_type = field.annotation

        value = values[value_idx]

        # Zisti, či field je vnorený Pydantic model
        is_nested_model = (
            isinstance(field_type, type) and
            issubclass(field_type, BaseModel)
        )

        # Ak je to Optional[PydanticModel], extrahuj typ
        if get_origin(field_type) is Union:
            args = get_args(field_type)
            if any(issubclass(arg, BaseModel) for arg in args if isinstance(arg, type)):
                for arg in args:
                    if isinstance(arg, type) and issubclass(arg, BaseModel):
                        field_type = arg
                        is_nested_model = True
                        break

        if is_nested_model and isinstance(value, list):
            # Rekurzívne zavolaj pre vnorený model
            nested_instance = from_list(field_type, value)
            kwargs[field_name] = nested_instance
        else:
            kwargs[field_name] = value

        value_idx += 1

    return model_cls(**kwargs)
