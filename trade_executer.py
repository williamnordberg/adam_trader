from binance.client import Client
import logging
import configparser
import os


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load the config file
config = configparser.ConfigParser()
config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.ini')

with open(config_path, 'r') as f:
    config_string = f.read()

config.read_string(config_string)
api_key = config.get('binance', 'api_key')
print('api_key: ', api_key)
api_secret = config.get('binance', 'api_secret')
print('api_secret: ', api_secret)

# Initialize the Binance client with your API key and secret key
client = Client(api_key, api_secret)


def buy_btc_at_price(btc_amount, price):
    # Get the latest ticker price for BTC
    ticker = client.get_symbol_ticker(symbol='BTCUSDT')
    latest_price = float(ticker['price'])
    logging.info(f'latest price: {latest_price}')

    # Check if the target price has been reached
    if latest_price >= price:
        # Place a limit buy order for the desired amount of BTC at the target price
        client.create_order(
            symbol='BTCUSDT',
            side='BUY',
            type='LIMIT',
            timeInForce='GTC',
            quantity=btc_amount,
            price=price
        )

        print('Buy order placed successfully')
    else:
        print('Target price has not been reached')


# Example usage: Buy 0.01 BTC when the price drops to $50,000
buy_btc_at_price(0.001, 11000)
