import numpy as np
#import yfinance as yf
import json
import alpaca_trade_api as tradeapi
import ta

import pandas as pd
ALPACA_API_KEY = "PKBNQ0DZTMY8DOB7JPAL"
ALPACA_SECRET_KEY = "HtXKpk7HcTPGW1Ct3NQijpaEGkd7xrOnPsinhvR8"
base_url = 'https://paper-api.alpaca.markets'

import logging
import argparse
# You must initialize logging, otherwise you'll not see debug output.
logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True

class Trade_bot:
    def __init__(self):
        self.alpaca = tradeapi.REST(ALPACA_API_KEY, ALPACA_SECRET_KEY, base_url, api_version='v2')

    def get_df(self,symbol, interval='5Min'):
        eq = self.alpaca.get_barset(symbol, interval)

        df = pd.DataFrame()

        for i in eq["EQ"]:
            a = str(i)
            a = a[4:-1]
            a = a.replace("'", '"')
            a = json.loads(a)

            df = df.append(a, ignore_index=True)
        return df

    def get_trigers(self,df, lags, buy=True):
        dfx = pd.DataFrame()
        for i in range(1, lags + 1):
            if buy:
                mask = (df["%K"].shift(i) < 20) & (df["%D"].shift(i) < 20)
            else:
                mask = (df["%K"].shift(i) > 80) & (df["%D"].shift(i) > 80)
            dfx = dfx.append(mask, ignore_index=True)
        return dfx.sum(axis=0)

    def strategy_intra(self,ticker, interval="5Min"):
        df = self.get_df(ticker, interval)
        df["%K"] = ta.momentum.stoch(df.h, df.l, df.c, window=14, smooth_window=3)
        df['%D'] = df["%K"].rolling(3).mean()
        df["rsi"] = ta.momentum.rsi(df.c, window=14)
        df["macd"] = ta.trend.macd_diff(df.c)
        df.dropna(inplace=True)

        dfx = pd.DataFrame()
        for i in range(1, 4):
            mask = (df['%K'].shift(i) < 20) & (df['%D'].shift(i) < 20)
            dfx = dfx.append(mask, ignore_index=True)
        dfx.sum(axis=0)
        df["Buytrigger"] = np.where(self.get_trigers(df, 4), 1, 0)
        df["Selltrigger"] = np.where(self.get_trigers(df, 4, False), 1, 0)
        df["Buy"] = np.where((df.Buytrigger) &
                             (df["%K"].between(20, 80)) & (df["%D"].between(20, 80)) & (df.rsi > 50) &
                             (df.macd > 0), 1, 0)
        df["Sell"] = np.where((df.Buytrigger) &
                              (df["%K"].between(20, 80)) & (df["%D"].between(20, 80)) & (df.rsi < 50) &
                              (df.macd < 0), 1, 0)
        if df["Sell"].iloc[-1] == 1:
            self.alpaca.submit_order(
                symbol=ticker,
                qty=400,  # notional value of 1.5 shares of SPY at $300
                side='sell',
                type='market',
                time_in_force='gtc',
            )
            return "Sell"
        if df["Buy"].iloc[-1] == 1:
            self.alpaca.submit_order(
                symbol='EQ',
                qty=400,  # notional value of 1.5 shares of SPY at $300
                side='buy',
                type='market',
                time_in_force='gtc',
            )
            return "Buy"
        account = self.alpaca.get_account()
        balance = float(account.equity)
        profit = balance - float(account.last_equity)

        return "Hold" , balance ,profit


ls = Trade_bot()
status,balance,profit =  ls.strategy_intra("EQ")
f = open("EQ_stats.txt","a")
text = "The current status  for EQ is {status} where as our current balance is {balance} and our profit is {profit}".format(status=status, balance=balance,profit=profit)

