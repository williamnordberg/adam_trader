import requests
import logging
from functools import wraps
from time import sleep
from json import JSONDecodeError
from binance.exceptions import BinanceAPIException, BinanceRequestException

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
BINANCE_FUTURES_ENDPOINT_PRICE = "https://fapi.binance.com/fapi/v1/ticker/price"

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
                raise Exception(f"Exception raised, All {max_retries} attempts failed without a fallback value.")

        return wrapper

    return decorator


@retry_on_error(max_retries=3, delay=5, allowed_exceptions=(
        requests.exceptions.RequestException, requests.exceptions.Timeout,
        BinanceAPIException, BinanceRequestException, ValueError, KeyError, JSONDecodeError),
                fallback_values=0)
def get_bitcoin_future_market_price() -> int:
    try:
        response = requests.get(BINANCE_FUTURES_ENDPOINT_PRICE, params={'symbol': 'BTCUSDT'})
        if response.status_code == 200:
            return int(float(response.json()['price']))
    except requests.exceptions.RequestException as e:
        logging.error(f"Error: Could not connect to Binance Futures API:{e}")

    raise requests.exceptions.RequestException("API call failed")


@retry_on_error(max_retries=3, delay=5, allowed_exceptions=(
    requests.exceptions.RequestException, requests.exceptions.Timeout,
    ValueError, KeyError, JSONDecodeError), fallback_values=0)
def get_bitcoin_price() -> int:
    try:
        response = requests.get(BINANCE_ENDPOINT_PRICE, params={'symbol': 'BTCUSDT'})
        if response.status_code == 200:
            return int(float(response.json()['price']))
    except requests.exceptions.RequestException as e:
        logging.error(f"Error: Could not connect to Binance API:{e}")

    try:
        response = requests.get(GECKO_ENDPOINT_PRICE)
        if response.status_code == 200:
            data = response.json()
            current_price = int(data['bitcoin']['usd'])
            return current_price
    except requests.exceptions.RequestException as e:
        logging.error(f"Error: Could not connect to CoinGecko API:{e}, It will try with Binance")

    raise requests.exceptions.RequestException("Both API calls failed")


if __name__ == '__main__':
    while True:
        print(get_bitcoin_future_market_price())
        sleep(2)
