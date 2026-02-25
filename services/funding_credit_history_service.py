from typing import List

from models import FundingCreditHistory


def get_fundings_credit_history(active_funding_orders) -> List[FundingCreditHistory]:
    param_names = list(FundingCreditHistory.model_fields.keys())

    try:
        return [
            FundingCreditHistory(**dict(zip(param_names, r))) for r in active_funding_orders
        ]
    except Exception:
        raise
