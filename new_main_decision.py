import logging
import requests
import pandas as pd
from time import sleep

from reddit import compare
from technical_analysis import technical_analyse
from position import long_position_is_open, short_position_is_open
from news_analyser import check_sentiment_of_news
from youtube import check_bitcoin_youtube_videos_increase
from reddit import reddit_check
from macro_analyser import macro_sentiment, print_upcoming_events
from new_google_search import check_search_trend
from adam_predictor import decision_tree_predictor
from order_book import get_probabilities
from trading_decision import make_trading_decision

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


# Main trading loop
while True:
    LOOP_COUNTER += 1
    logging.info(f"LOOP_COUNTER: {LOOP_COUNTER}")

    # 1 Get the prediction
    prediction_bullish, prediction_bearish = decision_tree_predictor()

    # 2 Get probabilities of price going up or down
    order_book_bullish, order_book_bearish = get_probabilities(SYMBOLS, bid_multiplier=0.995, ask_multiplier=1.005)

    # 3 Monitor the richest Bitcoin addresses
    latest_info_saved = pd.read_csv('latest_info_saved.csv')
    total_received = latest_info_saved['total_received_coins_in_last_24'][0]
    total_sent = latest_info_saved['total_sent_coins_in_last_24'][0]
    richest_addresses_bullish, richest_addresses_bearish = compare(
        total_received, total_sent)

    # 4 Check Google search trends for Bitcoin and cryptocurrency
    google_search_bullish, google_search_bearish = check_search_trend(["Bitcoin", "Cryptocurrency"])

    # 5 Check macroeconomic indicators
    macro_bullish, macro_bearish = macro_sentiment()

    # remind upcoming macro events
    events_dates = 0
    print_upcoming_events(events_dates)

    # 6 Reddit
    reddit_bullish, reddit_bearish = reddit_check()

    # 7 YouTube
    youtube_bullish, youtube_bearish = check_bitcoin_youtube_videos_increase()

    # 8 Collect data from news websites
    news_bullish, news_bearish = check_sentiment_of_news()

    # 9 Technical analysis
    technical_bullish, technical_bearish = technical_analyse()

    # Make decision about the trade
    current_price = get_bitcoin_price()

    make_trading_decision(macro_bullish, macro_bearish,
                          order_book_bullish, order_book_bearish,
                          prediction_bullish, prediction_bearish,
                          technical_bullish, technical_bearish,
                          richest_addresses_bullish, richest_addresses_bearish,
                          google_search_bullish, google_search_bearish,
                          reddit_bullish, reddit_bearish,
                          youtube_bullish, youtube_bearish,
                          news_bullish, news_bearish)

    sleep(10)
