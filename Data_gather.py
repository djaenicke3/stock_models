import bs4 as bs
import datetime as dt
import os
import pandas_datareader as web
import pickle
import requests
import time

def save_sp500_tickers():
    resp = requests.get('http://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    soup = bs.BeautifulSoup(resp.text, 'lxml')
    table = soup.find('table', {'class': 'wikitable sortable'})
    tickers = []
    for row in table.findAll('tr')[1:]:
        ticker = row.findAll('td')[0].text
        tickers.append(ticker)
    with open("sp500tickers.pickle", "wb") as f:
        pickle.dump(tickers, f)
    return tickers


save_sp500_tickers()
def get_data_from_yahoo(reload_sp500=False):
    if reload_sp500:
        tickers = save_sp500_tickers()

    else:
        with open("sp500tickers.pickle", "rb") as f:
            tickers = pickle.load(f)
    if not os.path.exists('stock_dfs'):
        os.makedirs('stock_dfs')

    start = dt.datetime(2016, 1, 1)
    end = dt.datetime.now()
    for ticker in tickers:

        if not os.path.exists('stock_dfs/{}.csv'.format(ticker)):
            print(type(ticker))

            try:


                df = company(ticker[:-1])

                print(df)






                df.to_csv('stock_dfs\{}.csv'.format(ticker[:-1]))

            except:
                print("Ace")
                continue
            #time.sleep(0.5)

        else:
            print('Already have {}'.format(ticker))
def company(ticker):
    start = dt.datetime(2016, 1, 1)
    end = dt.datetime.now()
    df = web.DataReader(ticker, "yahoo",start,end)
    df.reset_index(inplace=True)
    df.set_index("Date", inplace=True)
    return df

get_data_from_yahoo()