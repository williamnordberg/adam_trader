import logging
from time import sleep

from handy_modules import compare_send_receive_richest_addresses
from technical_analysis import technical_analyse
from news_analyser import check_sentiment_of_news
from youtube import check_bitcoin_youtube_videos_increase
from reddit import reddit_check
from macro_analyser import macro_sentiment, print_upcoming_events
from google_search import check_search_trend
from adam_predictor import decision_tree_predictor
from order_book import get_probabilities
from trading_decision import make_trading_decision
from long_position_open import long_position
from short_position_open import short_position
from factors_states_visualization import visualize_charts
from database_visualization import visualize_database_two_rows

# Constants
LOOP_COUNTER = 0
SYMBOLS = ['BTCUSDT', 'BTCBUSD']
long_threshold = 0.99
short_threshold = 0.99

logging.basicConfig(filename='trading.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Main trading loop
while True:
    LOOP_COUNTER += 1
    logging.info(f"LOOP_COUNTER: {LOOP_COUNTER}")

    # 1 Get the prediction
    prediction_bullish, prediction_bearish = decision_tree_predictor()

    # 2 Order book
    probabilities = get_probabilities(SYMBOLS, bid_multiplier=0.995, ask_multiplier=1.005)
    assert probabilities is not None, "get_probabilities returned None"
    order_book_bullish, order_book_bearish = probabilities

    # 3 Monitor the richest Bitcoin addresses
    richest_addresses_bullish, richest_addresses_bearish = compare_send_receive_richest_addresses()

    # 4 Check Google search trends for Bitcoin and cryptocurrency
    google_search_bullish, google_search_bearish = check_search_trend(["Bitcoin", "Cryptocurrency"])

    # 5 Macroeconomic
    macro_bullish, macro_bearish, events_date_dict = macro_sentiment()
    print_upcoming_events(events_date_dict)

    # 6 Reddit
    reddit_bullish, reddit_bearish = reddit_check()

    # 7 YouTube
    youtube_bullish, youtube_bearish = check_bitcoin_youtube_videos_increase()

    # 8 Collect data from news websites
    news_bullish, news_bearish = check_sentiment_of_news()

    # 9 Technical analysis
    technical_bullish, technical_bearish = technical_analyse()

    # Make decision about the trade
    weighted_score_up, weighted_score_down = make_trading_decision(
        macro_bullish, macro_bearish, order_book_bullish, order_book_bearish,
        prediction_bullish, prediction_bearish,
        technical_bullish, technical_bearish,
        richest_addresses_bullish, richest_addresses_bearish,
        google_search_bullish, google_search_bearish,
        reddit_bullish, reddit_bearish,
        youtube_bullish, youtube_bearish,
        news_bullish, news_bearish)

    # Visualization
    visualize_charts(macro_bullish, macro_bearish, order_book_bullish, order_book_bearish, prediction_bullish,
                     prediction_bearish, technical_bullish, technical_bearish, richest_addresses_bullish,
                     richest_addresses_bearish, google_search_bullish, google_search_bearish, reddit_bullish,
                     reddit_bearish, youtube_bullish, youtube_bearish, news_bullish, news_bearish,
                     weighted_score_up, weighted_score_down)

    # visualize database
    visualize_database_two_rows()
    # Trading decision
    if weighted_score_up > weighted_score_down and weighted_score_up > long_threshold:
        logging.info('Opening a long position')
        profit_after_trade, loss_after_trade = long_position()
        logging.info(f"profit_after_trade:{profit_after_trade}, loss_after_trade:"
                     f"{loss_after_trade}")

    elif weighted_score_down > weighted_score_up and weighted_score_down > short_threshold:
        logging.info('Opening short position')
        profit_after_trade, loss_after_trade = short_position()
        logging.info(f"profit_after_trade:{profit_after_trade}, "f"loss_after_trade:{loss_after_trade}")

    sleep(20 * 60)
