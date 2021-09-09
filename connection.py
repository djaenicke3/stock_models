import alpaca_trade_api as tradeapi
import threading
import time
import datetime
import logging
import argparse
# You must initialize logging, otherwise you'll not see debug output.
logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True
import pymongo

myclient = pymongo.MongoClient("mongodb://localhost:27017/")

mydb = myclient["Stock_Exchange"]
get_col = mydb["Stock_Status"]# the collect

# API KEYS
#region
API_KEY = "PKGSTTD8VRBIB159XLVS"
API_SECRET = "r08XYARQuASQUaI6D1vH30pghxu07GG8B62xYgrp"
APCA_API_BASE_URL = "https://paper-api.alpaca.markets"
api = tradeapi.REST(API_KEY, API_SECRET, APCA_API_BASE_URL, api_version='v2')

account = api.get_account()

# Check our current balance vs. our balance at the last market close
balance_change = float(account.equity)#- float(account.last_equity)
print(f'Today\'s portfolio balance change: ${balance_change}')


account = api.get_account()

# Check if our account is restricted from trading.
if account.trading_blocked:
    print('Account is currently restricted from trading.')
else:
    print("You can trade ")

# Check how much money we can use to open new positions.
print('${} is available as buying power.'.format(account.buying_power))
k = get_col.find()
for i in k:

    for j,l in i.items():
        if l == "BUY":
            print(1)

            # api.submit_order(
            #     symbol=str(j),
            #     qty=1,  # notional value of 1.5 shares of SPY at $300
            #     side='buy',
            #     type='market',
            #     time_in_force='day',
            # )
# #endregion
#Buy a stock when a doji candle forms
api.submit_order(
                symbol="SPY",
                qty=1,  # notional value of 1.5 shares of SPY at $300
                side='buy',
                type='market',
                time_in_force='day',
            )