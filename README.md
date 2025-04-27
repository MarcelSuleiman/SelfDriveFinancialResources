# SelfDriveFinancialResources

> [!IMPORTANT]
> [Bitfinex to Wind Down Lending Pro](https://www.bitfinex.com/posts/1054)

This little helpmate keeps your finances as much as possible on offer for lending.
Every 5 minutes, it looks to see if any money has been released from previous loans
(or if new money has been added), and if the amount is greater than $150 (the current lowest possible amount for 1 offer),
it calculates the ideal interest rate, making sure that the rate is slightly lower than the 
[FRR](https://support.bitfinex.com/hc/en-us/articles/213919009-What-is-the-Bitfinex-Funding-Flash-Return-Rate) 
or slightly lower than the wall of a large amount of accumulated money at one level of the interest rate.

If the offer does not meet the demand, the offer will be cancelled and the script will recalculate the ideal interest 
rate again based on the current situation and the new data and re-initiate the offer.

More about funding / lending on Bitfinex (i.e. what is going on?) you can find on their 
[official page](https://support.bitfinex.com/hc/en-us/articles/214441185-What-is-Margin-Funding)


## how to install
1) Create new folder and name it as you wish.
2) Inside new folder run 2 commands:
```sh
git clone https://github.com/MarcelSuleiman/SelfDriveFinancialResources.git
```

```sh
git clone https://github.com/MarcelSuleiman/UnofficialBitfinexGateway.git
```
or you can download it manually & unzip

## how to set up & run
1) If you don't already have an account on [Bitfinex](https://www.bitfinex.com/), you need to open one.
2) Create api keys [link](https://setting.bitfinex.com/api#my-keys).
3) All setting keep as is except one: under `Margin Funding` find `Offer, cancel and close funding` set it as __enable__.
4) Save & close.
5) Go to `SelfDriveFinancialResources` folder.
6) Open file `secrets_template.env` in text editor, fill `API_KEY` and `API_SECRET` from Bitfinex, save and close it.
7) Rename file from `secrets_template.env` to `secrets.env`
8) Navigate your terminal (bash, cmd, powershell, ...) to folder `..\SelfDriveFinancialResources` and run command:
* `pip install -r requirements.txt` to install all necessary libraries
* `python set_best_rate.py -h` to see all available arguments:
```usage: SelfDriveFinancialResource [-h] [-D {0,1}] [-C {USD,USDT,LTC}] [-S {cascade,single}] [-CL {1,2,3,4,5,6,7,8,9}] [-CS {1,2,3,4,5,6,7,8,9}] [-CVM {up,down}] [-FBS {FRR,WALL}]

options:
  -h, --help            show this help message and exit
  -D {0,1}, --daemon {0,1}
                        This sets whether the script should run in a loop (value 1) or shut down (value 0) after a bid is placed on the market.
  -C {USD,USDT,LTC}, --currency {USD,USDT,LTC}
                        What currency to be processed.
  -S {cascade,single}, --strategy {cascade,single}
                        Which strategy should be applied when placing a bid.
                        single: means that the entire available amount is taken and a bid for a single value (interest rate) is entered.
                        cascade: means that the entire available amount is divided into as many parts as specified in the -CL (--cascade_levels)
                                 parameter and the individual commands are successively set to the values calculated on the basis of -CS, -CVM and -FSB
  -CL {1,2,3,4,5,6,7,8,9}, --cascade_levels {1,2,3,4,5,6,7,8,9}
                        How many levels to apply - but how many parts to divide the amount.
                                Example: 3 means that the notional amount of available funds ($1500) is divided into 3 parts of $500 each
  -CS {1,2,3,4,5,6,7,8,9}, --cascade_steps {1,2,3,4,5,6,7,8,9}
                        In what steps will the interest rates be adjusted depending on the -CVM value.
                                Example: a value of 2 at the current interest rate of 0.045 percent per day (mathematically 0.00045)
                                means that 1 bid will be at 0.00045, the second at 0.00043, the third at 0.00041, etc.
  -CVM {up,down}, --cascade_vertical_movement {up,down}
                        In case of cascade and -CS higher than 1 in which direction the levels should be set.
                        up - means 0.045, 0.046, 0.047...
                        down - 0.045, 0.044, 0.043...
  -FBS {FRR,WALL}, --funding_book_strategy {FRR,WALL}
                        FRR - This rate is not based on an agreed fixed rate.
                                Instead, it is based on the average of all active fixed-rate fundings weighted by their amount.
                                This rate updates once per hour, allowing you to get rates that follow market action.
                        WALL - the script is trying to find an interest rate where a lot of money has been sent by other people
                                and thus they have created a wall - a dam above which it is very difficult to squeeze the interest because
                                there are enough funds to cover all the requirements. The WALL value lowers the interest by 0.0001 and
                                sets the bid to an achievable value. This is usually more than the current FRR.

```
Real demo usage:
```shell
python3 set_best_rate.py -D 1 -S cascade -FBS WALL -CL 5 -CS 2 -CVM down
```