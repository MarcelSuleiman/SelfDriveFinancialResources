import argparse
from argparse import RawTextHelpFormatter


def compose_input_parser():
    parser = argparse.ArgumentParser("SelfDriveFinancialResource", formatter_class=RawTextHelpFormatter)
    parser.add_argument(
        "-D", "--daemon",
        choices=["0", "1"],
        default="1",
        type=str,
        help="This sets whether the script should run in a loop (value 1) "
             "or shut down (value 0) after a bid is placed on the market."
    )
    parser.add_argument(
        "-C", "--currency",
        choices=["USD", "USDT", "LTC"],
        default="USD",
        type=str,
        help="What currency to be processed."
    )
    parser.add_argument(
        "-S", "--strategy",
        choices=["cascade", "single"],
        default="single",
        type=str,
        help="Which strategy should be applied when placing a bid.\n"
             "single: means that the entire available amount is taken and a bid for a single value (interest rate) is entered.\n"
             "cascade: means that the entire available amount is divided into as many parts as specified in the "
             "-CL (--cascade_levels)\n\t parameter and the individual commands are successively set to the values "
             "calculated on the basis of -CS, -CVM and -FSB"
    )
    parser.add_argument(
        "-CL", "--cascade_levels",
        choices=[str(i) for i in range(1, 10)],  # ["1", "2", ... "9"]
        default="2",
        type=str,
        help="How many levels to apply - but how many parts to divide the amount.\n"
             "\tExample: 3 means that the notional amount of available funds ($1500) is divided into 3 parts of $500 each"
    )
    parser.add_argument(
        "-CS", "--cascade_steps",
        choices=[str(i) for i in range(1, 10)],  # ["1", "2", ... "9"]
        default="1",
        type=str,
        help="In what steps will the interest rates be adjusted depending on the -CVM value.\n"
             "\tExample: a value of 2 at the current interest rate of 0.045 percent per day (mathematically 0.00045)\n"
             "\tmeans that 1 bid will be at 0.00045, the second at 0.00043, the third at 0.00041, etc."
    )
    parser.add_argument(
        "-CVM", "--cascade_vertical_movement",
        choices=["up", "down"],
        default="down",
        type=str,
        help="In case of cascade and -CS higher than 1 in which direction the levels should be set.\n"
             "up - means 0.045, 0.046, 0.047...\n"
             "down - 0.045, 0.044, 0.043..."
    )
    parser.add_argument(
        "-FBS", "--funding_book_strategy",
        choices=["FRR", "WALL"],
        default="FRR",
        type=str,
        help="FRR - This rate is not based on an agreed fixed rate.\n"
             "\tInstead, it is based on the average of all active fixed-rate fundings weighted by their amount.\n"
             "\tThis rate updates once per hour, allowing you to get rates that follow market action.\n"
             "WALL - the script is trying to find an interest rate where a lot of money has been sent by other people\n"
             "\tand thus they have created a wall - a dam above which it is very difficult to squeeze the interest because\n"
             "\tthere are enough funds to cover all the requirements. The WALL value lowers the interest by 0.0001 and\n"
             "\tsets the bid to an achievable value. This is usually more than the current FRR."
    )

    return parser.parse_args()
