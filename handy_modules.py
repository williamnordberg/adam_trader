import requests
import logging
from typing import Tuple
import pandas as pd
import time
from functools import wraps

from datetime import datetime, timedelta
from database import read_database, save_value_to_database

BINANCE_ENDPOINT_PRICE = "https://api.binance.com/api/v3/ticker/price"
GECKO_ENDPOINT_PRICE = 'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd'
LATEST_INFO_FILE = "latest_info_saved.csv"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

update_intervals = {
    "dataset": timedelta(hours=24),
    "macro": timedelta(hours=24),
    "order_book": timedelta(minutes=20),
    "predicted_price": timedelta(hours=12),
    "technical_analysis": timedelta(hours=12),
    "richest_addresses_compare": timedelta(hours=3),
    "google_search": timedelta(hours=3),
    "reddit": timedelta(hours=3),
    "youtube": timedelta(hours=3),
    "sentiment_of_news": timedelta(hours=1),
}


def retry_on_error(max_retries: int = 3, delay: int = 5, allowed_exceptions: tuple = ()):
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
                    time.sleep(delay)
            logging.error(f"All {max_retries} attempts failed. Returning fallback values (0, 0).")
            return 0, 0
        return wrapper
    return decorator


def retry_on_error_with_fallback(max_retries: int = 3, delay: int = 5,
                                 allowed_exceptions: tuple = (), fallback_values=(0, 0, 0, 0)):
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
                    time.sleep(delay)
            logging.error(f"All {max_retries} attempts failed. Returning fallback values {fallback_values}.")
            return fallback_values
        return wrapper
    return decorator


@retry_on_error(max_retries=3, delay=5, allowed_exceptions=(requests.ConnectionError,))
def check_internet_connection() -> bool:
    """
    Check if there is an internet connection.

    Returns:
        bool: True if there is an internet connection, False otherwise.
    """
    try:
        with requests.get("http://www.google.com", timeout=3) as response:
            return True
    except requests.ConnectionError:
        logging.warning("No internet connection available.")
        return False


@retry_on_error(max_retries=3, delay=5, allowed_exceptions=(requests.exceptions.RequestException,))
def get_bitcoin_price() -> int:
    """
    Retrieves the current Bitcoin price in USD from the CoinGecko API and Binance API.

    Returns:
        Int: The current Bitcoin price in USD or 0 if an error occurred.
    """
    if check_internet_connection():
        errors = []

        try:
            response = requests.get(GECKO_ENDPOINT_PRICE)
            if response.status_code == 200:
                data = response.json()
                current_price = int(data['bitcoin']['usd'])
                return current_price
        except requests.exceptions.RequestException as e:
            errors.append(f"Error: Could not connect to CoinGecko API:{e}")

        try:
            response = requests.get(BINANCE_ENDPOINT_PRICE, params={'symbol': 'BTCUSDT'})
            if response.status_code == 200:
                return int(float(response.json()['price']))
        except requests.exceptions.RequestException as e:
            errors.append(f"Error: Could not connect to Binance API:{e}")

        if errors:
            for error in errors:
                logging.error(error)

        return 0
    # no internet connection
    else:
        return 0


def compare_predicted_price(predicted_price: int, current_price: int) -> Tuple[float, float]:
    """
    Compare the predicted price to the current price and calculate the percentage difference.

    Args:
        predicted_price (int): The predicted price of Bitcoin.
        current_price (int): The current price of Bitcoin.

    Returns:
        tuple: bullish and bearish probabilities based on the price difference percentage.
    """
    activity_percentage = (predicted_price - current_price) / current_price * 100

    if activity_percentage > 0:
        if activity_percentage >= 5:
            return 1, 0
        elif activity_percentage >= 4:
            return 0.9, 0.1
        elif activity_percentage >= 3:
            return 0.8, 0.2
        elif activity_percentage >= 2:
            return 0.7, 0.3
        elif activity_percentage >= 1:
            return 0.6, 0.4
    elif activity_percentage <= 0:
        if activity_percentage <= -5:
            return 0, 1
        elif activity_percentage <= -4:
            return 0.1, 0.9
        elif activity_percentage <= -3:
            return 0.2, 0.8
        elif activity_percentage <= -2:
            return 0.3, 0.7
        elif activity_percentage <= -1:
            return 0.4, 0.6

    return 0, 0


def compare_google_search_trends(last_hour: int, two_hours_before: int) -> Tuple[float, float]:
    """
    Compare the search trends between the last hour and two hours before.

    Args:
        last_hour (int): The search volume of the last hour.
        two_hours_before (int): The search volume of two hours before the last hour.

    Returns:
        tuple: bullish and bearish probabilities based on the search trends.
    """
    if last_hour >= two_hours_before:
        if last_hour >= (two_hours_before * 1.8):
            return 1, 0
        elif last_hour >= (two_hours_before * 1.6):
            return 0.85, 0.15
        elif last_hour >= (two_hours_before * 1.35):
            return 0.75, 0.25
        elif last_hour >= (two_hours_before * 1.2):
            return 0.6, 0.4
        return 0, 0

    elif last_hour <= two_hours_before:
        if two_hours_before >= (last_hour * 1.8):
            return 0, 1
        elif two_hours_before >= (last_hour * 1.6):
            return 0.15, 0.85
        elif two_hours_before >= (last_hour * 1.35):
            return 0.25, 0.75
        elif two_hours_before >= (last_hour * 1.2):
            return 0.4, 0.6
        return 0, 0

    return 0, 0


def compare_send_receive_richest_addresses_wrapper() -> Tuple[float, float]:
    latest_info_saved = pd.read_csv('latest_info_saved.csv')
    total_received = latest_info_saved['total_received_coins_in_last_24'][0]
    total_sent = latest_info_saved['total_sent_coins_in_last_24'][0]

    # Save latest update time
    save_update_time('richest_addresses_compare')

    activity_percentage = (total_received - total_sent) / total_sent * 100

    if activity_percentage > 0:
        if activity_percentage >= 50:
            return 1, 0
        elif activity_percentage >= 40:
            return 0.9, 0.1
        elif activity_percentage >= 30:
            return 0.8, 0.2
        elif activity_percentage >= 20:
            return 0.7, 0.3
        elif activity_percentage >= 10:
            return 0.6, 0.4

    elif activity_percentage <= 0:
        if activity_percentage <= -50:
            return 0, 1
        elif activity_percentage <= -40:
            return 0.1, 0.9
        elif activity_percentage <= -30:
            return 0.2, 0.8
        elif activity_percentage <= -20:
            return 0.3, 0.7
        elif activity_percentage <= -10:
            return 0.4, 0.6

    return 0, 0


def compare_send_receive_richest_addresses() -> Tuple[float, float]:
    if should_update('richest_addresses_compare'):
        richest_addresses_bullish, richest_addresses_bearish = compare_send_receive_richest_addresses_wrapper()

        # Save to database
        save_value_to_database('richest_addresses_bullish', richest_addresses_bullish)
        save_value_to_database('richest_addresses_bearish', richest_addresses_bearish)

        return richest_addresses_bullish, richest_addresses_bearish
    else:
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
    latest_info_saved = pd.read_csv(LATEST_INFO_FILE)
    latest_info_saved.loc[0, f'latest_{factor_name}_update'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    latest_info_saved.to_csv(LATEST_INFO_FILE, index=False)


if __name__ == '__main__':
    logging.info(f'bitcoin price: {get_bitcoin_price()}')

    predicted_bullish, predicted_bearish = compare_predicted_price(200, 198)
    logging.info(f'predicted_bullish: {predicted_bullish}, predicted_bearish: {predicted_bearish} ')

    google_bullish, google_bearish = compare_google_search_trends(10, 13)
    logging.info(f'google_bullish: {google_bullish}, google_bearish: {google_bearish} ')
