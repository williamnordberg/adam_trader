import requests

ENDPOINT = "https://api.binance.com/api/v3/depth"
SYMBOLS = ['BTCUSDT', 'BTCBUSD']
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


def get_volume(current_price):
    bid_volume, ask_volume = 0, 0
    for symbol in SYMBOLS:
        try:
            response = requests.get(ENDPOINT, params={'symbol': symbol, 'limit': LIMIT})
            data = response.json()
            bid_volume += sum([float(bid[1]) for bid in data['bids'] if float(bid[0]) >= (current_price * 0.995)])
            ask_volume += sum([float(ask[1]) for ask in data['asks'] if float(ask[0]) <= current_price * 1.005])
        except requests.exceptions.RequestException as e:
            print(e)
    return bid_volume, ask_volume


def calculate_probability(bid_volume, ask_volume):
    probability_down = bid_volume / (bid_volume + ask_volume)
    probability_up = ask_volume / (bid_volume + ask_volume)
    return probability_down, probability_up


price = get_price('BTCUSDT')
bid_volume, ask_volume = get_volume(price)
probability_down, probability_up = calculate_probability(bid_volume, ask_volume)
print(probability_down, probability_up)
