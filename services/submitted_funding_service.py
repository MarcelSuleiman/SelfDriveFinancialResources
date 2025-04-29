from models import FundingOfferArray
from models import SubmittedFundingOffer


def generate_offer_object(resp: list[str]) -> SubmittedFundingOffer:
    offer = SubmittedFundingOffer(
        mst=resp[0],
        type_=resp[1],
        msg_id=resp[2],
        none1=resp[3],
        funding_offer_array=FundingOfferArray(
            id_=resp[4][0],
            symbol=resp[4][1],
            mts_created=resp[4][2],
            mts_updated=resp[4][3],
            amount=resp[4][4],
            amount_original=resp[4][5],
            offer_type=resp[4][6],
            none1=resp[4][7],
            none2=resp[4][8],
            flags=resp[4][9],
            offer_status=resp[4][10],
            none3=resp[4][11],
            none4=resp[4][12],
            none5=resp[4][13],
            rate=resp[4][14],
            period=resp[4][15],
            notify=resp[4][16],
            hidden=resp[4][17],
            none6=resp[4][18],
            renew=resp[4][19]
        ),
        code=resp[5],
        status=resp[6],
        text=resp[7]
    )

    return offer
