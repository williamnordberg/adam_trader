import pandas as pd
import yfinance as yf
from datetime import datetime
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def update_yahoo_data():
    # Read the main dataset from disk
    main_dataset = pd.read_csv('main_dataset.csv', dtype={146: str})
    latest_date = main_dataset.loc[main_dataset['Open'].last_valid_index(), 'Date']
    end_date = datetime.today().strftime('%Y-%m-%d')

    # Download the new data from Yahoo Finance
    ticker = yf.Ticker("BTC-USD")
    new_data = ticker.history(start=latest_date, end=end_date)

    new_data.index = new_data.index.to_series().dt.strftime('%Y-%m-%d')
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


if __name__ == "__main__":
    update_yahoo_data()
