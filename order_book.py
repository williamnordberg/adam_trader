import requests
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
ENDPOINT_DEPTH = "https://api.binance.com/api/v3/depth"
ENDPOINT_PRICE = "https://api.binance.com/api/v3/ticker/price"
LIMIT = 1000
SYMBOLS = ['BTCUSDT', 'BTCBUSD']


def get_price(symbol, session):
    try:
        response = session.get(ENDPOINT_PRICE, params={'symbol': symbol})
        return float(response.json()['price'])
    except requests.exceptions.RequestException as e:
        logging.error(f"Error getting price for {symbol}: {e}")
        raise


def get_order_book(symbol, limit, session):
    try:
        response = session.get(ENDPOINT_DEPTH, params={'symbol': symbol, 'limit': limit})
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(e)
        return None


def compare_probability(probability_up, probability_down):

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


def get_probabilities(symbols, limit=LIMIT, bid_multiplier=0.995, ask_multiplier=1.005):
    bid_volume, ask_volume = 0.0000001, 0
    with requests.Session() as session:
        for symbol in symbols:
            data = get_order_book(symbol, limit, session)
            if data is None:
                return None

            current_price = get_price(symbol, session)
            bid_volume += sum([float(bid[1]) for bid in data['bids'] if float(bid[0]) >= (current_price * bid_multiplier)])
            ask_volume += sum([float(ask[1]) for ask in data['asks'] if float(ask[0]) <= current_price * ask_multiplier])

    probability_up = bid_volume / (bid_volume + ask_volume)
    probability_down = ask_volume / (bid_volume + ask_volume)
    order_book_bullish, order_book_bearish = compare_probability(probability_up, probability_down)

    return order_book_bullish, order_book_bearish


def get_probabilities_hit_profit_or_stop(symbols, limit, profit_target, stop_loss):
    bid_volume, ask_volume = 0, 0
    with requests.Session() as session:
        for symbol in symbols:
            data = get_order_book(symbol, limit, session)
            if data is None:
                return None

            bid_volume += sum([float(bid[1]) for bid in data['bids'] if float(bid[0]) >= stop_loss])
            ask_volume += sum([float(ask[1]) for ask in data['asks'] if float(ask[0]) <= profit_target])

    probability_to_hit_target = bid_volume / (bid_volume + ask_volume)
    probability_to_hit_stop_loss = ask_volume / (bid_volume + ask_volume)
    return probability_to_hit_target, probability_to_hit_stop_loss


if __name__ == '__main__':
    order_book_bullish_outer, order_book_bearish_outer = \
        get_probabilities(SYMBOLS, limit=LIMIT, bid_multiplier=0.995, ask_multiplier=1.005)
    order_book_hit_target_outer, order_book_hit_stop_outer = \
        get_probabilities_hit_profit_or_stop(SYMBOLS, LIMIT, 30000, 20000)

    logging.info(f'order_book_bullish:{order_book_bullish_outer},'
                 f'order_book_bearish: {order_book_bearish_outer}')

    logging.info(f'order_book_hit_target:{order_book_hit_target_outer},'
                 f'order_book_hit_stop: {order_book_hit_stop_outer}')

