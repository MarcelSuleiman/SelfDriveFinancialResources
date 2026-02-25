from typing import List

from models import ActiveFunding


def get_active_fundings(active_funding_orders) -> List[ActiveFunding]:
    param_names = list(ActiveFunding.model_fields.keys())

    try:
        return [
            ActiveFunding(**dict(zip(param_names, r))) for r in active_funding_orders
        ]
    except Exception:
        raise
