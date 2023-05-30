import requests
import logging

from handy_modules import read_current_trading_state
from handy_modules import  retry_on_error_fallback_0_0

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
FUTURES_ENDPOINT_DEPTH = 'https://fapi.binance.com/fapi/v1/depth'
SPOT_ENDPOINT_DEPTH = "https://api.binance.com/api/v3/depth"

LIMIT = 1000
SYMBOLS = ['BTCUSDT', 'BTCBUSD']


# Tempor

@retry_on_error_fallback_0_0(max_retries=3, delay=5, allowed_exceptions=(requests.exceptions.RequestException,))
def get_order_book(symbol: str, limit: int):
    try:
        trading_state = 'short'
        if trading_state == 'short':
            ENDPOINT = FUTURES_ENDPOINT_DEPTH
            if symbol == 'BTCBUSD':
                return {'bids': [], 'asks': []}
        else:
            ENDPOINT = SPOT_ENDPOINT_DEPTH
        response = requests.get(ENDPOINT, params={'symbol': symbol, 'limit': str(limit)})
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(e)
        return None


x = get_order_book('BTCBUSD', 1000)
print('x', x)

y = get_order_book('BTCUSDT', 1000)
print(y)

