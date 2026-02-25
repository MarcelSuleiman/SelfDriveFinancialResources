from typing import Any, get_origin, Union, get_args, Type

from pydantic import BaseModel

from models import FundingOfferArray
from models import SubmittedFundingOffer


def generate_offer_object(resp: list[Any]) -> SubmittedFundingOffer | BaseModel:
    return from_list(SubmittedFundingOffer, resp)


def from_list(model_cls: Type[BaseModel], values: list[Any]) -> BaseModel:
    """
    Automaticky namapuje list hodnôt na Pydantic model (vrátane vnorených).
    """
    field_names = list(model_cls.model_fields.keys())
    kwargs = {}

    value_idx = 0

    for field_name in field_names:
        if value_idx >= len(values):
            break

        field = model_cls.model_fields[field_name]
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
