from time import sleep
import logging
from datetime import datetime

from a_config import position, factor_values_position, SHORT_POSITION
from z_read_write_csv import retrieve_latest_factor_values_database
from b_order_book import order_book, order_book_hit_target
from a_macro import macro_sentiment, print_upcoming_events
from d_technical import technical_analyse
from i_news_analyser import check_sentiment_of_news
from f_google import check_search_trend
from g_reddit import reddit_check
from h_youtube import check_bitcoin_youtube_videos_increase
from c_predictor import decision_tree_predictor
from l_position_decision import position_decision
from z_handy_modules import get_bitcoin_future_market_price


SYMBOL = 'BTCUSDT'
SYMBOLS = ['BTCUSDT', 'BTCBUSD']
MARGIN_MODE = 'isolated'


def short_position() -> dict:
    current_price = get_bitcoin_future_market_price()
    position['opening_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    position['opening_price'] = current_price
    position['profit_target'] = int(current_price - (current_price * SHORT_POSITION['PROFIT_MARGIN']))
    position['stop_loss'] = int(current_price + (current_price * SHORT_POSITION['PROFIT_MARGIN']))
    position['type'] = 'short'

    # Remind upcoming macro events
    macro_bullish_na, events_date_dict = macro_sentiment()
    print_upcoming_events(events_date_dict)

    while True:
        logging.info(f'███short_position RUNNING ███')

        factor_values_position['macro'], events_date_dict = macro_sentiment()

        factor_values_position['order'] = order_book(SYMBOLS, bid_multiplier=0.99, ask_multiplier=1.01)

        factor_values_position['order_target'] = order_book_hit_target(
            SYMBOLS, 1000, position['stop_loss'], position['profit_target'])

        factor_values_position['prediction'] = decision_tree_predictor()

        factor_values_position['richest'] = retrieve_latest_factor_values_database('richest_addresses')

        factor_values_position['technical'] = technical_analyse()

        factor_values_position['reddit'] = reddit_check()

        factor_values_position['youtube'] = check_bitcoin_youtube_videos_increase()

        factor_values_position['news'] = check_sentiment_of_news()

        factor_values_position['google'] = check_search_trend(["Bitcoin", "Cryptocurrency"])

        # position decision
        weighted_score = position_decision(factor_values_position)

        price = get_bitcoin_future_market_price()
        logging.info(f'Price:{price},PNL:{position["opening_price"]- price} '
                     f'target:{position["profit_target"]}, stop:{position["stop_loss"]}')
        if price <= position['profit_target'] or price > position['stop_loss'] or \
                weighted_score > SHORT_POSITION['THRESHOLD_TO_CLOSE']:

            position['PNL'] = int(price - position['opening_price'])
            logging.info('&&&&&&&&&&&&&& SHORT CLOSED &&&&&&&&&&&&&&&&&&&&')
            position['closing_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            position['closing_price'] = price
            position['closing_score'] = weighted_score

            return position

        logging.info(f'███ short_position SLEEPS ███')
        sleep(SHORT_POSITION['LOOP_SLEEP_TIME'])


if __name__ == "__main__":
    position = short_position()
    logging.info(f"profit_after_trade:{position['PNL']}")
