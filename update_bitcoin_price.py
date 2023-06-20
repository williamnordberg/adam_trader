import pytz
import requests
import pandas as pd
from datetime import datetime, timezone
from handy_modules import retry_on_error_with_fallback


DATABASE_PATH = 'data/database.csv'
API_URL = 'https://api.coingecko.com/api/v3/coins/bitcoin/market_chart'
ALLOWED_EXCEPTIONS = (requests.exceptions.RequestException, ValueError)


@retry_on_error_with_fallback(max_retries=3, delay=5,
                              allowed_exceptions=ALLOWED_EXCEPTIONS, fallback_values='pass')
def get_bitcoin_price(hours):
    response = requests.get(
        API_URL,
        params={
            'vs_currency': 'usd',
            'days': str(hours/24),
            'interval': 'hourly'
        }
    )
    response.raise_for_status()
    data = response.json()
    prices = data['prices']
    prices_dict = {datetime.fromtimestamp(timestamp / 1000).replace(minute=0, second=0, microsecond=0).astimezone(pytz.UTC): price for timestamp, price in prices}
    prices_list = [(date, price) for date, price in prices_dict.items()]

    return prices_list


def update_bitcoin_price_in_database():
    df = pd.read_csv(DATABASE_PATH, index_col='date', parse_dates=['date'])
    df.index = df.index.tz_localize('UTC')

    latest_date = df['bitcoin_price'].last_valid_index()
    now = datetime.now(timezone.utc)
    hours_diff = int((now - latest_date).total_seconds() / 3600)

    new_data = get_bitcoin_price(hours_diff)
    new_data = [(date, price) for date, price in new_data if date > latest_date]

    df_new = pd.DataFrame(new_data, columns=["date", "bitcoin_price"]).set_index("date")
    df_new['bitcoin_price'] = df_new['bitcoin_price'].astype(int)

    df.update(df_new)
    df.index = df.index.tz_localize(None)
    df['actual_price_12h_later'] = df['bitcoin_price'].shift(-12)

    df.to_csv(DATABASE_PATH)

    return df


if __name__ == '__main__':
    df_outer = update_bitcoin_price_in_database()
    print(df_outer['bitcoin_price'])
