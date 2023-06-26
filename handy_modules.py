import requests
import logging
from typing import Tuple
import pandas as pd
from functools import wraps
from time import sleep
import plotly.graph_objects as go
import pandas.errors

from datetime import datetime, timedelta
from database import read_database
from binance.exceptions import BinanceAPIException, BinanceRequestException
from testnet_future_short_trade import initialized_future_client


BINANCE_ENDPOINT_PRICE = "https://api.binance.com/api/v3/ticker/price"
GECKO_ENDPOINT_PRICE = 'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd'
LATEST_INFO_FILE = "data/latest_info_saved.csv"
SYMBOL = 'BTCUSDT'
TRADE_RESULT_PATH = 'data/trades_results.csv'
TRADE_DETAILS_PATH = 'data/trades_details.csv'

COLORS = {
    'red_chart': '#ca3f64',
    'green_chart': '#25a750',
    'white': '#FFFFFF',
    'black': '#000000',
    'lightgray': '#545454',
    'gray_text': '#fff',
    'background': '#000000',
    'black_chart': '#141414'
}

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def read_fed_announcement() -> str:
    latest_info_saved = pd.read_csv(LATEST_INFO_FILE)
    value = str(latest_info_saved.iloc[0]['next-fed-announcement'])
    return value


time_to_announce = datetime.strptime(read_fed_announcement(), '%Y-%m-%d %H:%M:%S')

update_intervals = {
    "dataset": timedelta(hours=24),
    "macro": timedelta(hours=1) if datetime.now() <= time_to_announce else timedelta(hours=24),
    "order_book": timedelta(minutes=10),
    "predicted_price": timedelta(hours=12),
    "technical_analysis": timedelta(hours=4),
    "richest_addresses": timedelta(minutes=20),
    "google_search": timedelta(hours=3),
    "reddit": timedelta(hours=8),
    "youtube": timedelta(hours=4),
    "sentiment_of_news": timedelta(hours=1),
    "richest_addresses_scrap": timedelta(hours=12),
    "weighted_score": timedelta(minutes=10),
}


def retry_on_error_fallback_0_0(max_retries: int = 3, delay: int = 5, allowed_exceptions: tuple = ()):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except allowed_exceptions as e:
                    retries += 1
                    logging.warning(f"Attempt {retries} failed with error: {e}. Retrying in {delay} seconds...")
                    sleep(delay)
            logging.error(f"All {max_retries} attempts failed. Returning fallback values (0, 0).")
            return 0, 0

        return wrapper

    return decorator


def retry_on_error(max_retries: int = 3, delay: int = 5,
                   allowed_exceptions: tuple = (), fallback_values=None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except allowed_exceptions as e:
                    retries += 1
                    logging.warning(f"Attempt {retries} failed with error: {e}. Retrying in {delay} seconds...")
                    sleep(delay)
            logging.error(f"All {max_retries} attempts failed.")
            if fallback_values is not None:
                if fallback_values == "pass":
                    logging.error("Fallback value is 'pass'. Skipping this function.")
                    return
                else:
                    logging.error(f"Returning fallback values {fallback_values}.")
                    return fallback_values
            else:
                raise Exception(f"All {max_retries} attempts failed without a fallback value.")

        return wrapper

    return decorator


@retry_on_error(max_retries=3, delay=5, allowed_exceptions=(
        requests.ConnectionError,), fallback_values=False)
def check_internet_connection() -> bool:
    """
    Check if there is an internet connection.

    Returns:
        bool: True if there is an internet connection, False otherwise.
    """
    try:
        requests.get("http://www.google.com", timeout=5)
        return True
    except (requests.ConnectionError, requests.exceptions.Timeout, requests.exceptions.ReadTimeout):
        logging.warning("No internet connection available.")
        return False


def get_bitcoin_future_market_price() -> int:
    while True:
        if check_internet_connection():
            client = initialized_future_client()
            try:
                ticker = client.futures_ticker(symbol=SYMBOL)
                current_price = int(float(ticker['lastPrice']))
                return current_price
            except (BinanceAPIException, BinanceRequestException) as e:
                logging.error(f"Error: Could not connect to Binance API:{e}")
        else:
            logging.error("No internet connection.")
        logging.error('Sleep 61 Sec and try again to retrieve Bitcoin price')
        sleep(61)  # wait for 61 seconds before retrying


def get_bitcoin_price() -> int:
    """
    Retrieves the current Bitcoin price in USD from the CoinGecko API and Binance API.
    Continuously retries until a valid price is obtained.

    Returns:
        Int: The current Bitcoin price in USD or None if an error occurred.
    """
    while True:
        if check_internet_connection():
            try:
                response = requests.get(GECKO_ENDPOINT_PRICE)
                if response.status_code == 200:
                    data = response.json()
                    current_price = int(data['bitcoin']['usd'])
                    return current_price
            except requests.exceptions.RequestException as e:
                logging.error(f"Error: Could not connect to CoinGecko API:{e}")

            try:
                response = requests.get(BINANCE_ENDPOINT_PRICE, params={'symbol': 'BTCUSDT'})
                if response.status_code == 200:
                    return int(float(response.json()['price']))
            except requests.exceptions.RequestException as e:
                logging.error(f"Error: Could not connect to Binance API:{e}")
        else:
            logging.error("No internet connection.")
        logging.error(f"Error: Could not retrieve BTC price, Sleep for 61 seconds ")
        sleep(61)  # wait for 61 seconds before retrying


def richest_addresses_() -> Tuple[float, float]:
    database = read_database()
    richest_addresses_bullish = database['richest_addresses_bullish'][-1]
    richest_addresses_bearish = database['richest_addresses_bearish'][-1]
    return richest_addresses_bullish, richest_addresses_bearish


def should_update(factor: str) -> bool:
    latest_info_saved = pd.read_csv(LATEST_INFO_FILE)
    last_update_time_str = latest_info_saved.iloc[0][f'latest_{factor}_update']
    last_update_time = datetime.strptime(last_update_time_str, '%Y-%m-%d %H:%M:%S')

    return datetime.now() - last_update_time > update_intervals[factor]


def save_update_time(factor_name: str):
    """
    save update time

    Args:
        factor_name (str): the factor that get updated

    """

    latest_info_saved = pd.read_csv(LATEST_INFO_FILE)
    latest_info_saved.loc[0, f'latest_{factor_name}_update'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    latest_info_saved.to_csv(LATEST_INFO_FILE, index=False)


def save_trading_state(state: str):
    latest_info_saved = pd.read_csv(LATEST_INFO_FILE)
    latest_info_saved.loc[0, 'latest_trading_state'] = state
    latest_info_saved.to_csv(LATEST_INFO_FILE, index=False)


def read_current_trading_state() -> str:
    latest_info_saved = pd.read_csv(LATEST_INFO_FILE)
    state = latest_info_saved.iloc[0]['latest_trading_state']
    return state


def save_float_to_latest_saved(column: str, value: float):
    latest_info_saved = pd.read_csv(LATEST_INFO_FILE)
    latest_info_saved.loc[0, f'{column}'] = round(value, 2)
    latest_info_saved.to_csv(LATEST_INFO_FILE, index=False)


def save_int_to_latest_saved(column: str, value: int):
    latest_info_saved = pd.read_csv(LATEST_INFO_FILE)
    latest_info_saved.loc[0, f'{column}'] = value
    latest_info_saved.to_csv(LATEST_INFO_FILE, index=False)


def read_float_from_latest_saved(column: str) -> float:
    latest_info_saved = pd.read_csv(LATEST_INFO_FILE)
    retrieved_value = latest_info_saved.iloc[0][f'{column}']
    latest_info_saved.to_csv(LATEST_INFO_FILE, index=False)
    return float(retrieved_value)


def save_trade_details(weighted_score, position_opening_time, position_closing_time,
                       position_type, opening_price, close_price, pnl, factor_values):

    # Read the existing trade details CSV
    df = pd.read_csv(TRADE_DETAILS_PATH)

    # Create a new row with the provided trade details
    new_row = {
        'weighted_score': weighted_score,
        'position_opening_time': position_opening_time,
        'position_closing_time': position_closing_time,
        'position_type': position_type,
        'opening_price': opening_price,
        'close_price': close_price,
        'PNL': pnl,
        'macro_bullish': factor_values['macro_bullish'],
        'macro_bearish': factor_values['macro_bearish'],
        'order_book_bullish': factor_values['order_book_bullish'],
        'order_book_bearish': factor_values['order_book_bearish'],
        'prediction_bullish': factor_values['prediction_bullish'],
        'prediction_bearish': factor_values['prediction_bearish'],
        'technical_bullish': factor_values['technical_bullish'],
        'technical_bearish': factor_values['technical_bearish'],
        'richest_bullish': factor_values['richest_bullish'],
        'richest_bearish': factor_values['richest_bearish'],
        'google_bullish': factor_values['google_bullish'],
        'google_bearish': factor_values['google_bearish'],
        'reddit_bullish': factor_values['reddit_bullish'],
        'reddit_bearish': factor_values['reddit_bearish'],
        'youtube_bullish': factor_values['youtube_bullish'],
        'youtube_bearish': factor_values['youtube_bearish'],
        'news_bullish': factor_values['news_bullish'],
        'news_bearish': factor_values['news_bearish'],
        'weighted_score_up': factor_values['weighted_score_up'],
        'weighted_score_down': factor_values['weighted_score_down']
    }

    # Use a list to store new rows
    new_rows = [new_row]

    # Create a new DataFrame from the list of new rows
    df_new = pd.DataFrame(new_rows)

    # Concatenate the new DataFrame with the original DataFrame
    df = pd.concat([df, df_new], ignore_index=True)

    # Save the updated DataFrame to the CSV file
    df.to_csv(TRADE_DETAILS_PATH, index=False)


def save_trade_result(pnl: float, weighted_score: float, trade_type: str):
    df = pd.read_csv(TRADE_RESULT_PATH)

    if 0.65 <= weighted_score < 0.70:
        weighted_score_category = '65to70'
    elif 0.70 <= weighted_score < 0.75:
        weighted_score_category = '70to75'
    elif 0.75 <= weighted_score < 0.80:
        weighted_score_category = '75to80'
    else:
        weighted_score_category = '80to100'

    # Locate the row with the specific model_name
    row_index = df[df['weighted_score_category'] == weighted_score_category].index[0]

    # Update the number_of_trades and PNL values for the specific model
    df.loc[row_index, 'total_trades'] += 1
    df.loc[row_index, 'PNL'] += pnl

    if trade_type == 'short':
        df.loc[row_index, 'short_trades'] += 1
    else:
        df.loc[row_index, 'long_trades'] += 1

    if pnl >= 0:
        df.loc[row_index, 'win_trades'] += 1
    else:
        df.loc[row_index, 'loss_trades'] += 1

    # Save the updated DataFrame to the CSV file
    df.to_csv(TRADE_RESULT_PATH, index=False)


def calculate_score_margin(weighted_score):
    if 0.65 <= weighted_score < 0.70:
        return 0.65
    elif 0.70 <= weighted_score < 0.75:
        return 0.68
    elif 0.75 <= weighted_score < 0.80:
        return 0.7
    else:
        return 0.65


@retry_on_error(max_retries=3, delay=5, allowed_exceptions=(
        pandas.errors.EmptyDataError, Exception), fallback_values=('0', '0'))
def last_and_next_update(factor: str) -> Tuple[str, str]:
    latest_info_saved = pd.read_csv(LATEST_INFO_FILE)
    last_update_time_str = latest_info_saved.iloc[0][f'latest_{factor}_update']
    last_update_time = datetime.strptime(last_update_time_str, '%Y-%m-%d %H:%M:%S')

    # Calculate the time difference between now and the last update time
    time_since_last_update = datetime.now() - last_update_time

    # If the time since last update is more than 1 hour, convert it to hours
    if time_since_last_update.total_seconds() > 3600:
        time_since_last_update_str = f'{int(time_since_last_update.total_seconds() // 3600)}h'
    else:  # else, convert it to minutes
        time_since_last_update_str = f'{int(time_since_last_update.total_seconds() // 60)}m'

    if update_intervals[factor] < time_since_last_update:
        next_update = timedelta(seconds=0)  # equivalent to zero
    else:
        next_update = update_intervals[factor] - time_since_last_update

    # Similar conversion for next update
    if next_update.total_seconds() > 3600:
        next_update_str = f'{int(next_update.total_seconds() // 3600)}h'
    else:
        next_update_str = f'{int(next_update.total_seconds() // 60)}m'

    return time_since_last_update_str, next_update_str


def create_gauge_chart(bullish, bearish, factor):
    last_update_time_str, next_update_str = last_and_next_update(factor)

    if bullish == 0 and bearish == 0:
        value = 0
        gauge_steps = [
            {"range": [0, 1], "color": COLORS['lightgray']},
        ]
        bar_thickness = 0
        mode_str = "gauge"
        number = {}

    else:
        value = round(((bullish / (bullish + bearish)) * 1), 2)
        gauge_steps = [
            {"range": [0, 1], "color": COLORS['red_chart']}
        ]
        bar_thickness = 1

        mode_str = "gauge+number"
        if factor == 'weighted_score':
            if value >= 0.55:
                number = {"font": {"size": 26, "color": COLORS['green_chart']}}
            elif value <= 0.45:
                number = {"font": {"size": 26, "color": COLORS['red_chart']}}
            else:
                number = {"font": {"size": 26, "color": COLORS['white']}}
        else:
            number = {"font": {"size": 12, "color": COLORS['white']}}
    return go.Indicator(
        mode=mode_str,
        value=value,
        title={
            "text": f"L: {last_update_time_str}   N: {next_update_str}",
            "font": {"size": 12, "color": COLORS['lightgray']}
        },
        domain={"x": [0, 1], "y": [0, 1]},
        gauge={
            "axis": {"range": [0, 1], "showticklabels": False},
            "bar": {"color": COLORS['green_chart'], "thickness": bar_thickness},
            "steps": gauge_steps,
            "bgcolor": COLORS['black']
        },
        number=number,
    )


def read_time_last_update_time_difference(column: str) -> timedelta:
    latest_info_saved = pd.read_csv(LATEST_INFO_FILE).squeeze("columns")
    last_news_sentiment_str = latest_info_saved.iloc[0][f'{column}']
    last_news_sentiment = datetime.strptime(last_news_sentiment_str, '%Y-%m-%d %H:%M:%S')
    last_update_time_difference = datetime.now() - last_news_sentiment
    return last_update_time_difference


if __name__ == '__main__':
    print('')
