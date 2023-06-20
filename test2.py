import pytz
import requests
import pandas as pd
from datetime import datetime, timezone
from database import read_database

DATABASE_PATH = 'data/database.csv'


def get_bitcoin_price(hours):
    """Fetch the last 'hours' of Bitcoin price from the CoinGecko API"""
    response = requests.get(
        'https://api.coingecko.com/api/v3/coins/bitcoin/market_chart',
        params={
            'vs_currency': 'usd',
            'days': str(hours/24),  # Convert hours to days
            'interval': 'hourly'  # Hourly data
        }
    )
    response.raise_for_status()  # Raise an exception if the request failed
    data = response.json()

    # Extract all the prices from the data
    prices = data['prices']

    # Convert the timestamps to datetime objects (UTC time), make them timezone-aware by adding .astimezone(pytz.UTC),
    # and round to nearest hour
    prices_dict = {datetime.fromtimestamp(timestamp / 1000).replace(minute=0, second=0, microsecond=0).astimezone(pytz.UTC): price for timestamp, price in prices}

    # Convert the dictionary to a list of tuples
    prices_list = [(date, price) for date, price in prices_dict.items()]

    return prices_list


def update_bitcoin_price():
    """Update the Bitcoin price in the database"""
    df = pd.read_csv(DATABASE_PATH, index_col='date', parse_dates=['date'])

    # Make the index timezone-aware
    df.index = df.index.tz_localize('UTC')

    # Find the most recent date in the data where 'bitcoin_price' has a value
    latest_date = df['bitcoin_price'].last_valid_index()

    # Calculate the number of hours between the most recent date and now
    now = datetime.now(timezone.utc)
    hours_diff = int((now - latest_date).total_seconds() / 3600)

    # Get the bitcoin price for the last 'hours_diff' hours
    new_data = get_bitcoin_price(hours_diff)

    # Only keep the data that is more recent than 'latest_date'
    new_data = [(date, price) for date, price in new_data if date > latest_date]

    # Convert the new data to a dataframe
    df_new = pd.DataFrame(new_data, columns=["date", "bitcoin_price"]).set_index("date")
    df_new['bitcoin_price'] = df_new['bitcoin_price'].astype(int)

    print('df_new', df_new)

    # Append the new data to the existing data and remove timezone information
    df = pd.concat([df, df_new])
    df.index = df.index.tz_localize(None)

    # Shift the 'bitcoin_price' column 12 hours back to create 'actual_price_12h_later'
    df['actual_price_12h_later'] = df['bitcoin_price'].shift(-12)

    # Save the updated dataframe
    df.to_csv(DATABASE_PATH)

    return df


if __name__ == '__main__':
    update_bitcoin_price()
    df_outer = read_database()
    print(df_outer['bitcoin_price'])
