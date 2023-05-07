import logging
from time import sleep
from multiprocessing import Process
import datetime
import time
import pandas as pd

from database import read_database
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
from new_long_position_open import long_position
from new_short_position_open import short_position
from factors_states_visualization import visualize_charts
from database_visualization import visualize_database_one_chart, visualize_trade_results

# Constants
SYMBOLS = ['BTCUSDT', 'BTCBUSD']
LONG_THRESHOLD = 0.65
SHORT_THRESHOLD = 0.65
SCORE_MARGIN_TO_CLOSE = 0.65
PROFIT_MARGIN = 0.01
VISUALIZATION_SLEEP_TIME = 20 * 60
TRADE_RESULT_PATH = 'data/trades_results.csv'
TRADE_DETAILS_PATH = 'data/trades_details.csv'


logging.basicConfig(filename='trading.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def save_trade_details(model_name: str, trade_open_time: str, trade_close_time: str, pnl: float):
    # Read the existing trade details CSV
    df = pd.read_csv(TRADE_DETAILS_PATH)

    # Create a new row with the provided trade details
    new_row = {
        'model_name': model_name,
        'trade_open_time': trade_open_time,
        'trade_close_time': trade_close_time,
        'PNL': pnl
    }

    # Append the new row to the DataFrame
    df = df.append(new_row, ignore_index=True)

    # Save the updated DataFrame to the CSV file
    df.to_csv(TRADE_DETAILS_PATH, index=False)


def save_trade_result(pnl: float, model_name: str):
    df = pd.read_csv(TRADE_RESULT_PATH)

    # Locate the row with the specific model_name
    row_index = df[df['model_name'] == model_name].index[0]

    # Update the number_of_trades and PNL values for the specific model
    df.loc[row_index, 'number_of_trades'] += 1
    df.loc[row_index, 'PNL'] += pnl

    # Save the updated DataFrame to the CSV file
    df.to_csv(TRADE_RESULT_PATH, index=False)


def run_visualize_factors_states():
    while True:
        database = read_database()

        shared_data = dict({
            'macro_bullish': database['macro_bullish'][-1],
            'macro_bearish': database['macro_bearish'][-1],
            'order_book_bullish': database['order_book_bullish'][-1],
            'order_book_bearish': database['order_book_bearish'][-1],
            'prediction_bullish': database['prediction_bullish'][-1],
            'prediction_bearish': database['prediction_bearish'][-1],
            'technical_bullish': database['technical_bullish'][-1],
            'technical_bearish': database['technical_bearish'][-1],
            'richest_addresses_bullish': database['richest_addresses_bullish'][-1],
            'richest_addresses_bearish': database['richest_addresses_bearish'][-1],
            'google_search_bullish': database['google_search_bullish'][-1],
            'google_search_bearish': database['google_search_bearish'][-1],
            'reddit_bullish': database['reddit_bullish'][-1],
            'reddit_bearish': database['reddit_bearish'][-1],
            'youtube_bullish': database['youtube_bullish'][-1],
            'youtube_bearish': database['youtube_bearish'][-1],
            'news_bullish': database['news_bullish'][-1],
            'news_bearish': database['news_bearish'][-1],
            'weighted_score_up': database['weighted_score_up'][-1],
            'weighted_score_down': database['weighted_score_down'][-1],
        })
        visualize_charts(shared_data)
        sleep(VISUALIZATION_SLEEP_TIME)  # Update visualization every 20 minutes


def run_visualize_database():
    while True:
        visualize_database_one_chart(run_dash=True)
        sleep(VISUALIZATION_SLEEP_TIME)  # Update visualization every 20 minutes


def run_visualize_trade_result():
    while True:
        visualize_trade_results(run_dash=True)
        sleep(VISUALIZATION_SLEEP_TIME)  # Update visualization every 20 minutes


def trading_loop(long_threshold: float, short_threshold: float,
                 score_margin_to_close: float, profit_margin: float, model_name: str):
    LOOP_COUNTER = 0
    # Main trading loop
    while True:
        LOOP_COUNTER += 1
        logging.info(f'Model run with threshold:{long_threshold} LOOP_COUNTER: {LOOP_COUNTER}')

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
            logging.info('Opening a long position')
            trade_open_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            profit_after_trade, loss_after_trade = long_position(score_margin_to_close, profit_margin)
            pnl = profit_after_trade - loss_after_trade
            trade_close_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            save_trade_result(pnl, model_name)
            save_trade_details(model_name, trade_open_time, trade_close_time, pnl)

            logging.info(f"profit_after_trade:{profit_after_trade}, loss_after_trade:"
                         f"{loss_after_trade}")

        elif weighted_score_down > weighted_score_up and weighted_score_down > short_threshold:
            logging.info('Opening short position')
            trade_open_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            profit_after_trade, loss_after_trade = short_position(score_margin_to_close, profit_margin)
            pnl = profit_after_trade - loss_after_trade
            trade_close_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            save_trade_result(pnl, model_name)
            save_trade_details(model_name, trade_open_time, trade_close_time, pnl)

            logging.info(f"profit_after_trade:{profit_after_trade}, "f"loss_after_trade:{loss_after_trade}")
        logging.info('End of loop and sleeping')
        sleep(20 * 60)


if __name__ == "__main__":
    # Start visualization processes
    visualization_process = Process(target=run_visualize_database)
    visualization_process.start()

    visualization_charts_process = Process(target=run_visualize_factors_states)
    visualization_charts_process.start()

    visualization_trade_result_process = Process(target=run_visualize_trade_result)
    visualization_trade_result_process.start()

    models = {
        'model1': [0.65, 0.65, 0.65, 0.1, 'model1'],
        'model2': [0.70, 0.70, 0.70, 0.1, 'model2'],
        'model3': [0.75, 0.75, 0.75, 0.1, 'model3'],
        'model4': [0.80, 0.80, 0.80, 0.1, 'model4'],
        'model5': [0.85, 0.85, 0.85, 0.1, 'model5']
    }

    # Run models
    for i in range(1, 6):
        process = Process(target=trading_loop, args=(models[f'model{i}']))
        process.start()
        time.sleep(60)
