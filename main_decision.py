import requests
from time import sleep
from monitor_2000_richest import monitor_bitcoin_richest_addresses
from order_book import get_probabilities
from adam_predictor import decision_tree_predictor
from google_search import check_search_trend
from macro_expected import get_macro_expected_and_real_compare
from reddit import reddit_check, load_previous_values
from youtube import check_bitcoin_youtube_videos_increase

LOOP_COUNTER = 0
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


# Main trading loop
while True:
    LOOP_COUNTER += 1
    print(LOOP_COUNTER)

    # 1.1 Get the prediction
    predicted_price = decision_tree_predictor()
    print(f"The predicted price is: {predicted_price}")

    # region 2. Gather data from external sources
    # 2.1 Get probabilities of price going up or down
    probability_down, probability_up = get_probabilities(SYMBOLS, bid_multiplier=0.995, ask_multiplier=1.005)
    print('Probability of price going down and up:', probability_down, probability_up)

    # 2.2 Monitor the richest Bitcoin addresses
    total_received, total_sent = monitor_bitcoin_richest_addresses()

    # 2.3 Check Google search trends for Bitcoin and cryptocurrency
    increase_google_search = check_search_trend(["Bitcoin", "Cryptocurrency"], threshold=1.2)

    # 2.4 Check macroeconomic indicators
    cpi_better_than_expected, ppi_better_than_expected, interest_rate_better_than_expected \
        = get_macro_expected_and_real_compare()

    # 2.5 Reddit
    previous_activity, previous_count = load_previous_values()
    current_activity, current_count, activity_increase, count_increase = reddit_check(previous_activity, previous_count)
    previous_activity, previous_count = current_activity, current_count

    # 2.6 YouTube
    bitcoin_youtube_increase_15_percent = check_bitcoin_youtube_videos_increase()

    # 2.8 Collect data from news websites

    # 2.9 Twitter

    # endregion

    # region 3. Make decision about the trade
    current_price = get_bitcoin_price()

    # 3.1 Check if conditions are met for a long position
    if (predicted_price > current_price * 1.01) and (probability_up > 0.6) and increase_google_search:
        if total_received > total_sent:
            if cpi_better_than_expected and ppi_better_than_expected and interest_rate_better_than_expected:
                if activity_increase or count_increase:
                    if bitcoin_youtube_increase_15_percent:
                        print('Opening a long position')
                # TODO: Add code to execute the long position

    # 3.2 Check if conditions are met for a short position
    elif (predicted_price < current_price * 0.99) and (probability_down > 0.6) and not increase_google_search:
        if total_received < total_sent:
            if not cpi_better_than_expected and not ppi_better_than_expected and not interest_rate_better_than_expected:
                if not activity_increase or not count_increase:
                    if not bitcoin_youtube_increase_15_percent:
                      print('Opening a short position')
                # TODO: Add code to execute the short position
    # endregion

    sleep(10)

# region when a trade is open
# TODO: Add code to
