import numpy as np
import numpy as np
import pandas as pd
import requests




# read the data
dataset = pd.read_csv('main_dataset.csv', index_col='Date')
data_close = dataset['Close']


def calculate_bollinger_bands(data, window=20, std_dev=2):
    # Calculate rolling mean and standard deviation
    rolling_mean = data.rolling(window=window).mean()
    rolling_std = data.rolling(window=window).std()

    # Calculate upper and lower bands
    upper_band = rolling_mean + (rolling_std * std_dev)
    lower_band = rolling_mean - (rolling_std * std_dev)

    return upper_band, rolling_mean, lower_band


upper_band, rolling_mean, lower_band = calculate_bollinger_bands(data_close)
print(upper_band[-1], rolling_mean[-1], lower_band[-1])
