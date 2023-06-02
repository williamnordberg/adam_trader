import logging
from time import sleep
from multiprocessing import Process
import datetime

from handy_modules import compare_send_receive_richest_addresses, get_bitcoin_price, \
    save_trade_details, save_trade_result, save_trading_state,\
    calculate_score_margin, compare_send_receive_richest_addresses_wrapper
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
from database_visualization import visualize_database_one_chart, visualize_trade_results
from testnet_future_short_trade import check_no_open_future_position
from monitor_richest import monitor_bitcoin_richest_addresses
from database import save_value_to_database

# Constants
SYMBOLS = ['BTCUSDT', 'BTCBUSD']
SYMBOL = 'BTCUSDT'
LONG_THRESHOLD = 0.65
SHORT_THRESHOLD = 0.65
SCORE_MARGIN_TO_CLOSE = 0.65
PROFIT_MARGIN = 0.005
RICHEST_ADDRESSES_SLEEP_TIME = 20 * 60

logging.basicConfig(filename='trading.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def run_visualize_factors_states():
    visualize_charts()


def run_visualize_database():
    while True:
        visualize_database_one_chart(run_dash=True)


def run_visualize_trade_result():
    while True:
        visualize_trade_results()


def run_monitor_richest_addresses():
    while True:
        total_received, total_sent = monitor_bitcoin_richest_addresses()

        richest_addresses_bullish, richest_addresses_bearish = compare_send_receive_richest_addresses_wrapper()

        # Save to database
        save_value_to_database('richest_addresses_bullish', richest_addresses_bullish)
        save_value_to_database('richest_addresses_bearish', richest_addresses_bearish)

        logging.info(f'300 Richest addresses sent: {int(total_sent)} and receive: {int(total_received)} in last 24h')
        sleep(RICHEST_ADDRESSES_SLEEP_TIME)


def trading_loop(long_threshold: float, short_threshold: float, profit_margin: float):
    LOOP_COUNTER = 0
    while True:
        LOOP_COUNTER += 1
        logging.info(f'threshold:{long_threshold} and loop counter: {LOOP_COUNTER} RUNS')
        save_trading_state('main')

        # 1 Get the prediction
        prediction_bullish, prediction_bearish = decision_tree_predictor()

        # 2 Order book
        probabilities = get_probabilities(SYMBOLS, bid_multiplier=0.99, ask_multiplier=1.01)
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

        # Trading decision
        if weighted_score_up > weighted_score_down and weighted_score_up > long_threshold:
            logging.info(f'Opening a long position with score of: {weighted_score_up}')
            trade_open_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            opening_price = get_bitcoin_price()
            score_margin_to_close = calculate_score_margin(weighted_score_up)

            save_trading_state('long')
            profit_after_trade, loss_after_trade = long_position(score_margin_to_close, profit_margin)
            pnl = profit_after_trade - loss_after_trade
            trade_close_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            close_price = get_bitcoin_price()

            save_trade_result(pnl, weighted_score_up, 'long')
            save_trade_details(weighted_score_up, trade_open_time,
                               trade_close_time, 'long', opening_price, close_price, pnl)
            logging.info(f"profit_after_trade:{profit_after_trade}, loss_after_trade:"
                         f"{loss_after_trade}")

        elif weighted_score_down > weighted_score_up and weighted_score_down > short_threshold and \
                check_no_open_future_position(SYMBOL):
            logging.info(f'Opening short position with score of: {weighted_score_down}')
            trade_open_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            opening_price = get_bitcoin_price()
            score_margin_to_close = calculate_score_margin(weighted_score_down)

            save_trading_state('short')
            profit_after_trade, loss_after_trade = short_position(score_margin_to_close, profit_margin)
            pnl = profit_after_trade - loss_after_trade
            trade_close_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            close_price = get_bitcoin_price()

            save_trade_result(pnl, weighted_score_down, 'short')
            save_trade_details(weighted_score_down, trade_open_time, trade_close_time,
                               'short', opening_price, close_price, pnl)

            logging.info(f"profit_after_trade:{profit_after_trade}, "f"loss_after_trade:{loss_after_trade}")
        logging.info(f'Threshold:{long_threshold} and loop counter: {LOOP_COUNTER} SLEEPS')
        save_trading_state('main')
        sleep(60 * 20)  # Sleep for 20 minutes


if __name__ == "__main__":

    visualization_process = Process(target=run_visualize_database)
    visualization_process.start()
    sleep(2)

    visualization_charts_process = Process(target=run_visualize_factors_states)
    visualization_charts_process.start()
    sleep(2)  # Sleep To let Visualization be complete before next process start

    visualization_trade_result_process = Process(target=run_visualize_trade_result)
    visualization_trade_result_process.start()
    sleep(2)

    process = Process(target=trading_loop, args=[0.65, 0.65, 0.005])
    process.start()
    sleep(60)

    process = Process(target=run_monitor_richest_addresses)
    process.start()
