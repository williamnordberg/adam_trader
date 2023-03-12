from time import sleep
import requests
from order_book import get_probabilities, get_probabilities_hit_profit_or_stop
import pandas as pd
from macro_expected import get_macro_expected_and_real_compare, print_upcoming_events


PROFIT_MARGIN = 0.002
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
            return 0
    except requests.exceptions.RequestException as e:
        print(f"Error: Could not connect to CoinGecko API:{e}")
        return 0


def long_position_is_open():
    current_price = get_bitcoin_price()
    position_opening_price = current_price
    profit_point = current_price + (current_price * PROFIT_MARGIN)
    stop_loss = current_price - (current_price * PROFIT_MARGIN)
    print(f'current_price:{current_price}, profit_point:{profit_point},stop_loss:{stop_loss} ')
    profit, loss = 0, 0

    while True:
        print('******************************************')
        current_price = get_bitcoin_price()
        print(f'current_price:{current_price}, profit_point:{profit_point},stop_loss:{stop_loss} ')
        # Check if we meet profit or stop loss
        if current_price > profit_point:
            profit = current_price - position_opening_price
            print('&&&&&&&&&&&&&& target hit &&&&&&&&&&&&&&&&&&&&&')
            return profit, loss
        elif current_price < stop_loss:
            loss = position_opening_price - current_price
            print('&&&&&&&&&&&&&& STOP LOSS &&&&&&&&&&&&&&&&&&&&&')
            return profit, loss

        # 1.Order book
        probability_down, probability_up = get_probabilities(
            SYMBOLS, bid_multiplier=0.995, ask_multiplier=1.005)
        # print('Probability of price going down and up:', probability_down, probability_up)

        probability_to_hit_target, probability_to_hit_stop_loss = \
            get_probabilities_hit_profit_or_stop(SYMBOLS, 1000, profit_point, stop_loss)
        print(f'profit:{probability_to_hit_target}stop:{probability_to_hit_stop_loss}')

        # 2. Blockchain monitoring(is the richest addresses accumulating?)
        last_24_accumulation = pd.read_csv('last_24_accumulation.csv')
        total_received, total_sent = last_24_accumulation['total_received']\
            .values[0], last_24_accumulation['total_sent'].values[0]

        # 3. Macroeconomics data
        cpi_better_than_expected, ppi_better_than_expected, interest_rate_better_than_expected, \
            events_dates = get_macro_expected_and_real_compare()

        # remind upcoming macro events
        print_upcoming_events(events_dates)

        # 4. Technical Analysis (are we going toward position)?

        # 5.News and Events(positive > negative * 1.6)

        # 6. Twitter

        # 7.Google search (is that increase?)

        # 8.Reddit

        # 9.Youtube

        # 10. Adam predictor (is prediction is positive)

        # decision to close long position
        if probability_to_hit_target < 40 or probability_up < 40:
            if total_received < total_sent:
                print('close position at loss')
                return profit, loss
        sleep(5)


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
