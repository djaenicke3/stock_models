import alpaca_trade_api as tradeapi

from datetime import datetime
import requests
import ta
import numpy as np
import yfinance as yf


import pandas as pd
ALPACA_API_KEY = "PK5Q2YVJJ38P4WRYKXMF"
ALPACA_SECRET_KEY = "UVLNeh8enYEav7JZnani2wA8SLPWNWPxqaxhwczG"
base_url = 'https://paper-api.alpaca.markets'

api = tradeapi.REST(ALPACA_API_KEY, ALPACA_SECRET_KEY, base_url, api_version='v2')
#This is for checking account status
# account = api.get_account()
# print(account)


#Code for getting data
eq = api.get_barset('EQ', '1Min')
print(eq)
print(len(eq["EQ"]))
def get_trigers(df, lags, buy=True):
    dfx = pd.DataFrame()
    for i in range(1, lags+1):
        if buy:
            mask = (df["%K"].shift(i)<20) & (df["%D"].shift(i)<20)
        else:
            mask = (df["%K"].shift(i)>80) & (df["%D"].shift(i)>80)
        dfx = dfx.append(mask, ignore_index =True)
    return dfx.sum(axis=0)


def strategy_intra(ticker,interval="15m"):
    df = yf.download(ticker, start="2021-07-25", interval=interval)
    df["%K"] = ta.momentum.stoch(df.High,df.Low,df.Close, window=14,smooth_window=3)
    df['%D'] = df["%K"].rolling(3).mean()
    df["rsi"] = ta.momentum.rsi(df.Close, window=14)
    df["macd"] = ta.trend.macd_diff(df.Close)
    df.dropna(inplace=True)

    dfx = pd.DataFrame()
    for i in range(1,4):
        mask = (df['%K'].shift(i)<20) & (df['%D'].shift(i) < 20)
        dfx = dfx.append(mask,ignore_index = True)
    dfx.sum(axis=0)
    df["Buytrigger"] = np.where(get_trigers(df, 4), 1, 0)
    df["Selltrigger"] = np.where(get_trigers(df, 4, False), 1, 0)
    if np.where((df.Buytrigger) &
                         (df["%K"].between(20, 80)) & (df["%D"].between(20, 80)) & (df.rsi > 50) &
                         (df.macd > 0), 1, 0)
    df["Sell"] = np.where((df.Buytrigger) &
                          (df["%K"].between(20, 80)) & (df["%D"].between(20, 80)) & (df.rsi < 50) &
                          (df.macd < 0), 1, 0)