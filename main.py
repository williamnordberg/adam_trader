# Logging config must be in begen of first import to inherit
from a_a_logging_config import do_nothing
import logging
from time import sleep
from multiprocessing import Process
import signal
import sys
import os

from a_config import (factor_values, LONG_THRESHOLD, SHORT_THRESHOLD,
                      RICHEST_ADDRESSES_SLEEP_TIME, MAIN_TRADING_LOOP_SLEEP_TIME)
from z_compares import compare_richest_addresses
from d_technical import technical_analyse
from i_news_analyser import check_sentiment_of_news
from h_youtube import check_bitcoin_youtube_videos_increase
from g_reddit import reddit_check
from a_macro import macro_sentiment, print_upcoming_events
from f_google import check_search_trend
from c_predictor import decision_tree_predictor
from b_order_book import order_book
from k_combined_score import make_trading_decision
from l_position_long import long_position
from l_position_short import short_position
from m_visual_app import visualize_charts
from e_richest import monitor_bitcoin_richest_addresses
from z_read_write_csv import retrieve_latest_factor_values_database, \
    save_value_to_database, write_latest_data, save_trade_details

SYMBOLS = ['BTCUSDT', 'BTCBUSD']
do_nothing()


def run_visualize_factors_states():
    visualize_charts()


def run_monitor_richest_addresses():
    RICH_LOOP_COUNTER = 0
    while True:
        RICH_LOOP_COUNTER += 1
        logging.info(f'♥♥♥♥ {os.getpid()}_Rich addresses({RICH_LOOP_COUNTER}) RUNNING ♥♥♥♥')
        total_received, total_sent = monitor_bitcoin_richest_addresses()
        if total_received != 0.0:
            richest_addresses_bullish = compare_richest_addresses()

            # Save to database
            save_value_to_database('richest_addresses_bullish', richest_addresses_bullish)

            logging.info(f'♥♥♥♥ Richest Send: {total_sent} '
                         f' RECEIVE: {total_received} in 24H ♥♥♥♥')

        logging.info(f'♥♥♥♥ {os.getpid()}_Rich addresses({RICH_LOOP_COUNTER}) SLEEPS ♥♥♥♥')
        sleep(RICHEST_ADDRESSES_SLEEP_TIME)


# noinspection PyDictCreation
def trading_loop(long_threshold: float, short_threshold: float):
    LOOP_COUNTER = 0
    while True:
        LOOP_COUNTER += 1
        logging.info(f'███ {os.getpid()}_trading({LOOP_COUNTER}) RUNNING ███')
        write_latest_data('latest_trading_state', 'main')

        factor_values['macro'], events_date_dict = macro_sentiment()
        print_upcoming_events(events_date_dict)

        factor_values['order'] = order_book(SYMBOLS, bid_multiplier=0.99, ask_multiplier=1.01)

        factor_values['prediction'] = decision_tree_predictor()

        factor_values['richest'] = retrieve_latest_factor_values_database('richest_addresses')

        factor_values['technical'] = technical_analyse()

        factor_values['reddit'] = reddit_check()

        factor_values['youtube'] = check_bitcoin_youtube_videos_increase()

        factor_values['news'] = check_sentiment_of_news()

        factor_values['google'] = check_search_trend(["Bitcoin", "Cryptocurrency"])

        # Make decision about the trade
        weighted_score = make_trading_decision(factor_values)

        # Trading decision
        if weighted_score > long_threshold:
            logging.info(f'Opening a long position with score of: {weighted_score}')
            write_latest_data('latest_trading_state', 'long')
            position = long_position()
            position['opening_score'] = weighted_score
            save_trade_details(position, factor_values)

        elif weighted_score < short_threshold:
            logging.info(f'Opening short position with score of: {weighted_score}')
            write_latest_data('latest_trading_state', 'short')
            position = short_position()
            position['opening_score'] = weighted_score
            save_trade_details(position, factor_values)

        logging.info(factor_values)
        logging.info(f'███ {os.getpid()}_trading({LOOP_COUNTER}) SLEEPS ███')
        write_latest_data('latest_trading_state', 'main')
        sleep(MAIN_TRADING_LOOP_SLEEP_TIME)


def signal_handler(sig, frame):
    logging.info('Received interrupt signal. Cleaning up...')
    # Stop child processes here.
    visualization_charts_process.terminate()
    rich_addresses_process.terminate()
    main_trading_loop_process.terminate()
    sys.exit(0)


if __name__ == "__main__":
    # Register the signal handler
    signal.signal(signal.SIGINT, signal_handler)

    visualization_charts_process = Process(target=run_visualize_factors_states)
    visualization_charts_process.start()
    sleep(2)

    main_trading_loop_process = Process(target=trading_loop, args=[LONG_THRESHOLD, SHORT_THRESHOLD])
    main_trading_loop_process.start()
    sleep(60)

    rich_addresses_process = Process(target=run_monitor_richest_addresses)
    rich_addresses_process.start()
