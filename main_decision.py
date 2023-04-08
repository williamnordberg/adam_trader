import logging
import requests
import pandas as pd
from time import sleep
from technical_analysis import technical_analyse
from position import long_position_is_open, short_position_is_open
from news_websites import check_sentiment_of_news
from youtube import check_bitcoin_youtube_videos_increase
from reddit import reddit_check
from macro_analyser import macro_sentiment, print_upcoming_events
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


# Main trading loop
while True:
    LOOP_COUNTER += 1
    logging.info(f"LOOP_COUNTER: {LOOP_COUNTER}")

    # 1.1 Get the prediction
    predicted_price = decision_tree_predictor()
    logging.info(f"The predicted price is: {predicted_price}")

    # 2. Gather data from external sources
    # 2.1 Get probabilities of price going up or down
    probability_down, probability_up = get_probabilities(SYMBOLS, bid_multiplier=0.995, ask_multiplier=1.005)
    logging.info(f'Probability of price going down and up: {probability_down}, {probability_up}')

    # 2.2 Monitor the richest Bitcoin addresses
    latest_info_saved = pd.read_csv('latest_info_saved.csv')
    total_received = latest_info_saved['total_received_coins_in_last_24'][0]
    total_sent = latest_info_saved['total_sent_coins_in_last_24'][0]

    # 2.3 Check Google search trends for Bitcoin and cryptocurrency
    google_bullish, google_bearish = check_search_trend(["Bitcoin", "Cryptocurrency"])

    # 2.4 Check macroeconomic indicators
    cpi_better_than_expected, ppi_better_than_expected, interest_rate_better_than_expected, events_dates \
        = macro_sentiment()

    # remind upcoming macro events
    print_upcoming_events(events_dates)

    # 2.5 Reddit
    activity_increase, count_increase = reddit_check()

    # 2.6 YouTube
    bitcoin_youtube_increase_15_percent = check_bitcoin_youtube_videos_increase()

    # 2.8 Collect data from news websites
    sentiment_of_news = check_sentiment_of_news()

    # 2.10 Technical analysis
    technical_bullish, technical_bearish = technical_analyse()

    # 3. Make decision about the trade
    current_price = get_bitcoin_price()

    make_trading_decision(predicted_price, current_price, probability_down, probability_up, increase_google_search,
                          total_received, total_sent, cpi_better_than_expected, ppi_better_than_expected,
                          interest_rate_better_than_expected, activity_increase, count_increase,
                          bitcoin_youtube_increase_15_percent, sentiment_of_news, technical_bullish, technical_bearish)

    sleep(10)
