from fredapi import Fred
import pandas as pd
import yfinance as yf
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
import os
import time


# region A. update factors


def update_internal_factors():
    # Read the main dataset from disk
    main_dataset = pd.read_csv('main_dataset.csv', dtype={146: str})

    # Get the latest date in the main dataset
    latest_date = main_dataset['Date'].max()

    # Create a new instance of the Firefox driver
    driver = webdriver.Firefox()

    # Open the webpage
    driver.get("https://coinmetrics.io/community-network-data/")

    # Accept cookies
    accept_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "a.fusion-privacy-bar-acceptance")))
    accept_button.click()

    # Find and select Bitcoin from the dropdown menu
    time.sleep(4)
    selector = Select(WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#downloadSelect"))))
    selector.select_by_value("https://raw.githubusercontent.com/coinmetrics/data/master/csv/btc.csv")

    # Click the Download button
    download_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.cm-button")))
    download_button.click()

    # Wait for the download to finish and read the new data
    wait_for_download = True
    new_data = None
    while wait_for_download:
        for file in os.listdir(os.path.join(os.path.expanduser("~"), "Downloads")):
            if file.endswith(".csv"):
                new_data = pd.read_csv(os.path.join(os.path.expanduser("~"), "Downloads", file), dtype={146: str})
                wait_for_download = False
                break

    # Close the Firefox window
    driver.quit()

    if new_data is not None:
        # Rename the 'time' column to 'Date'
        new_data = new_data.rename(columns={'time': 'Date'})

        # Filter the new data to only include rows with a date after the latest date in the main dataset
        new_data = new_data[new_data['Date'] > latest_date]

        if len(new_data) > 0:
            # Append the new rows to the main dataset
            main_dataset = pd.concat([main_dataset, new_data])

            # Write the updated dataset to disk
            main_dataset.to_csv('main_dataset.csv', index=False)

            print(f"{len(new_data)} new rows of internal factors added.")
        else:
            print("internal factors is already up to date.")
    else:
        print("Error: Failed to download internal factors.")

    return None


def update_yahoo_data():
    # Read the main dataset from disk
    main_dataset = pd.read_csv('main_dataset.csv', dtype={146: str})

    # Get the latest date in the main dataset
    latest_date = main_dataset['Date'].max()

    # Download the new data from Yahoo Finance
    ticker = yf.Ticker("BTC-USD")
    new_data = ticker.history(period="max")

    if new_data is not None:
        # Filter the new data to only include rows with a date after the latest date in the main dataset
        new_data = new_data[new_data.index > latest_date]

        if len(new_data) > 0:
            # Append the new rows to the main dataset
            new_rows = new_data[['Open', 'High', 'Low', 'Close']].reset_index().rename(columns={'Date': 'Date'})
            main_dataset = pd.concat([main_dataset, new_rows])

            # Write the updated dataset to disk
            main_dataset.to_csv('main_dataset.csv', index=False)

            print(f"{len(new_rows)} new rows of yahoo data added.")
        else:
            print("Yahoo data is already up to date.")
    else:
        print("Error: Failed to download new data of yahoo data.")

    return None


def update_macro_economic():
    # Connect to FRED API and get the latest federal funds rate data
    try:
        fred = Fred(api_key='8f7cbcbc1210c7efa87ee9484e159c21')
        df2 = fred.get_series('FEDFUNDS')
    except Exception as e:
        print(f"Error: {e}")
        return

    # Load the main dataset into a DataFrame
    main_dataset = pd.read_csv('main_dataset.csv')

    # Check if the latest federal funds rate is already in the main dataset
    latest_rate = df2.iloc[-1]
    if latest_rate == main_dataset['Rate'].iloc[-1]:
        print("interest rate data is already up to date.")
        return

    # Update the last row of the Rate column with the latest federal funds rate data
    main_dataset.loc[main_dataset.index[-1], 'Rate'] = latest_rate

    # Backward fill missing values with the next non-null value, but only up to the next value change
    main_dataset['Rate'].fillna(method='bfill', limit=1, inplace=True)

    # Print a message indicating that the new rate has been added to the main dataset
    print("interest rate added to the main dataset.")

    # Save the updated main dataset to a CSV file
    main_dataset.to_csv('main_dataset.csv', index=False)


# endregion


def decision_tree_predictor():
    update_internal_factors()
    update_yahoo_data()
    update_macro_economic()
    # consider the last day have close also ( so do not use it for train)
    # train model with all data before last Row
    #X_train = dataset[['DiffLast', 'DiffMean', 'CapAct1yrUSD', 'HashRate', 'Open', 'Rate']]
    #y_train = dataset[['Close']]

    # use last row to predict price
    #X_test = dataset[['DiffLast', 'DiffMean', 'CapAct1yrUSD', 'HashRate', 'Open', 'Rate']]
    #decision_model = DecisionTreeRegressor(random_state=0)
    #decision_model.fit(X_train, y_train)
    #predictions_tree = decision_model.predict(X_test).reshape(-1, 1)
    return None#predictions_tree


