from typing import List, Optional, Tuple, Dict
import requests
import logging
from datetime import datetime, timedelta

from database import save_value_to_database
from handy_modules import get_bitcoin_price, retry_on_error_fallback_0_0

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
ENDPOINT_DEPTH = "https://api.binance.com/api/v3/depth"
LIMIT = 1000
SYMBOLS = ['BTCUSDT', 'BTCBUSD']


# Temporary storage for aggregated values
aggregated_values: Dict[str, List[float]] = {
    'bid_volume': [],
    'ask_volume': [],
    'order_book_bullish': [],
    'order_book_bearish': []
}


def aggregate_and_save_values():
    if not aggregated_values['bid_volume']:  # If there are no values, do nothing
        return

    # Calculate the average values for each key in the temporary storage
    avg_values = {key: sum(values) / len(values) for key, values in aggregated_values.items()}

    # Save the average values to the database
    save_value_to_database('bid_volume', round(avg_values['bid_volume'], 2))
    save_value_to_database('ask_volume', round(avg_values['ask_volume'], 2))
    save_value_to_database('order_book_bullish', avg_values['order_book_bullish'])
    save_value_to_database('order_book_bearish', avg_values['order_book_bearish'])

    # Clear the temporary storage
    for key in aggregated_values:
        aggregated_values[key] = []


@retry_on_error_fallback_0_0(max_retries=3, delay=5, allowed_exceptions=(requests.exceptions.RequestException,))
def get_order_book(symbol: str, limit: int):
    try:
        response = requests.get(ENDPOINT_DEPTH, params={'symbol': symbol, 'limit': str(limit)})
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(e)
        return None


def compare_probability(probability_up: float, probability_down: float) -> Tuple[float, float]:

    if probability_up > probability_down:
        if probability_up >= 0.65:
            return 1, 0
        elif probability_up >= 0.62:
            return 0.9, 0.1
        elif probability_up >= 0.59:
            return 0.8, 0.2
        elif probability_up >= 0.56:
            return 0.7, 0.3
        elif probability_up >= 0.53:
            return 0.6, 0.4

    elif probability_up < probability_down:
        if probability_down >= 0.65:
            return 0, 1
        elif probability_down >= 0.62:
            return 0.1, 0.9
        elif probability_down >= 0.59:
            return 0.2, 0.8
        elif probability_down >= 0.56:
            return 0.3, 0.7
        elif probability_down >= 0.53:
            return 0.4, 0.6

    return 0, 0


def get_probabilities(symbols: List[str], limit: int = LIMIT, bid_multiplier: float = 0.995,
                      ask_multiplier: float = 1.005) -> Optional[Tuple[float, float]]:
    bid_volume, ask_volume = 0.0000001, 0.0
    current_price = get_bitcoin_price()
    for symbol in symbols:
        data = get_order_book(symbol, limit)
        if data is None:
            return 0, 0

        bid_volume += sum([float(bid[1]) for bid in data['bids'] if float(bid[0]) >=
                           (current_price * bid_multiplier)])
        ask_volume += sum([float(ask[1]) for ask in data['asks'] if float(ask[0]) <=
                           current_price * ask_multiplier])
    print('bid_volume', bid_volume)
    print('ask vol', ask_volume)
    probability_up = bid_volume / (bid_volume + ask_volume)
    probability_down = ask_volume / (bid_volume + ask_volume)
    print('probability_up', probability_up)
    print('probability_down', probability_down)

    order_book_bullish, order_book_bearish = compare_probability(probability_up, probability_down)

    # Add the values to the temporary storage
    aggregated_values['bid_volume'].append(bid_volume)
    aggregated_values['ask_volume'].append(ask_volume)
    aggregated_values['order_book_bullish'].append(order_book_bullish)
    aggregated_values['order_book_bearish'].append(order_book_bearish)

    # Check if an hour has passed since the last database update
    current_time = datetime.now()
    last_hour = current_time.replace(minute=0, second=0, microsecond=0)
    if current_time - last_hour >= timedelta(hours=1):
        aggregate_and_save_values()

    # Save the value in database for a run before an hour pass
    else:
        save_value_to_database('bid_volume', round(bid_volume, 2))
        save_value_to_database('ask_volume', round(ask_volume, 2))
        save_value_to_database('order_book_bullish', order_book_bullish)
        save_value_to_database('order_book_bearish', order_book_bearish)

    return order_book_bullish, order_book_bearish


def get_probabilities_hit_profit_or_stop(symbols: List[str], limit: int, profit_target: float,
                                         stop_loss: float) -> Optional[Tuple[float, float]]:
    bid_volume, ask_volume = 0.0, 0.0
    for symbol in symbols:
        data = get_order_book(symbol, limit)
        if data is None:
            return None

        bids = data.get('bids')
        asks = data.get('asks')

        if bids is not None:
            bid_volume += sum([float(bid[1]) for bid in bids if float(bid[0]) >= stop_loss])

        if asks is not None:
            ask_volume += sum([float(ask[1]) for ask in asks if float(ask[0]) <= profit_target])

    probability_to_hit_target = bid_volume / (bid_volume + ask_volume)
    probability_to_hit_stop_loss = ask_volume / (bid_volume + ask_volume)

    return probability_to_hit_target, probability_to_hit_stop_loss


if __name__ == '__main__':
    probabilities = get_probabilities(SYMBOLS, limit=LIMIT, bid_multiplier=0.99, ask_multiplier=1.01)
    assert probabilities is not None, "get_probabilities returned None"
    order_book_bullish_outer, order_book_bearish_outer = probabilities

    probabilities_hit = get_probabilities_hit_profit_or_stop(SYMBOLS, LIMIT, 30000, 20000)
    assert probabilities_hit is not None, "get_probabilities_hit_profit_or_stop returned None"
    order_book_hit_target_outer, order_book_hit_stop_outer = probabilities_hit

    logging.info(f'order_book_bullish:{order_book_bullish_outer},'
                 f'order_book_bearish: {order_book_bearish_outer}')

    logging.info(f'order_book_hit_target:{order_book_hit_target_outer},'
                 f'order_book_hit_stop: {order_book_hit_stop_outer}')
