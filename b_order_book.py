from typing import List
import requests

from z_read_write_csv import save_update_time, read_latest_data,\
    write_latest_data, save_value_to_database
from z_handy_modules import get_bitcoin_price, retry_on_error
from z_compares import compare_order_volume
from a_config import position, SHORT_POSITION
from z_handy_modules import get_bitcoin_future_market_price


SPOT_ENDPOINT_DEPTH = "https://api.binance.com/api/v3/depth"
FUTURES_ENDPOINT_DEPTH = 'https://fapi.binance.com/fapi/v1/depth'

LIMIT = 10000
SYMBOLS = ['BTCUSDT', 'BTCBUSD']

BID_MULTIPLIER = 0.99
ASK_MULTIPLIER = 1.01


@retry_on_error(max_retries=3, delay=5,
                allowed_exceptions=(requests.exceptions.RequestException, KeyError, TypeError
                                    ), fallback_values={'bids': [], 'asks': []})
def get_volume(symbol: str, limit: int) -> dict:
    trading_state = read_latest_data('latest_trading_state', str)
    if trading_state == 'short':
        ENDPOINT = FUTURES_ENDPOINT_DEPTH
        if symbol == 'BTCBUSD':
            return {'bids': [], 'asks': []}
    else:
        ENDPOINT = SPOT_ENDPOINT_DEPTH
    response = requests.get(ENDPOINT, params={'symbol': symbol, 'limit': str(limit)})
    return response.json()


def order_book(symbols: List[str], limit: int = LIMIT, bid_multiplier: float = BID_MULTIPLIER,
               ask_multiplier: float = ASK_MULTIPLIER) -> float:

    bid_volume, ask_volume = 0.0000001, 0.0
    current_price = get_bitcoin_price()
    for symbol in symbols:
        data = get_volume(symbol, limit)
        if data is None:
            return 0.5
        bid_volume += sum([float(bid[1]) for bid in data['bids'] if float(bid[0]) >=
                           (current_price * bid_multiplier)])
        ask_volume += sum([float(ask[1]) for ask in data['asks'] if float(ask[0]) <=
                           current_price * ask_multiplier])

    probability_up = bid_volume / (bid_volume + ask_volume)
    probability_down = ask_volume / (bid_volume + ask_volume)

    order_book_bullish = compare_order_volume(probability_up, probability_down)

    save_value_to_database('bid_volume', round(bid_volume, 0))
    save_value_to_database('ask_volume', round(ask_volume, 0))
    save_value_to_database('order_book_bullish', order_book_bullish)
    # save_value_to_database('order_book_bearish', order_book_bearish)

    save_update_time('order_book')

    return order_book_bullish


def order_book_hit_target(symbols: List[str], limit: int, profit_target: float,
                          stop_loss: float) -> float:
    print('here pull worked \n', )

    bid_volume, ask_volume = 0.0000001, 0.0
    for symbol in symbols:
        data = get_volume(symbol, limit)
        if data is None:
            return 0.5

        bids = data.get('bids')
        asks = data.get('asks')

        if bids is not None:
            bid_volume += sum([float(bid[1]) for bid in bids if float(bid[0]) >= stop_loss])

        if asks is not None:
            ask_volume += sum([float(ask[1]) for ask in asks if float(ask[0]) <= profit_target])

    probability_to_hit_target = bid_volume / (bid_volume + ask_volume)
    #  probability_to_hit_stop_loss = ask_volume / (bid_volume + ask_volume)

    write_latest_data('order_book_hit_profit', round(probability_to_hit_target, 2))

    return probability_to_hit_target


if __name__ == '__main__':
    print('order_book')
    order_book_bullish_outer = order_book(
        SYMBOLS, limit=LIMIT, bid_multiplier=BID_MULTIPLIER, ask_multiplier=ASK_MULTIPLIER)
    print(f'order_book_bullish:{order_book_bullish_outer}')

    print('order_book_ target')

    current_price = get_bitcoin_future_market_price()

    profit_target = int(current_price - (current_price * SHORT_POSITION['PROFIT_MARGIN']))
    stop_loss = int(current_price + (current_price * SHORT_POSITION['PROFIT_MARGIN']))
    position['type'] = 'short'
    order_book_bullish_outer1 = order_book_hit_target(
            SYMBOLS, 1000, stop_loss, profit_target)
    print(f'order_book_bullish:{order_book_bullish_outer1}')


