from typing import List

from models import ActiveFunding


def get_active_fundings(active_funding_orders) -> List[ActiveFunding]:
    active_fundings = []
    for i, r in enumerate(active_funding_orders):
        row = ActiveFunding(
            id=r[0],
            symbol=r[1],
            date_created=r[2],
            date_updated=r[3],
            amount=r[4],
            amount_symbol=r[5],
            type=r[6],
            none1=r[7],
            none2=r[8],
            flags=r[9],
            status=r[10],
            none3=r[11],
            none4=r[12],
            none5=r[13],
            rate=r[14],
            period=r[15],
            notify=r[16],
            hidden=r[17],
            none6=r[18],
            renew=r[19],
        )
        active_fundings.append(row)
    return active_fundings
