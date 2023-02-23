import numpy as np
from sklearn.tree import DecisionTreeRegressor
from fredapi import Fred
import pandas as pd
import yfinance as yf
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
import os

# region A. update factors


def update_yahoo_data():
    # Set the start and end dates for the historical data
    start_date = '2022-11-01'
    end_date = '2023-02-20'
    # Use yfinance to get the historical data for Bitcoin
    ticker_data = yf.download('BTC-USD', start=start_date, end=end_date)
    # Create a Pandas DataFrame from the ticker data
    df1 = pd.DataFrame(ticker_data)
    fred = Fred(api_key='8f7cbcbc1210c7efa87ee9484e159c21')
    series_id = 'DGS10'
    data = fred.get_series(series_id, observation_start='2022-11-01')
    df2 = pd.DataFrame({'Date': data.index, 'Interest Rate': data.values}, columns=['Date', 'Interest Rate'])
    df2.set_index('Date', inplace=True)
    df1['Rate'] = df2['Interest Rate']
    # Forward fill missing values with the last non-null value
    df1['Rate'] = df1['Rate'].fillna(method='ffill')

    # Backward fill missing values with the next non-null value, but only up to the next value change
    df1['Rate'] = df1['Rate'].fillna(method='bfill', limit=1)
    return df1


def update_internal_factors():

    # Create a new instance of the Firefox driver
    driver = webdriver.Firefox()

    # Open the webpage
    driver.get("https://coinmetrics.io/community-network-data/")

    # Accept cookies
    accept_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "a.fusion-privacy-bar-acceptance")))
    accept_button.click()

    # Find and select Bitcoin from the dropdown menu
    selector = Select(WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#downloadSelect"))))
    selector.select_by_value("https://raw.githubusercontent.com/coinmetrics/data/master/csv/btc.csv")

    # Click the Download button
    download_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.cm-button")))
    download_button.click()

    # Wait for the download to finish and print the CSV data
    wait_for_download = True
    while wait_for_download:
        for file in os.listdir(os.path.join(os.path.expanduser("~"), "Downloads")):
            if file.endswith(".csv"):
                data = pd.read_csv(os.path.join(os.path.expanduser("~"), "Downloads", file), dtype={146: str})
                print(data)
                wait_for_download = False

    # Close the Firefox window
    driver.quit()

    return None


def update_macro_economic():

    return None

# endregion


def decision_tree_predictor(data_to_regression1):
    update_internal_factors()
    update_yahoo_data()
    update_macro_economic()

    # train model with all data before last Row
    X_train = data_to_regression1[['DiffLast', 'DiffMean', 'CapAct1yrUSD', 'HashRate', 'Open', 'Rate']]
    y_train = data_to_regression1[['Close']]

    # use last row to predict price
    X_test = data_to_regression1[['DiffLast', 'DiffMean', 'CapAct1yrUSD', 'HashRate', 'Open', 'Rate']]
    decision_model = DecisionTreeRegressor(random_state=0)
    decision_model.fit(X_train, y_train)
    predictions_tree = decision_model.predict(X_test).reshape(-1, 1)
    return predictions_tree


data_to_regression = pd.read_csv('data22.csv')
