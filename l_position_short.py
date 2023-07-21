from time import sleep
from typing import Tuple
import logging

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
from l_position_short_testnet import short_market, close_shorts_open_positions

SCORE_MARGIN_TO_CLOSE_OUTER = 0.68
PROFIT_MARGIN = 0.01
SYMBOL = 'BTCUSDT'
SYMBOLS = ['BTCUSDT', 'BTCBUSD']
POSITION_SIZE = 0.01
LEVERAGE = 10
MARGIN_MODE = 'isolated'
TRADING_LOOP_SLEEP_TIME = 60 * 5


def short_position(score_margin_to_close: float, profit_margin: float) -> Tuple[int, int]:

    current_price = get_bitcoin_future_market_price()
    position_opening_price = current_price
    profit_point = int(current_price - (current_price * profit_margin))
    stop_loss = int(current_price + (current_price * profit_margin))
    profit, loss = 0, 0

    # Remind upcoming macro events
    macro_bullish_NA, macro_bearish_NA, events_date_dict = macro_sentiment()
    print_upcoming_events(events_date_dict)

    # Place an order on testnet
    short_market(POSITION_SIZE, LEVERAGE, MARGIN_MODE)  # 5x leverage and isolated margin mode

    while True:
        current_price = get_bitcoin_future_market_price()

        # Check if we meet profit or stop loss
        if current_price < profit_point:
            close_shorts_open_positions(SYMBOL)
            profit = int(position_opening_price - current_price) * LEVERAGE
            logging.info('&&&&&&&&&&&&&& TARGET HIT &&&&&&&&&&&&&&&&&&&&&')
            return profit, loss
        elif current_price > stop_loss:
            close_shorts_open_positions(SYMBOL)
            loss = int(current_price - position_opening_price) * LEVERAGE
            logging.info('&&&&&&&&&&&&&& STOP LOSS &&&&&&&&&&&&&&&&&&&&&')
            return profit, loss

        # order  book Hit
        probability_to_hit_stop_loss, probability_to_hit_target = \
            order_book_hit_target(SYMBOLS, 1000, stop_loss, profit_point)

        prediction_bullish, prediction_bearish = decision_tree_predictor()

        order_book_bullish, order_book_bearish = \
            order_book(SYMBOLS, bid_multiplier=0.99, ask_multiplier=1.01)

        richest_addresses_bullish, richest_addresses_bearish = \
            retrieve_latest_factor_values_database('richest_addresses')

        google_search_bullish, google_search_bearish = check_search_trend(["Bitcoin", "Cryptocurrency"])

        macro_bullish, macro_bearish, events_date_dict = macro_sentiment()

        reddit_bullish, reddit_bearish = reddit_check()

        youtube_bullish, youtube_bearish = check_bitcoin_youtube_videos_increase()

        news_bullish, news_bearish = check_sentiment_of_news()

        technical_bullish, technical_bearish = technical_analyse()

        # position decision
        weighted_score_up, weighted_score_down = position_decision(
            macro_bullish, macro_bearish,
            order_book_bullish, order_book_bearish,
            probability_to_hit_target, probability_to_hit_stop_loss,
            prediction_bullish, prediction_bearish,
            technical_bullish, technical_bearish,
            richest_addresses_bullish, richest_addresses_bearish,
            google_search_bullish, google_search_bearish,
            reddit_bullish, reddit_bearish,
            youtube_bullish, youtube_bearish,
            news_bullish, news_bearish)

        if weighted_score_up > weighted_score_down and weighted_score_up > score_margin_to_close:
            logging.info('short position clos')
            close_shorts_open_positions(SYMBOL)
            if current_price < position_opening_price:
                profit = int(position_opening_price - current_price) * LEVERAGE
                logging.info('short position closed with profit')
            elif current_price >= position_opening_price:
                loss = int(current_price - position_opening_price) * LEVERAGE
                logging.info('short position closed with loss')
            return profit, loss
        sleep(TRADING_LOOP_SLEEP_TIME)


if __name__ == "__main__":
    profit_after_trade_outer, loss_after_trade_outer = short_position(SCORE_MARGIN_TO_CLOSE_OUTER, PROFIT_MARGIN)
    logging.info(f"profit_after_trade:{profit_after_trade_outer}, loss_after_trade:{loss_after_trade_outer}")
