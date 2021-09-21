import yfinance as yf
import ta
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pickle
import time


# df = yf.download("ETH-USD", start="2021-07-20", interval='15m')
# df["%K"] = ta.momentum.stoch(df.High,df.Low,df.Close, window=14,smooth_window=3)
# df['%D'] = df["%K"].rolling(3).mean()
# df["rsi"] = ta.momentum.rsi(df.Close, window=14)
# df["macd"] = ta.trend.macd_diff(df.Close)
# df.dropna(inplace=True)

# dfx = pd.DataFrame()
# for i in range(1,4):
#     mask = (df['%K'].shift(i)<20) & (df['%D'].shift(i) < 20)
#     dfx = dfx.append(mask,ignore_index = True)
# dfx.sum(axis=0)

def get_trigers(df, lags, buy=True):
    dfx = pd.DataFrame()
    for i in range(1, lags+1):
        if buy:
            mask = (df["%K"].shift(i)<20) & (df["%D"].shift(i)<20)
        else:
            mask = (df["%K"].shift(i)>80) & (df["%D"].shift(i)>80)
        dfx = dfx.append(mask, ignore_index =True)
    return dfx.sum(axis=0)

# df["Buytrigger"] = np.where(get_trigers(df,4),1,0)
# df["Selltrigger"] = np.where(get_trigers(df,4,False),1,0)
# df["Buy"] = np.where((df.Buytrigger)&
#                     (df["%K"].between(20,80))&  (df["%D"].between(20,80))& (df.rsi > 50) &
#                     (df.macd > 0 ), 1,0)
# df["Sell"] = np.where((df.Buytrigger)&
#                     (df["%K"].between(20,80))&  (df["%D"].between(20,80))& (df.rsi <50) &
#                     (df.macd < 0 ), 1,0)
#
# Buying_dates, Selling_dates = [],[]
#
# for i in range(len(df)-1):
#     if df.Buy.iloc[i]:
#         Buying_dates.append(df.iloc[i+1].name)
#         for num,j in enumerate(df.Sell[i:]):
#             if j:
#                 Selling_dates.append(df.iloc[i+num+1].name)
#                 break
#
# cutit = len(Buying_dates) - len(Selling_dates)
#
# if cutit:
#     Buying_dates = Buying_dates[:-cutit]
# frame = pd.DataFrame({"Buying_dates": Buying_dates,"Selling_dates": Selling_dates})
#
#
# actuals = frame[frame.Buying_dates > frame.Selling_dates.shift(1)]

# def profitcalc():
#     Buyprices = df.loc[actuals.Buying_dates].Open
#     Selling_dates = df.loc[actuals.Selling_dates].Open
#     return (Selling_dates.values - Buyprices.values)/Buyprices.values


# profits = profitcalc()
# print("PROFIT IN DOLLARS")
# print((profits + 1).prod()*2000 -2000)
#
# plt.figure(figsize=(20,10))
# plt.plot(df.Close, color="k",alpha=0.7)
# plt.scatter(actuals.Buying_dates, df.Open[actuals.Buying_dates],marker='^',color='g',s=500)
# plt.scatter(actuals.Buying_dates, df.Open[actuals.Selling_dates],marker='v',color='r',s=500)
# plt.show()

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
    df["Buy"] = np.where((df.Buytrigger) &
                         (df["%K"].between(20, 80)) & (df["%D"].between(20, 80)) & (df.rsi > 50) &
                         (df.macd > 0), 1, 0)
    df["Sell"] = np.where((df.Buytrigger) &
                          (df["%K"].between(20, 80)) & (df["%D"].between(20, 80)) & (df.rsi < 50) &
                          (df.macd < 0), 1, 0)

    Buying_dates, Selling_dates = [], []

    for i in range(len(df) - 1):
        if df.Buy.iloc[i]:
            Buying_dates.append(df.iloc[i + 1].name)
            for num, j in enumerate(df.Sell[i:]):
                if j:
                    Selling_dates.append(df.iloc[i + num + 1].name)
                    break

    cutit = len(Buying_dates) - len(Selling_dates)

    if cutit:
        Buying_dates = Buying_dates[:-cutit]
    frame = pd.DataFrame({"Buying_dates": Buying_dates, "Selling_dates": Selling_dates})

    actuals = frame[frame.Buying_dates > frame.Selling_dates.shift(1)]

    def profitcalc():
        Buyprices = df.loc[actuals.Buying_dates].Open
        Selling_dates = df.loc[actuals.Selling_dates].Open
        return (Selling_dates.values - Buyprices.values) / Buyprices.values
    profits = profitcalc()
    profits = ((profits+1).prod()*2000 - 2000)
    return  ticker , profits


# a,b = strategy_intra("AAPL","5m")
# print(a,b)

with open("sp500tickers.pickle", "rb") as f:
    tickers = pickle.load(f)

return_dict = {}
for tick in tickers[:]:
    try:
        a,b = strategy_intra(tick[:-2],"15m")
        time.sleep(1)

    except:
        continue
    return_dict[a] = b
sorted_order = dict(sorted(return_dict.items(), key=lambda item: item[1] , reverse=True))
data = pd.DataFrame(sorted_order.items(), columns=['Tickers', 'Pft_in_15m_int'])
data.to_csv("profit in 35 days intraday trade using 15m interval ")