from typing import List

from models import ActiveFunding
import inspect


def get_active_fundings(active_funding_orders) -> List[ActiveFunding]:
    param_names = list(ActiveFunding.__fields__.keys())

    try:
        return [
            ActiveFunding(**dict(zip(param_names, r))) for r in active_funding_orders
        ]
    except Exception as e:
        raise Exception(str(e))
