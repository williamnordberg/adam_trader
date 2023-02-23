from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
import pandas as pd
import yfinance as yf
import os
from fredapi import Fred
import pandas as pd
import yfinance as yf
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
import os


def update_yahoo_data1():
    main_dataset = pd.read_csv('main_dataset.csv')

    fred = Fred(api_key='8f7cbcbc1210c7efa87ee9484e159c21')
    series_id = 'DGS10'
    data = fred.get_series(series_id, observation_start='2022-01-01')
    df2 = pd.DataFrame({'Date': data.index, 'Interest Rate': data.values}, columns=['Date', 'Interest Rate'])
    df2.set_index('Date', inplace=True)
    df2.to_csv('interest_rate.csv')
    main_dataset['Interest Rate1'] = df2['Interest Rate']

    # Forward fill missing values with the last non-null value
    #main_dataset['Interest Rate1'] = main_dataset['Interest Rate1'].fillna(method='ffill')

    # Backward fill missing values with the next non-null value, but only up to the next value change
    #main_dataset['Interest Rate1'] = main_dataset['Interest Rate1'].fillna(method='bfill', limit=1)
    #main_dataset.to_csv('main_dataset.csv')
    #print(main_dataset['Interest Rate1'])
    print(main_dataset['Interest Rate1'] )
    return None


#update_yahoo_data1()
main_dataset = pd.read_csv('main_dataset.csv')

print(main_dataset['Rate'])
