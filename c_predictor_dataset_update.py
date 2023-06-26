from coinmetrics.api_client import CoinMetricsClient
import pandas as pd
import logging
from datetime import datetime, timedelta
import warnings
from fredapi import Fred
import configparser
import os

from read_write_csv import load_dataset, save_dataset

warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=RuntimeWarning)

config = configparser.ConfigParser()
config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config/config.ini')

with open(config_path, 'r') as f:
    config_string = f.read()

config.read_string(config_string)
API_KEY_FRED = config.get('API', 'freed')


def update_macro_economic():
    """ Connect to FRED API and get the latest federal funds rate data"""
    try:
        fred = Fred(api_key=API_KEY_FRED)
        fred_dataset = fred.get_series('FEDFUNDS')
    except Exception as e:
        logging.error(f"Error: {e}")
        raise Exception("Failed to update macroeconomic data.")

    # Load the main dataset into a DataFrame
    main_dataset = load_dataset()

    # Check if the latest federal funds rate is already in the main dataset
    latest_rate = fred_dataset.iloc[-1]

    if latest_rate == main_dataset['Rate'].iloc[-1]:
        logging.info("interest rate data is already up to date.")
        return

    # Update the last row of the Rate column with the latest federal funds rate data
    main_dataset.iloc[-1]['Rate'] = latest_rate

    # Backward fill missing values with the next non-null value, but only up to the next value change
    main_dataset['Rate'].fillna(method='bfill', limit=30, inplace=True)

    # Print a message indicating that the new rate has been added to the main dataset
    logging.info("interest rate added to the main dataset")

    save_dataset(main_dataset)


def get_date_string(date_obj):
    return date_obj.strftime("%Y-%m-%d")


def update_internal_factors():
    main_dataset = load_dataset()

    # Get the latest date in the main dataset
    latest_date = main_dataset.loc[main_dataset['DiffLast'].last_valid_index()].name

    # Initialize CoinMetricsClient
    client = CoinMetricsClient()

    # Get the latest available data
    end_date = get_date_string(datetime.now() - timedelta(days=1))
    last_value_date = get_date_string(latest_date + timedelta(days=1))
    # Check if the start_date is later than the end_date
    if pd.to_datetime(last_value_date) > pd.to_datetime(end_date):
        logging.info("Dataset is already up to date.")
        return

    # Request the required metrics for Bitcoin
    metric_ids = "DiffLast,DiffMean,CapAct1yrUSD,HashRate,PriceUSD"
    asset_id = "btc"
    response = client.get_asset_metrics(
        assets=asset_id,
        metrics=metric_ids,
        start_time=last_value_date,
        end_time=end_date,
        frequency="1d",
    )

    new_data = response.to_dataframe()

    if len(new_data) > 0:
        new_data = new_data.rename(columns={'time': 'Date'})
        new_data = new_data.rename(columns={'PriceUSD': 'Close'})
        new_data['Date'] = pd.to_datetime(new_data['Date'], unit='s').dt.strftime('%Y-%m-%d')
        new_data['Open'] = new_data['Close'].shift(1)
        new_data.set_index('Date', inplace=True)

        # Convert the index to a datetime index and then to the desired date format
        new_data.index = pd.to_datetime(new_data.index).strftime('%Y-%m-%d')

        for column in new_data.columns:
            if new_data.at[new_data.index[-1], column] == 'btc':
                new_data = new_data.drop(columns=[column])
                break

        # Get last 'Close' value from main_dataset
        last_close = main_dataset['Close'].iloc[-1]

        # Set first 'Open' value in new_data
        new_data['Open'].iloc[0] = last_close

        # Append the new rows to the main dataset
        main_dataset = pd.concat([main_dataset, new_data])

        # Fix the format of the index

        main_dataset.index = pd.to_datetime(main_dataset.index).date

        # Write the updated dataset to disk
        main_dataset.index.name = 'Date'

        save_dataset(main_dataset)

        logging.info(f"{len(new_data)} new rows of internal factors added.")
    else:
        logging.info("Internal factors are already up to date.")


if __name__ == "__main__":
    update_internal_factors()
