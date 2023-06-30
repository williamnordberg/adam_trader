import requests
import logging
from functools import wraps
from time import sleep
from json import JSONDecodeError
from binance.exceptions import BinanceAPIException, BinanceRequestException

from l_position_short_testnet import initialized_future_client


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

BINANCE_ENDPOINT_PRICE = "https://api.binance.com/api/v3/ticker/price"
GECKO_ENDPOINT_PRICE = 'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd'
SYMBOL = 'BTCUSDT'


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


@retry_on_error(max_retries=3, delay=5, allowed_exceptions=(
        requests.exceptions.RequestException, requests.exceptions.Timeout,
        requests.exceptions.RequestException, requests.exceptions.Timeout,
        ValueError, KeyError, JSONDecodeError), fallback_values=0)
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


@retry_on_error(max_retries=3, delay=5, allowed_exceptions=(
        requests.exceptions.RequestException, requests.exceptions.Timeout,
        requests.exceptions.RequestException, requests.exceptions.Timeout,
        ValueError, KeyError, JSONDecodeError), fallback_values=0)
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


def calculate_score_margin(weighted_score):
    if 0.65 <= weighted_score < 0.70:
        return 0.65
    elif 0.70 <= weighted_score < 0.75:
        return 0.68
    elif 0.75 <= weighted_score < 0.80:
        return 0.7
    else:
        return 0.65


if __name__ == '__main__':
    print('')
