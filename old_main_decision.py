import requests
from time import sleep
from order_book import get_probabilities
from adam_predictor import decision_tree_predictor
from google_search import check_search_trend
from macro_expected import get_macro_expected_and_real_compare, print_upcoming_events
from reddit import reddit_check
from youtube import check_bitcoin_youtube_videos_increase
from news_websites import check_sentiment_of_news
from position import long_position_is_open, short_position_is_open
from technical_analysis import technical_analyse
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
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
            logging.error("Error: Could not retrieve Bitcoin price data")
            return None
    except requests.exceptions.RequestException as e:
        logging.error(f"Error: Could not connect to CoinGecko API:{e}")
        return None


# Main trading loop
while True:
    LOOP_COUNTER += 1
    logging.info(f"LOOP_COUNTER: {LOOP_COUNTER}")

    # 1.1 Get the prediction
    predicted_price = decision_tree_predictor()
    logging.info(f"The predicted price is: {predicted_price}")

    # region 2. Gather data from external sources
    # 2.1 Get probabilities of price going up or down
    probability_down, probability_up = get_probabilities(SYMBOLS, bid_multiplier=0.995, ask_multiplier=1.005)
    logging.info(f'Probability of price going down and up: {probability_down}, {probability_up}')

    # 2.2 Monitor the richest Bitcoin addresses

    latest_info_saved = pd.read_csv('latest_info_saved.csv')
    total_received = latest_info_saved['total_received_coins_in_last_24'][0]
    total_sent = latest_info_saved['total_sent_coins_in_last_24'][0]

    # 2.3 Check Google search trends for Bitcoin and cryptocurrency
    increase_google_search = check_search_trend(["Bitcoin", "Cryptocurrency"], threshold=1.2)

    # 2.4 Check macroeconomic indicators
    cpi_better_than_expected, ppi_better_than_expected, interest_rate_better_than_expected, events_dates \
        = get_macro_expected_and_real_compare()

    # remind upcoming macro events
    print_upcoming_events(events_dates)

    # 2.5 Reddit
    current_activity, current_count, activity_increase, count_increase = reddit_check()

    # 2.6 YouTube
    bitcoin_youtube_increase_15_percent = check_bitcoin_youtube_videos_increase()

    # 2.8 Collect data from news websites
    sentiment_of_news = check_sentiment_of_news()

    # 2.9 Twitter
    # TODO: after getting academic api key

    # 2.10 Technical analysis
    technical_bullish, technical_bearish = technical_analyse()
    # endregion

    # region 3. Make decision about the trade
    current_price = get_bitcoin_price()

    # 3.1 Check if conditions are met for a long position
    if (predicted_price > current_price * 1.01) and (probability_up > 0.6) and increase_google_search:
        if total_received > total_sent:
            if cpi_better_than_expected and ppi_better_than_expected and interest_rate_better_than_expected:
                if activity_increase or count_increase:
                    if bitcoin_youtube_increase_15_percent:
                        if sentiment_of_news:
                            if technical_bullish:
                                logging.info('Opening a long position')
                                profit_after_trade, loss_after_trade = \
                                    long_position_is_open()
                                logging.info(f"profit_after_trade:{profit_after_trade}, loss_after_trade:"
                                             f"{loss_after_trade}")

    # 3.2 Check if conditions are met for a short position
    elif (predicted_price < current_price * 0.99) and (probability_down > 0.6) and not increase_google_search:
        if total_received < total_sent:
            if not cpi_better_than_expected and not ppi_better_than_expected and not interest_rate_better_than_expected:
                if not activity_increase or not count_increase:
                    if not bitcoin_youtube_increase_15_percent:
                        if not sentiment_of_news:
                            if technical_bearish:
                                logging.info('Opening short position')
                                profit_after_trade, loss_after_trade = \
                                    short_position_is_open()
                                logging.info(f"profit_after_trade:{profit_after_trade}, "
                                             f"loss_after_trade:{loss_after_trade}")

    # endregion

    sleep(10)