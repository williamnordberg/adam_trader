from time import sleep
import logging
from typing import Tuple

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
from z_handy_modules import get_bitcoin_price
from l_position_long_testnet import place_market_buy_order, close_position_at_market, get_btc_open_positions

SCORE_MARGIN_TO_CLOSE = 0.65
PROFIT_MARGIN = 0.01
SYMBOLS = ['BTCUSDT', 'BTCBUSD']
POSITION_SIZE = 0.3
TRADING_LOOP_SLEEP_TIME = 60 * 5


def long_position(score_margin_to_close: float, profit_margin: float) -> Tuple[int, int]:
    current_price = get_bitcoin_price()
    position_opening_price = current_price
    profit_point = int(current_price + (current_price * profit_margin))
    stop_loss = int(current_price - (current_price * profit_margin))
    profit, loss = 0, 0

    # Place order o spot testnet
    place_market_buy_order(POSITION_SIZE)

    while True:
        current_price = get_bitcoin_price()
        logging.info(f'Current_price:{current_price},PNL:{current_price-position_opening_price} '
                     f'Profit_point:{profit_point},Stop_loss:{stop_loss}')

        # Check if we meet profit or stop loss
        if current_price >= profit_point:
            close_position_at_market(POSITION_SIZE)
            profit = int(current_price - position_opening_price)
            logging.info('&&&&&&&&&&&&&& target hit &&&&&&&&&&&&&&&&&&&&&')
            return profit, loss
        elif current_price < stop_loss:
            close_position_at_market(POSITION_SIZE)
            loss = int(position_opening_price - current_price)
            logging.info('&&&&&&&&&&&&&& STOP LOSS &&&&&&&&&&&&&&&&&&&&&')
            return profit, loss

        # Order book Hit
        probabilities_hit = order_book_hit_target(SYMBOLS, 1000, profit_point, stop_loss)
        assert probabilities_hit is not None, "get_probabilities_hit_profit_or_stop returned None"
        probability_to_hit_target, probability_to_hit_stop_loss = probabilities_hit

        logging.info(f'Profit probability: {round(probability_to_hit_target, 1)}'
                     f' Stop probability: {round(probability_to_hit_stop_loss, 1)}')

        # 1 Get the prediction
        prediction_bullish, prediction_bearish = decision_tree_predictor()

        # 2 Get probabilities of price going up or down
        probabilities = order_book(SYMBOLS, bid_multiplier=0.99, ask_multiplier=1.01)
        assert probabilities is not None, "get_probabilities returned None"
        order_book_bullish, order_book_bearish = probabilities

        # 3 Monitor the richest Bitcoin addresses
        richest_addresses_bullish, richest_addresses_bearish = \
            retrieve_latest_factor_values_database('richest_addresses')

        # 4 Check Google search trends for Bitcoin and cryptocurrency
        google_search_bullish, google_search_bearish = check_search_trend(["Bitcoin", "Cryptocurrency"])

        # 5 Check macroeconomic indicators
        macro_bullish, macro_bearish, events_date_dict = macro_sentiment()

        # remind upcoming macro events
        print_upcoming_events(events_date_dict)

        # 6 Reddit
        reddit_bullish, reddit_bearish = reddit_check()

        # 7 YouTube
        youtube_bullish, youtube_bearish = check_bitcoin_youtube_videos_increase()

        # 8 Collect data from news websites
        news_bullish, news_bearish = check_sentiment_of_news()

        # 9 Technical analysis
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

        # Check if weighed score show high chance to position loss
        if weighted_score_down > weighted_score_up and weighted_score_down > score_margin_to_close:
            close_position_at_market(POSITION_SIZE)
            if current_price > position_opening_price:
                profit = int(current_price - position_opening_price)
                logging.info('long position closed with profit')
                return profit, loss
            elif current_price <= position_opening_price:
                loss = int(position_opening_price - current_price)
                logging.info('long position closed with loss')
                return profit, loss
        get_btc_open_positions()
        sleep(TRADING_LOOP_SLEEP_TIME)


if __name__ == "__main__":
    profit_after_trade, loss_after_trade = long_position(SCORE_MARGIN_TO_CLOSE, PROFIT_MARGIN)
    logging.info(f"profit_after_trade:{profit_after_trade}, loss_after_trade:{loss_after_trade}")
