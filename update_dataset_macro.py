from fredapi import Fred
import pandas as pd
import logging
import configparser
import os
from handy_modules import retry_on_error


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# Load the config file
config = configparser.ConfigParser()
config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.ini')

with open(config_path, 'r') as f:
    config_string = f.read()

config.read_string(config_string)
API_KEY_FRED = config.get('API', 'freed')


@retry_on_error(max_retries=3, delay=5)
def update_macro_economic():
    """ Connect to FRED API and get the latest federal funds rate data"""
    try:
        fred = Fred(api_key=API_KEY_FRED)
        fred_dataset = fred.get_series('FEDFUNDS')
    except Exception as e:
        logging.error(f"Error: {e}")
        raise Exception("Failed to update macroeconomic data.")

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
    logging.info("interest rate added to the main dataset")

    # Save the updated main dataset to a CSV file
    main_dataset.to_csv('main_dataset.csv', index=False)


if __name__ == "__main__":
    update_macro_economic()
