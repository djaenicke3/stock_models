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
    past = []
    status = []

    final_dict = {}
    Rolling = []
    re_invest =  []
    by_hold = []
    New_strategy = []

    for i in Tickers:
        a = i
        ohlcv_histories, technical_indicators, next_day_open_values, unscaled_y, y_normaliser = csv_to_dataset(a)


        n = int(ohlcv_histories.shape[0])-1# * test_split)

        ohlcv_train = ohlcv_histories[:n]
        tech_ind_train = technical_indicators[:n]
        y_train = next_day_open_values[:n]

        ohlcv_test = ohlcv_histories[n:]
        tech_ind_test = technical_indicators[n:]
        y_test = next_day_open_values[n:]
        past_y  = unscaled_y[-1]




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
        if past_y > y_test_predicted:
            status.append("SELL/HOLD")
        if past_y < y_test_predicted:
            status.append("BUY")

    return status




