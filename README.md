# SelfDriveFinancialResources

This little helpmate keeps your finances as much as possible on offer for lending.
Every 5 minutes, it looks to see if any money has been released from previous loans
(or if new money has been added), and if the amount is greater than $150 (the current lowest possible amount for 1 offer),
it calculates the ideal interest rate, making sure that the rate is slightly lower than the FRR or slightly lower
than the wall of a large amount of accumulated money at one level of the interest rate.

If the offer does not meet the demand, the offer will be cancelled and the script will recalculate the ideal interest 
rate again based on the current situation and the new data and re-initiate the offer.

More about funding / lending on Bitfinex (i.e. what is going on?) you can find on their [official page](https://support.bitfinex.com/hc/en-us/articles/214441185-What-is-Margin-Funding)


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
```sh
python set_best_rate.py
```
