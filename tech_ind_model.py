import keras
import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dense, Dropout, LSTM, Input, Activation, concatenate
from tensorflow.keras import optimizers
import numpy as np
np.random.seed(4)
from tensorflow.python.framework.random_seed import set_random_seed
set_random_seed(4)
from util import csv_to_dataset, history_points, Bull_twok, buy_hold, strategy_two , new_strategy




def predictions(Tickers):

    final_dict = {}
    Rolling = []
    re_invest =  []
    by_hold = []
    New_strategy = []

    for i in Tickers:
        a = i
        ohlcv_histories, technical_indicators, next_day_open_values, unscaled_y, y_normaliser = csv_to_dataset(a)

        test_split = 0.9
        n = int(ohlcv_histories.shape[0] * test_split)

        ohlcv_train = ohlcv_histories[:n]
        tech_ind_train = technical_indicators[:n]
        y_train = next_day_open_values[:n]

        ohlcv_test = ohlcv_histories[n:]
        tech_ind_test = technical_indicators[n:]
        y_test = next_day_open_values[n:]

        unscaled_y_test = unscaled_y[n:]


# model architecture

# define two sets of inputs
        lstm_input = Input(shape=(history_points, 5), name='lstm_input')
        dense_input = Input(shape=(technical_indicators.shape[1],), name='tech_input')

# the first branch operates on the first input
        x = LSTM(100, name='lstm_0')(lstm_input)
        x = Dropout(0.2, name='lstm_dropout_0')(x)
        lstm_branch = Model(inputs=lstm_input, outputs=x)

# the second branch opreates on the second input
        y = Dense(20, name='tech_dense_0')(dense_input)
        y = Activation("relu", name='tech_relu_0')(y)
        y = Dropout(0.2, name='tech_dropout_0')(y)
        technical_indicators_branch = Model(inputs=dense_input, outputs=y)

# combine the output of the two branches
        combined = concatenate([lstm_branch.output, technical_indicators_branch.output], name='concatenate')

        z = Dense(64, activation="sigmoid", name='dense_pooling')(combined)

        z = Dense(1, activation="linear", name='dense_out')(z)

# our model will accept the inputs of the two branches and
# then output a single value
        model = Model(inputs=[lstm_branch.input, technical_indicators_branch.input], outputs=z)
        adam = optimizers.Adam(lr=0.0005)
        model.compile(optimizer=adam, loss='mse')
        model.fit(x=[ohlcv_train, tech_ind_train], y=y_train, batch_size=32, epochs=50, shuffle=True, validation_split=0.1)


# evaluation

        y_test_predicted = model.predict([ohlcv_test, tech_ind_test])
        y_test_predicted = y_normaliser.inverse_transform(y_test_predicted)
        y_predicted = model.predict([ohlcv_histories, technical_indicators])
        y_predicted = y_normaliser.inverse_transform(y_predicted)
#assert unscaled_y_test.shape == y_test_predicted.shape
        real_mse = np.mean(np.square(unscaled_y_test - y_test_predicted))
        scaled_mse = real_mse / (np.max(unscaled_y_test) - np.min(unscaled_y_test)) * 100


        start = 0
        end = -1


        Df = pd.DataFrame(unscaled_y_test , columns=["Real_values"])
        Df["predicted_value"] = y_test_predicted





        Real_val = [i for i in Df["Real_values"]]
        Pred_val = [i for i in Df["predicted_value"]]

        correct = 1
        for i in range(1,len(Real_val)):
            if (Real_val[i]> Real_val[i-1]) and (Pred_val[i]>Pred_val[i-1]):
                correct+=1
            if (Real_val[i]< Real_val[i-1]) and (Pred_val[i]<Pred_val[i-1]):
                correct+=1

        total = len(Real_val)
        accuracy = (correct / total) * 100

        s = Bull_twok(Real_val,Pred_val)
        s1 = buy_hold(Real_val, Pred_val)
        s2 = strategy_two(Real_val,Pred_val)
        s3 = new_strategy(Real_val,Pred_val)

        temp_dict = {"Rolling":s,"buy_hold":s1,"Reinvest":s2,"New_strategy":s3}
        re_invest.append(s2)
        by_hold.append(s1)
        Rolling.append(s)
        New_strategy.append(s3)

        final_dict[a]=temp_dict

        df1 = pd.DataFrame(list(zip(Tickers,by_hold)),columns=["Tickers", "amount"])
        df2 = pd.DataFrame(list(zip(Tickers,Rolling)), columns=["Tickers", "amount"])
        df3 = pd.DataFrame(list(zip(Tickers, re_invest)), columns=["Tickers", "amount"])
        df4 = pd.DataFrame(list(zip(Tickers, New_strategy)), columns=["Tickers", "amount"])


    return df1,df2,df3, df4                 #df4# accuracy, Real_val, Pred_val#s , s1 , s2, accuracy, Real_val, Pred_val#df1,df2,df3, accuracy





# Df.to_csv("Results.csv")
# real = plt.plot(unscaled_y[start:end], label='real')
# pred = plt.plot(y_predicted[start:end], label='predicted')

#plt.legend(['Real', 'Predicted'])

#plt.show()

from datetime import datetime
#model.save(f'technical_model.h5')
