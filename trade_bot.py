import numpy as np
##import yfinance as yf
import json
import alpaca_trade_api as tradeapi
import ta
import random
import pandas as pd
ALPACA_API_KEY = "PKTRHSF675P5F63Z30BE"
ALPACA_SECRET_KEY = "oqux38a7VyDh3WDCnefxtMfhfjZJ8M7oPajPJAYg"
base_url = 'https://paper-api.alpaca.markets'

import logging
import argparse
# You must initialize logging, otherwise you'll not see debug output.
logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True
num = random.randint(1,5)
# f = open("root/stock_models/working.txt","w")
# f.write("working " + str(num))

class Trade_bot:
    def __init__(self):
        self.alpaca = tradeapi.REST(ALPACA_API_KEY, ALPACA_SECRET_KEY, base_url, api_version='v2')

    def get_df(self,symbol, interval='5Min'):
        eq = self.alpaca.get_barset(symbol, interval)

        df = pd.DataFrame()

        for i in eq[symbol]:
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

    def strategy_intra(self,ticker, interval="1Min"):
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
        limit_price_buy = str(float(df["c"].iloc[-1]) * 1.05)  # take profit on 2 percent
        stop_price_buy = str(float(df["c"].iloc[-1]) * 0.95)
        stop_loss_buy = str(float(df["c"].iloc[-1]) * 0.945)
        limit_price_sell = str(float(df["c"].iloc[-1]) * 0.945)
        stop_price_sell = str(float(df["c"].iloc[-1]) * 1.045)
        stop_loss_sell = str(float(df["c"].iloc[-1]) * 1.05)
        rsi = df["rsi"].iloc[-1]
        k_line = df["%K"].iloc[-1]
        d_line = df["%D"].iloc[-1]


        if df["Sell"].iloc[-1] == 1:
            self.alpaca.submit_order(
                symbol=ticker,
                qty=10,  # notional value of 1.5 shares of SPY at $300
                side='sell',
                type='market',
                time_in_force='day',
                order_class="bracket",
                take_profit=dict(limit_price = limit_price_sell,),
                stop_loss=dict(
                    stop_price = stop_price_sell,
                    limit_price = stop_loss_sell ,
                )
            )
            account = self.alpaca.get_account()
            balance = float(account.equity)
            profit = balance - float(account.last_equity)
            return "Sell",balance,profit,rsi,k_line,d_line
        if df["Buy"].iloc[-1] == 1:
            self.alpaca.submit_order(
                symbol=ticker,
                qty=10,  # notional value of 1.5 shares of SPY at $300
                side='buy',
                type='market',
                time_in_force='day',
                order_class="bracket",
                take_profit=dict(limit_price = limit_price_buy,),
                stop_loss=dict(
                    stop_price = stop_price_buy,
                    limit_price = stop_loss_buy ,
                )
            )
            account = self.alpaca.get_account()
            balance = float(account.equity)
            profit = balance - float(account.last_equity)
            return "Buy",balance,profit,rsi,k_line,d_line
        account = self.alpaca.get_account()
        balance = float(account.equity)
        profit = balance - float(account.last_equity)

        return "Hold" , balance ,profit,rsi,k_line,d_line


ls = Trade_bot()
# status,balance,profit =  ls.strategy_intra("EQ")
# f = open("EQ_stats.txt","a")
# text = "The current status  for EQ is {status} where as our current balance is {balance} and our profit is {profit}".format(status=status, balance=balance,profit=profit)
# f.write(text)


lst_stocks = ["BBW","HA","M","FC","SE","VOO","XPOF","OCUL","FITB","HPQ","AMC","GME"]
for stock in lst_stocks:
    status, balance, profit,rsi,kl,dl = ls.strategy_intra(stock)
    if status == "Hold":
        continue

    file_name = "stats.txt"
    text = "{stock} status: {status} balance :{balance} profit:{profit} , rsi: {rsi} ,kline: {kl}, dline: {dl}.".format(stock=stock,
        status=status, balance=balance, profit=profit,rsi=rsi,kl=kl,dl = dl)
    f = open(file_name, "a")
    f.write(text)





