# import numpy as np
# import  datetime as dt
# import matplotlib.pyplot as plt
# import pandas as pd
# from datetime import timedelta
# from sklearn.preprocessing import RobustScaler
# plt.style.use("bmh")
# import pandas_datareader as web
# # Technical Analysis library
# import ta
#
# # Neural Network library
# from keras.models import Sequential
# from keras.layers import LSTM, Dense, Dropout
#
# start = dt.datetime(2018, 1, 1)
# end = dt.datetime.now()
#
# data = web.DataReader("EQ", 'yahoo', start, end)
# print(data)

import yfinance as yf
import ta
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pickle
import time



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
    df = yf.download(ticker, start="2021-07-30", interval=interval)
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
    df["Buy"] = np.where((df.Buytrigger) &
                         (df["%K"].between(20, 80)) & (df["%D"].between(20, 80)) & (df.rsi > 50) &
                         (df.macd > 0), 1, 0)
    df["Sell"] = np.where((df.Buytrigger) &
                          (df["%K"].between(20, 80)) & (df["%D"].between(20, 80)) & (df.rsi < 50) &
                          (df.macd < 0), 1, 0)

    return df


df = strategy_intra("EQ")

Buy  =list(df["Buy"])
sell = list(df["Sell"])
print(Buy)
print(sell)