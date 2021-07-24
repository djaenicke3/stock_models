import pandas as pd
from sklearn import preprocessing
import numpy as np
import requests
API_URL = "https://www.alphavantage.co/query"
apikey = "I92EXE4UX0377113"








history_points = 50


def csv_to_dataset(company):

    data = {"function": "TIME_SERIES_DAILY_ADJUSTED",
                    "symbol": company,
                    "outputsize": "full",
                    "datatype": "json",
                    "apikey": apikey}


    response = requests.get(API_URL,
                                    data)
    response_json = response.json()
    data = pd.DataFrame.from_dict(response_json['Time Series (Daily)'], orient='index')
    data = data.reset_index()
    data = data[0:751]
    data = data.iloc[::-1]

    data = data.drop('index', axis=1)
    data = data.drop('6. volume', axis=1)
    data = data.drop('7. dividend amount', axis=1)
    data = data.drop('8. split coefficient', axis=1)
    data = data.drop(0, axis=0)
    data = data.apply(pd.to_numeric)


    # data = pd.DataFrame.from_dict(response_json['Time Series (Daily)'], orient='index')
    # data = data.reset_index()

    data = data.values
    train_split = len(data) - int(len(data) / 10)
    data = data[:train_split]

    data_normaliser = preprocessing.MinMaxScaler()
    data_normalised = data_normaliser.fit_transform(data)

    # using the last {history_points} open close high low volume data points, predict the next open value
    ohlcv_histories_normalised = np.array([data_normalised[i:i + history_points].copy() for i in range(len(data_normalised) - history_points)])
    next_day_open_values_normalised = np.array([data_normalised[:, 0][i + history_points].copy() for i in range(len(data_normalised) - history_points)])
    next_day_open_values_normalised = np.expand_dims(next_day_open_values_normalised, -1)

    next_day_open_values = np.array([data[:, 0][i + history_points].copy() for i in range(len(data) - history_points)])
    next_day_open_values = np.expand_dims(next_day_open_values, -1)

    y_normaliser = preprocessing.MinMaxScaler()
    y_normaliser.fit(next_day_open_values)

    def calc_ema(values, time_period):
        # https://www.investopedia.com/ask/answers/122314/what-exponential-moving-average-ema-formula-and-how-ema-calculated.asp
        sma = np.mean(values[:, 3])
        ema_values = [sma]
        k = 2 / (1 + time_period)
        for i in range(len(his) - time_period, len(his)):
            close = his[i][3]
            ema_values.append(close * k + ema_values[-1] * (1 - k))
        return ema_values[-1]

    technical_indicators = []
    for his in ohlcv_histories_normalised:
        # note since we are using his[3] we are taking the SMA of the closing price
        sma = np.mean(his[:, 3])
        macd = calc_ema(his, 12) - calc_ema(his, 26)
        technical_indicators.append(np.array([sma]))
        # technical_indicators.append(np.array([sma,macd,]))

    technical_indicators = np.array(technical_indicators)

    tech_ind_scaler = preprocessing.MinMaxScaler()
    technical_indicators_normalised = tech_ind_scaler.fit_transform(technical_indicators)

    assert ohlcv_histories_normalised.shape[0] == next_day_open_values_normalised.shape[0] == technical_indicators_normalised.shape[0]
    return ohlcv_histories_normalised, technical_indicators_normalised, next_day_open_values_normalised, next_day_open_values, y_normaliser


def multiple_csv_to_dataset(test_set_name):
    import os
    ohlcv_histories = 0
    technical_indicators = 0
    next_day_open_values = 0
    for csv_file_path in list(filter(lambda x: x.endswith('daily.csv'), os.listdir('./'))):
        if not csv_file_path == test_set_name:
            print(csv_file_path)
            if type(ohlcv_histories) == int:
                ohlcv_histories, technical_indicators, next_day_open_values, _, _ = csv_to_dataset(csv_file_path)
            else:
                a, b, c, _, _ = csv_to_dataset(csv_file_path)
                ohlcv_histories = np.concatenate((ohlcv_histories, a), 0)
                technical_indicators = np.concatenate((technical_indicators, b), 0)
                next_day_open_values = np.concatenate((next_day_open_values, c), 0)

    ohlcv_train = ohlcv_histories
    tech_ind_train = technical_indicators
    y_train = next_day_open_values

    ohlcv_test, tech_ind_test, y_test, unscaled_y_test, y_normaliser = csv_to_dataset(test_set_name)

    return ohlcv_train, tech_ind_train, y_train, ohlcv_test, tech_ind_test, y_test, unscaled_y_test, y_normaliser

# def compute_earnings(Real_val, Pred_val):
#
#     purchase = 2000
#     balance = 2000
#     stock = purchase/Real_val[0]
#
#
#     for i in range(1,len(Real_val)):
#
#
#         if (Pred_val[i] > Pred_val[i - 1]):
#             balance+= stock*Real_val[i]
#             stock = 0
#         if  (Pred_val[i] < Pred_val[i - 1]) and stock!=0:
#             stock = balance/Real_val[i-1]
#             balance -= stock*Real_val[i-1]
#     return balance, stock

def buy_hold(Real_val, Pred_val):
    purchase = 2000/Real_val[0]
    sell = purchase * Real_val[-1]
    return sell -2000

    # while len(buys_) > 0 and len(sells_) > 0:
    #     if buys_[0][0] < sells_[0][0]:
    #         # time to buy $10 worth of stock
    #         balance -= purchase_amt
    #         stock += purchase_amt / buys_[0][1]
    #         buys_.pop(0)
    #     else:
    #         # time to sell all of our stock
    #         balance += stock * sells_[0][1]
    #         stock = 0
    #         sells_.pop(0)
    #print(f"earnings: ${balance}")

def Bull_twok(Real_val, Pred_val):
    balance = 2000
    amount = []
    earning = []
    end_profit = 0

    for i in range(1, len(Real_val)):


        prev_share = balance/Real_val[i-1]
        profit = prev_share*Real_val[i]
        amount.append((profit))
        earning.append(profit -balance)
        end_profit+=profit-balance


    return end_profit #amount, earning, end_profit

def Bull_twok_csv(Real_val, Pred_val):
    balance = 2000
    amount = []
    earning = []
    end_profit = []

    right_wrong = []


    for i in range(1, len(Real_val)):
        #
        # if (Real_val[i]> Real_val[i-1]) and (Pred_val[i]>Pred_val[i-1]):
        #     right_wrong.append("Right")
        # if (Real_val[i]< Real_val[i-1]) and (Pred_val[i]<Pred_val[i-1]):
        #     right_wrong.append(("Right"))
        # else:
        #     right_wrong.append("Wrong")
        prev_share = balance/Real_val[i-1]
        profit = prev_share*Real_val[i]
        amount.append((profit))
        earning.append(profit -balance)

        if earning[i-1] > 0:
            right_wrong.append("Right")
        else:
            right_wrong.append("Wrong")


    for i in range(len(earning)):
        if i == 0:
            end_profit.append(earning[i])
        if i != 0:
            end_profit.append(earning[i] +end_profit[i-1])



    df = pd.DataFrame(list(zip(Real_val[:],Pred_val[:],right_wrong,earning,end_profit)), columns=["Real_value","predicted_value","Predicted_price","money_gained_lost","Running_total"])




    return  df


