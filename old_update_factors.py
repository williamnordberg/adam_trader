from selenium.common import TimeoutException
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
from datetime import datetime
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def update_internal_factors():
    # Read the main dataset from disk
    main_dataset = pd.read_csv('main_dataset.csv', dtype={146: str})

    # Get the latest date in the main dataset

    latest_date = main_dataset.loc[main_dataset['DiffLast'].last_valid_index(), 'Date']

    # Create a new instance of the Firefox driver
    driver = webdriver.Firefox()

    # Open the webpage
    driver.get("https://coinmetrics.io/community-network-data/")

    # Check if the accept button for cookies is present
    try:
        accept_button = WebDriverWait(driver, 7).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a.fusion-privacy-bar-acceptance")))
        accept_button.click()
    except TimeoutException:
        pass

    # Find and select Bitcoin from the dropdown menu
    time.sleep(4)
    selector = Select(WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#downloadSelect"))))
    selector.select_by_value("https://raw.githubusercontent.com/coinmetrics/data/master/csv/btc.csv")

    # Click the Download button
    download_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.cm-button")))
    download_button.click()
    time.sleep(2)

    # Wait for the download to finish
    wait_for_download = True
    new_data = None  # Initialize new_data as None
    while wait_for_download:
        # Get a list of all files in the Downloads folder, sorted by creation time (new first)
        files = sorted(os.listdir(os.path.join(os.path.expanduser("~"), "Downloads")),
                       key=lambda x: os.path.getctime(os.path.join(os.path.expanduser("~"), "Downloads", x)),
                       reverse=True)
        for file in files:
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
        new_data = new_data[['Date', 'DiffLast', 'DiffMean', 'CapAct1yrUSD', 'HashRate']]
        if len(new_data) > 0:

            # check if new data have a same date row with main_dataset
            if main_dataset['Date'].iloc[-1] == new_data['Date'].iloc[0]:
                # drop the last row in main datasett
                main_dataset = main_dataset.drop(main_dataset.index[-1])

            # Append the new rows to the main dataset
            main_dataset = pd.concat([main_dataset, new_data])

            # Write the updated dataset to disk
            main_dataset.to_csv('main_dataset.csv', index=False)

            logging.info(f"{len(new_data)} new rows of internal factors added.")
        else:
            logging.info("internal factors is already up to date.")
    else:
        logging.error("Failed to download internal factors.")

    return None


def update_yahoo_data():
    # Read the main dataset from disk
    main_dataset = pd.read_csv('main_dataset.csv', dtype={146: str})
    latest_date = main_dataset.loc[main_dataset['Open'].last_valid_index(), 'Date']
    end_date = datetime.today().strftime('%Y-%m-%d')

    # Download the new data from Yahoo Finance
    ticker = yf.Ticker("BTC-USD")
    new_data = ticker.history(start=latest_date, end=end_date)

    new_data.index = new_data.index.strftime('%Y-%m-%d')
    new_data['Date'] = new_data.index

    # check if the dataset is already update
    if latest_date == new_data['Date'].iloc[-1]:
        logging.info('Yahoo data is already update')
        return None

    if new_data is not None:
        logging.info(f"{len(new_data)} new rows of yahoo data added.")
        # Update main dataset with new data
        for date, open_value, close_value in new_data[['Date', 'Open', 'Close']].values:
            # Check if date already exists in main dataset
            if date in main_dataset['Date'].tolist():
                # Update the corresponding row in the main dataset
                main_dataset.loc[main_dataset['Date'] == date, ['Open', 'Close']] = [open_value, close_value]
    else:
        logging.info("Yahoo data is already up to date.")
    main_dataset.to_csv('main_dataset.csv', index=False)
    return None


def update_macro_economic():
    # Connect to FRED API and get the latest federal funds rate data
    try:
        fred = Fred(api_key='8f7cbcbc1210c7efa87ee9484e159c21')
        fred_dataset = fred.get_series('FEDFUNDS')
    except Exception as e:
        logging.error(f"Error: {e}")
        return

    # Load the main dataset into a DataFrame
    main_dataset = pd.read_csv('main_dataset.csv', dtype={146: str})

    # Check if the latest federal funds rate is already in the main dataset
    latest_rate = fred_dataset.iloc[-1]
    latest_date_in_main_dataset = main_dataset.loc[main_dataset['Close'].last_valid_index(), 'Date']

    if latest_rate == main_dataset['Rate'].iloc[-1]:
        logging.info("interest rate data is already up to date.")
        return
    # Update the last row of the Rate column with the latest federal funds rate data
    main_dataset.loc[main_dataset['Date'] == latest_date_in_main_dataset, 'Rate'] = latest_rate

    # Backward fill missing values with the next non-null value, but only up to the next value change
    main_dataset['Rate'].fillna(method='bfill', limit=30, inplace=True)

    # Print a message indicating that the new rate has been added to the main dataset
    logging.info("interest rate added to the main dataset.")

    # Save the updated main dataset to a CSV file
    main_dataset.to_csv('main_dataset.csv', index=False)