# Logging config must be in begen of first import to inherit
from a_a_logging_config import do_nothing
import logging
from time import sleep
from multiprocessing import Process
from datetime import datetime
import signal
import sys
import os

from z_handy_modules import get_bitcoin_price, calculate_score_margin
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
from l_position_short_testnet import check_no_open_future_position
from e_richest import monitor_bitcoin_richest_addresses
from z_read_write_csv import retrieve_latest_factor_values_database, \
    save_value_to_database, write_latest_data, save_trade_details, save_trade_result


# Constants
SYMBOLS = ['BTCUSDT', 'BTCBUSD']
SYMBOL = 'BTCUSDT'
LONG_THRESHOLD = 0.68
SHORT_THRESHOLD = 0.70
PROFIT_MARGIN = 0.005
RICHEST_ADDRESSES_SLEEP_TIME = 20 * 60
MAIN_TRADING_LOOP_SLEEP_TIME = 20 * 60


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
            richest_addresses_bullish, richest_addresses_bearish = compare_richest_addresses()

            # Save to database
            save_value_to_database('richest_addresses_bullish', richest_addresses_bullish)
            save_value_to_database('richest_addresses_bearish', richest_addresses_bearish)

            logging.info(f'♥♥♥♥ Richest Send: {total_sent} '
                         f' RECEIVE: {total_received} in 24H ♥♥♥♥')

        logging.info(f'♥♥♥♥ {os.getpid()}_Rich addresses({RICH_LOOP_COUNTER}) SLEEPS ♥♥♥♥')
        sleep(RICHEST_ADDRESSES_SLEEP_TIME)


# noinspection PyDictCreation
def trading_loop(long_threshold: float, short_threshold: float, profit_margin: float):
    LOOP_COUNTER = 0
    while True:
        LOOP_COUNTER += 1
        logging.info(f'███ {os.getpid()}_trading({LOOP_COUNTER}) RUNNING ███')
        write_latest_data('latest_trading_state', 'main')
        factor_values = {
            'macro': 0.0,
            'order_book': 0.0,
            'prediction': 0.0,
            'technical': 0.0,
            'richest': 0.0,
            'google': 0.0,
            'reddit': 0.0,
            'youtube': 0.0,
            'news': 0.0
        }

        factor_values['macro'], events_date_dict = macro_sentiment()
        print_upcoming_events(events_date_dict)

        factor_values['prediction_bullish'], factor_values['prediction_bearish'] = decision_tree_predictor()

        factor_values['order_book_bullish'], factor_values['order_book_bearish'] =\
            order_book(SYMBOLS, bid_multiplier=0.99, ask_multiplier=1.01)


        factor_values['richest_bullish'], factor_values['richest_bearish'] = \
            retrieve_latest_factor_values_database('richest_addresses')

        factor_values['google_bullish'], factor_values['google_bearish'] = \
            check_search_trend(["Bitcoin", "Cryptocurrency"])

        factor_values['reddit_bullish'], factor_values['reddit_bearish'] = reddit_check()

        factor_values['youtube_bullish'], factor_values['youtube_bearish'] = check_bitcoin_youtube_videos_increase()

        factor_values['news_bullish'], factor_values['news_bearish'] = check_sentiment_of_news()

        factor_values['technical_bullish'], factor_values['technical_bearish'] = technical_analyse()

        # Make decision about the trade
        weighted_score_up, weighted_score_down = make_trading_decision(factor_values)
        factor_values['weighted_score_up'] = weighted_score_up
        factor_values['weighted_score_down'] = weighted_score_down

        # Trading decision
        if weighted_score_up > weighted_score_down and weighted_score_up > long_threshold:
            logging.info(f'Opening a long position with score of: {weighted_score_up}')
            trade_open_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            opening_price = get_bitcoin_price()
            score_margin_to_close = calculate_score_margin(weighted_score_up)

            write_latest_data('latest_trading_state', 'long')
            profit_after_trade, loss_after_trade = long_position(score_margin_to_close, profit_margin)
            pnl = profit_after_trade - loss_after_trade
            trade_close_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            close_price = get_bitcoin_price()

            save_trade_result(pnl, weighted_score_up, 'long')
            save_trade_details(weighted_score_up, trade_open_time,
                               trade_close_time, 'long', opening_price, close_price, pnl, factor_values)
            logging.info(f"profit_after_trade:{profit_after_trade}, loss_after_trade:"
                         f"{loss_after_trade}")

        elif weighted_score_down > weighted_score_up and weighted_score_down > short_threshold and \
                check_no_open_future_position(SYMBOL):
            logging.info(f'Opening short position with score of: {weighted_score_down}')
            trade_open_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            opening_price = get_bitcoin_price()
            score_margin_to_close = calculate_score_margin(weighted_score_down)

            write_latest_data('latest_trading_state', 'short')
            profit_after_trade, loss_after_trade = short_position(score_margin_to_close, profit_margin)
            pnl = profit_after_trade - loss_after_trade
            trade_close_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            close_price = get_bitcoin_price()

            save_trade_result(pnl, weighted_score_down, 'short')
            save_trade_details(weighted_score_down, trade_open_time, trade_close_time,
                               'short', opening_price, close_price, pnl, factor_values)

            logging.info(f"profit_after_trade:{profit_after_trade}, "f"loss_after_trade:{loss_after_trade}")
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

    main_trading_loop_process = Process(target=trading_loop, args=[LONG_THRESHOLD, SHORT_THRESHOLD, PROFIT_MARGIN])
    main_trading_loop_process.start()
    sleep(60)

    rich_addresses_process = Process(target=run_monitor_richest_addresses)
    rich_addresses_process.start()
