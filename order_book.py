import requests

ENDPOINT = "https://api.binance.com/api/v3/depth"
LIMIT = 1000
IMBALANCE_TO_INITIATE = 0.53
IMBALANCE_TO_CLOSE_POSITION = 0.65
PROBABILITY_THRESHOLD = -0.2
BID_VOLUME, ASK_VOLUME, TARGET_PRICE, STOP_PRICE = 0, 0, 0, 0


def get_price(symbol):
    try:
        response = requests.get("https://api.binance.com/api/v3/ticker/price", params={'symbol': symbol})
        return float(response.json()['price'])
    except requests.exceptions.RequestException as e:
        print(e)
        return None


def get_probabilities(symbols, limit=1000, bid_multiplier=0.995, ask_multiplier=1.005):
    endpoint = "https://api.binance.com/api/v3/depth"
    bid_volume, ask_volume = 0, 0
    for symbol in symbols:
        try:
            response = requests.get(endpoint, params={'symbol': symbol, 'limit': limit})
            data = response.json()
            current_price = get_price(symbol)
            bid_volume += sum([float(bid[1]) for bid in data['bids'] if float(bid[0]) >= (current_price * bid_multiplier)])
            ask_volume += sum([float(ask[1]) for ask in data['asks'] if float(ask[0]) <= current_price * ask_multiplier])
        except requests.exceptions.RequestException as e:
            print(e)
            return None
    probability_down_in_function = bid_volume / (bid_volume + ask_volume)
    probability_up_in_function = ask_volume / (bid_volume + ask_volume)
    return probability_down_in_function, probability_up_in_function


