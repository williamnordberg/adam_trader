import requests
import logging


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def compare_predicted_price(predicted_price, current_price):

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


def get_bitcoin_price():
    """
    Retrieves the current Bitcoin price in USD from the CoinGecko API.

    Returns:
        float: The current Bitcoin price in USD or 0 if an error occurred.
    """
    try:
        url = 'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd'
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            current_price_local = data['bitcoin']['usd']
            return current_price_local
        else:
            logging.error("Error: Could not retrieve Bitcoin price data")
            return 0
    except requests.exceptions.RequestException as e:
        logging.error(f"Error: Could not connect to CoinGecko API:{e}")
        return 0

