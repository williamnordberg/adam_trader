import requests
import logging
from typing import Tuple

BINANCE_ENDPOINT_PRICE = "https://api.binance.com/api/v3/ticker/price"
GECKO_ENDPOINT_PRICE = 'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd'

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


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


if __name__ == '__main__':
    logging.info(f'bitcoin price: {get_bitcoin_price()}')

    predicted_bullish, predicted_bearish = compare_predicted_price(200, 198)
    logging.info(f'predicted_bullish: {predicted_bullish}, predicted_bearish: {predicted_bearish} ')

    google_bullish, google_bearish = compare_google_search_trends(10, 13)
    logging.info(f'google_bullish: {google_bullish}, google_bearish: {google_bearish} ')
