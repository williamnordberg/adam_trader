import requests
import logging
import configparser

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load the config file
config = configparser.ConfigParser()
config.read('config.ini')

ENDPOINT = "https://api.binance.com/api/v3/depth"
LIMIT = 1000
SYMBOLS = ['BTCUSDT', 'BTCBUSD']
PROFIT_MARGIN = 0.01


def get_price(symbol):
    """
      Get the price of a given symbol.

      :param symbol: The trading symbol to get the price for
      :return: The price of the symbol or None if an error occurs
      """
    try:
        response = requests.get("https://api.binance.com/api/v3/ticker/price", params={'symbol': symbol})
        return float(response.json()['price'])
    except requests.exceptions.RequestException as e:
        logging.error(e)
        return None


def get_probabilities(symbols, limit=LIMIT, bid_multiplier=0.995, ask_multiplier=1.005):
    """
    Calculate the probabilities of price movement for a list of trading symbols.

    :param symbols: List of trading symbols
    :param limit: Limit for the depth of the order book
    :param bid_multiplier: Multiplier for bid orders
    :param ask_multiplier: Multiplier for ask orders
    :return: Probabilities of price movement (down, up) or None if an error occurs
    """
    bid_volume, ask_volume = 0, 0
    for symbol in symbols:
        try:
            response = requests.get(f"{ENDPOINT}/depth", params={'symbol': symbol, 'limit': limit})
            data = response.json()
            current_price = get_price(symbol)
            bid_volume += sum(
                [float(bid[1]) for bid in data['bids'] if float(bid[0]) >= (current_price * bid_multiplier)])
            ask_volume += sum(
                [float(ask[1]) for ask in data['asks'] if float(ask[0]) <= current_price * ask_multiplier])
        except requests.exceptions.RequestException as e:
            logging.error(e)
            return None
    probability_down = bid_volume / (bid_volume + ask_volume)
    probability_up = ask_volume / (bid_volume + ask_volume)
    return probability_down, probability_up


def get_probabilities_hit_profit_or_stop(symbols, limit, profit_target, stop_loss):
    """
    Calculate the probabilities of hitting profit target or stop loss for a list of trading symbols.

    :param symbols: List of trading symbols
    :param limit: Limit for the depth of the order book
    :param profit_target: Profit target price
    :param stop_loss: Stop loss price
    :return: Probabilities of hitting profit target and stop loss (target, stop_loss) or None if an error occurs
    """
    bid_volume, ask_volume = 0, 0
    for symbol in symbols:
        try:
            response = requests.get(f"{ENDPOINT}/depth", params={'symbol': symbol, 'limit': limit})
            data = response.json()
            bid_volume += sum([float(bid[1]) for bid in data['bids'] if float(bid[0]) >= stop_loss])
            ask_volume += sum([float(ask[1]) for ask in data['asks'] if float(ask[0]) <= profit_target])
        except requests.exceptions.RequestException as e:
            logging.error(e)
            return None
    probability_to_hit_target = bid_volume / (bid_volume + ask_volume)
    probability_to_hit_stop_loss = ask_volume / (bid_volume + ask_volume)
    return probability_to_hit_target, probability_to_hit_stop_loss


if __name__ == "__main__":
    probability_down_outer, probability_up_outer = get_probabilities(SYMBOLS, LIMIT, bid_multiplier=0.995, ask_multiplier=1.005)
    logging.info(f'Probability of price going down and up: {probability_down_outer}, {probability_up_outer}')