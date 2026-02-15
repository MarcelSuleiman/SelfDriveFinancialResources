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

    # result = []
    # for r in active_funding_orders:
    #     try:
    #         obj = ActiveFunding(**dict(zip(param_names, r)))
    #         result.append(obj)
    #     except Exception as e:
    #         print(f"❌ Chyba pri vytváraní ActiveFunding: {e}\n  → Dáta: {r}")
    # return result

# def get_active_fundings(active_funding_orders) -> List[ActiveFunding]:
#     active_fundings = []
#     for i, r in enumerate(active_funding_orders):
#         row = ActiveFunding(
#             id=r[0],
#             symbol=r[1],
#             date_created=r[2],
#             date_updated=r[3],
#             amount=r[4],
#             amount_symbol=r[5],
#             type=r[6],
#             none1=r[7],
#             none2=r[8],
#             flags=r[9],
#             status=r[10],
#             none3=r[11],
#             none4=r[12],
#             none5=r[13],
#             rate=r[14],
#             period=r[15],
#             notify=r[16],
#             hidden=r[17],
#             none6=r[18],
#             renew=r[19],
#         )
#         active_fundings.append(row)
#     return active_fundings
