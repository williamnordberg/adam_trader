import pandas as pd
import yfinance as yf
from datetime import datetime


def update_yahoo_data():
    # Read the main dataset from disk
    main_dataset = pd.read_csv('main_dataset.csv', dtype={146: str})

    # Get the latest date in the main dataset
    latest_date = main_dataset.loc[main_dataset['Open'].last_valid_index(), 'Date']

    # Set the end date to today
    end_date = datetime.today().strftime('%Y-%m-%d')

    # Download the new data from Yahoo Finance
    ticker = yf.Ticker("BTC-USD")
    new_data = ticker.history(start=latest_date, end=end_date)

    new_data.index = new_data.index.strftime('%Y-%m-%d')
    new_data['Date'] = new_data.index

    if new_data is not None:
        print(f"{len(new_data)} new rows of yahoo data added.")
        # Update main dataset with new data
        for date, open_value, close_value in new_data[['Date', 'Open', 'Close']].values:
            # Check if date already exists in main dataset
            if date in main_dataset['Date'].tolist():
                # Update the corresponding row in the main dataset
                main_dataset.loc[main_dataset['Date'] == date, ['Open', 'Close']] = [open_value, close_value]
            else:
                # Append a new row to the main dataset
                new_row = pd.DataFrame([[date, open_value, close_value]], columns=['Date', 'Open', 'Close'])
                main_dataset = pd.concat([main_dataset, new_row], ignore_index=True)

    else:
        print("Yahoo data is already up to date.")
    return None


update_yahoo_data()