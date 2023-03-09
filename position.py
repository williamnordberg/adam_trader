from time import sleep
import requests
from order_book import get_probabilities, get_probabilities_hit_profit_or_stop

PROFIT_MARGIN = 0.01
SYMBOLS = ['BTCUSDT', 'BTCBUSD']


def get_bitcoin_price():
    """
    Retrieves the current Bitcoin price in USD from the CoinGecko API.
    """
    try:
        url = 'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd'
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            current_price_local = data['bitcoin']['usd']
            return current_price_local
        else:
            print("Error: Could not retrieve Bitcoin price data")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error: Could not connect to CoinGecko API:{e}")
        return None


def long_position_is_open():
    current_price = get_bitcoin_price()
    position_opening_price = current_price
    profit_point = current_price + (current_price * PROFIT_MARGIN)
    stop_loss = current_price - (current_price * PROFIT_MARGIN)
    profit, loss = 0, 0

    while True:
        current_price = get_bitcoin_price()
        # Check if we meet profit or stop loss
        if current_price > profit_point:
            profit = current_price - position_opening_price
            return profit, loss
        elif current_price < stop_loss:
            loss = position_opening_price - current_price
            return profit, loss

        # 1.Order book
        probability_down, probability_up = get_probabilities(
            SYMBOLS, bid_multiplier=0.995, ask_multiplier=1.005)
        print('Probability of price going down and up:', probability_down, probability_up)

        probability_to_hit_target, probability_to_hit_stop_loss = \
            get_probabilities_hit_profit_or_stop(SYMBOLS, 1000, profit_point, stop_loss)
        print('get_probabilities_hit_profit_or_stop', probability_to_hit_target,
              probability_to_hit_stop_loss)

        # 2. Blockchain monitoring(is the richest addresses accumulating?)
        # TODO: here

        # 3. Macroeconomics data ( is the day that important data comes out)?

        # 4. Technical Analysis (are we going toward position)?

        # 5.News and Events(positive > negative * 1.6)

        # 6. Twitter

        # 7.Google search (is that increase?)

        # 8.Reddit

        # 9.Youtube

        # 10. Adam predictor (is prediction is positive)

        if probability_to_hit_target < 40 or probability_up < 40:
            print('close position at loss')
        sleep(20)


def short_position_is_open():

    print('short trade')

    # 1.Order book
    # probability of going toward profit
    # sell market if we there are some position to take position toward SL

    # 2. Blockchain monitoring(is the richest addresses accumulating?)

    # 3. Macroeconomics data ( is the day that important data comes out)?

    # 4. Technical Analysis (are we going toward position)?

    # 5.News and Events(positive > negative * 1.6)

    # 6. Twitter

    # 7.Google search (is that increase?)

    # 8.Reddit

    # 9.Youtube

    # 10. Adam predictor (is prediction is positive)


profit_after_trade, loss_after_trade = long_position_is_open()
print(f"profit_after_trade:{profit_after_trade}, loss_after_trade:{loss_after_trade}")

