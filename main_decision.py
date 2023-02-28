from time import sleep

from monitor_2000_richest import monitor_bitcoin_richest_addresses
from order_book import get_probabilities
from adam_predictor import decision_tree_predictor
from google_search import check_search_trend
import requests

loop_counter = 0
SYMBOLS = ['BTCUSDT', 'BTCBUSD']


def get_bitcoin_price():
    try:
        url = 'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd'
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            current_price_in_function = data['bitcoin']['usd']
            return current_price_in_function
        else:
            print("Error: Could not retrieve Bitcoin price data")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error: Could not connect to CoinGecko API:{e}")
        return None


# trading opportunity
while True:
    loop_counter += 1
    print(loop_counter)

    # region 1.1 Get the prediction
    Predicted_price = decision_tree_predictor()
    print(f"The predicted price is: {Predicted_price}")

    # endregion

    # region 2. Get Adam Watcher value

    # endregion 2. Get Adam Watcher value

    # region 2.1 get order book
    # get probability of price go up and down
    probability_down, probability_up = get_probabilities(SYMBOLS, bid_multiplier=0.995, ask_multiplier=1.005)
    print('prob down and up', probability_down, probability_up)

    # endregion

    # region 2.2. Richest address on blockchain
    total_received, total_sent = monitor_bitcoin_richest_addresses()
    # endregion

    # region 2.3 google search
    Increase_google_search = check_search_trend(["Bitcoin", "Cryptocurrency"], threshold=1.2)

    # endregion

    # region 2.4 interest rate

    # endregion

    # region 2.5 news website
    # endregion

    # region 2.6 Reddit
    # endregion

    # region  2.7 CPI PPI

    # end region

    # region 2.8 Twitter
    # endregion

    # region 2.9 Youtube
    # endregion

    # region 3.Make decision about the trade

    # Adam predictor
    current_price = get_bitcoin_price()
    if (Predicted_price > current_price * 1.01) and (probability_up > 0.6) and Increase_google_search:
        if total_received > total_sent:
            print('A long opened')
        break
    elif (Predicted_price < current_price * 0.99) and (probability_down > 0.6) and not Increase_google_search:
        if total_received < total_sent:
            print('A short opened')

    # endregion

    sleep(10)

# region when a trade is open
# endregion
