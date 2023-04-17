from fredapi import Fred
import pandas as pd
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
from database import save_value_to_database


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

    # Save to database
    save_value_to_database('interest_rate', latest_rate)

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


if __name__ == "__main__":
    update_macro_economic()
