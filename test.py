import logging
import requests
import pandas as pd
from time import sleep
from technical_analysis import technical_analyse
from position import long_position_is_open, short_position_is_open
from news_websites import check_sentiment_of_news
from youtube import check_bitcoin_youtube_videos_increase
from reddit import reddit_check
from macro_expected import get_macro_expected_and_real_compare, print_upcoming_events
from google_search import check_search_trend
from adam_predictor import decision_tree_predictor
from order_book import get_probabilities

# Constants
LOOP_COUNTER = 0
SYMBOLS = ['BTCUSDT', 'BTCBUSD']

# Logging setup
logging.basicConfig(filename='trading.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


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
            raise Exception("Error: Could not retrieve Bitcoin price data")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error: Could not connect to CoinGecko API:{e}")
        raise Exception(f"Error: Could not connect to CoinGecko API:{e}")


def make_trading_decision(predicted_price_inner, current_price_inner, probability_down_inner, probability_up_inner,
                          increase_google_search_inner, total_received_inner, total_sent_inner,
                          cpi_better_than_expected_inner, ppi_better_than_expected_inner,
                          interest_rate_better_than_expected_inner, activity_increase_inner, count_increase_inner,
                          bitcoin_youtube_increase_15_percent_inner, sentiment_of_news_inner, technical_bullish_inner,
                          technical_bearish_inner):
    """
    Makes a trading decision based on the conditions met.
    """
    if (predicted_price_inner > current_price_inner * 1.01) and (probability_up_inner > 0.6) and \
            increase_google_search_inner:
        if total_received_inner > total_sent_inner:
            if cpi_better_than_expected_inner and ppi_better_than_expected_inner and \
                    interest_rate_better_than_expected_inner:
                if activity_increase_inner or count_increase_inner:
                    if bitcoin_youtube_increase_15_percent_inner:
                        if sentiment_of_news_inner:
                            if technical_bullish_inner:
                                logging.info('Opening a long position')
                                profit_after_trade, loss_after_trade = long_position_is_open()
                                logging.info(f"profit_after_trade:{profit_after_trade}, loss_after_trade:"
                                             f"{loss_after_trade}")
    elif (predicted_price_inner < current_price_inner * 0.99) and (probability_down_inner > 0.6) and not \
            increase_google_search_inner:
        if total_received_inner < total_sent_inner:
            if not cpi_better_than_expected_inner and not ppi_better_than_expected_inner and not \
                    interest_rate_better_than_expected_inner:
                if not activity_increase_inner or not count_increase_inner:
                    if not bitcoin_youtube_increase_15_percent_inner:
                        if not sentiment_of_news_inner:
                            if technical_bearish_inner:
                                logging.info('Opening short position')
                                profit_after_trade, loss_after_trade = short_position_is_open()
                                logging.info(f"profit_after_trade:{profit_after_trade}, "
                                             f"loss_after_trade:{loss_after_trade}")


def gather_data():
    data = {}

    try:
        data["predicted_price"] = decision_tree_predictor()
        data["probability_down"], data["probability_up"] = get_probabilities(SYMBOLS, bid_multiplier=0.995,
                                                                             ask_multiplier=1.005)
        latest_info_saved_inner = pd.read_csv('latest_info_saved.csv')
        data["total_received"] = latest_info_saved_inner['total_received_coins_in_last_24'][0]
        data["total_sent"] = latest_info_saved_inner['total_sent_coins_in_last_24'][0]
        data["increase_google_search"] = check_search_trend(["Bitcoin", "Cryptocurrency"], threshold=1.2)
        data["cpi_better_than_expected"], data["ppi_better_than_expected"], data["interest_rate_better_than_expected"],\
            data["events_dates"] = get_macro_expected_and_real_compare()
        data["current_activity"], data["current_count"], data["activity_increase"], data[
            "count_increase"] = reddit_check()
        data["bitcoin_youtube_increase_15_percent"] = check_bitcoin_youtube_videos_increase()
        data["sentiment_of_news"] = check_sentiment_of_news()
        data["technical_bullish"], data["technical_bearish"] = technical_analyse()
        data["current_price"] = get_bitcoin_price()

    except Exception as e:
        logging.error(f"Error gathering data: {e}")

    return data


# Main trading loop
while True:
    LOOP_COUNTER += 1
    logging.info(f"LOOP_COUNTER: {LOOP_COUNTER}")

    data = gather_data()

    make_trading_decision(**data)

    sleep(10)
