import datetime as dt
import matplotlib.pyplot as plt
from matplotlib import style
import pandas as pd
import pandas_datareader as web
from mplfinance.original_flavor import candlestick_ohlc
import matplotlib.dates as mdates
import numpy as np
import finplot as fplt

style.use('ggplot')
# #df = pd.read_csv("SPY.csv", parse_dates=True, index_col=0)
#
# df_ohlc = df["Adj Close"].resample('10D').ohlc()
# df_volume = df["Volume"].resample('10D').sum()
#
# df_ohlc.reset_index(inplace=True)
# df_ohlc['Date'] = df_ohlc['Date'].map(mdates.date2num)
# ax1 = plt.subplot2grid((6,1), (0,0), rowspan=5, colspan=1)
# ax2 = plt.subplot2grid((6,1), (5,0), rowspan=1, colspan=1, sharex=ax1)
# ax1.xaxis_date()
# # fplt.candlestick_ochl(df[['Open','Close','High','Low']])
# # fplt.show()
#
# candlestick_ohlc(ax1, df_ohlc.values, width=5, colorup='g')
# #ax2.fill_between(df_volume.index.map(mdates.date2num), df_volume.values, 0)
# #plt.show()


def visualize_data():
    df = pd.read_csv('sp500_joined_closes.csv')
    df_corr = df.corr()
    print(df_corr.head())
    df_corr.to_csv('sp500corr.csv')
    data1 = df_corr.values
    fig1 = plt.figure()
    ax1 = fig1.add_subplot(111)

    heatmap1 = ax1.pcolor(data1, cmap=plt.cm.RdYlGn)
    fig1.colorbar(heatmap1)

    ax1.set_xticks(np.arange(data1.shape[1]) + 0.5, minor=False)
    ax1.set_yticks(np.arange(data1.shape[0]) + 0.5, minor=False)
    ax1.invert_yaxis()
    ax1.xaxis.tick_top()
    column_labels = df_corr.columns
    row_labels = df_corr.index
    ax1.set_xticklabels(column_labels)
    ax1.set_yticklabels(row_labels)
    plt.xticks(rotation=90)
    heatmap1.set_clim(-1, 1)
    plt.tight_layout()
    plt.show()


visualize_data()
