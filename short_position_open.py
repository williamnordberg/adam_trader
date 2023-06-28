from time import sleep
import logging
from typing import Tuple

from b_order_book import order_book, order_book_hit_target
from a_macro import macro_sentiment, print_upcoming_events
from d_technical import technical_analyse
from i_news_analyser import check_sentiment_of_news
from f_google import check_search_trend
from g_reddit import reddit_check
from h_youtube import check_bitcoin_youtube_videos_increase
from c_predictor import decision_tree_predictor
from position_decision_maker import position_decision
from z_handy_modules import get_bitcoin_future_market_price
from testnet_future_short_trade import short_market, close_shorts_open_positions, get_open_futures_positions
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

SCORE_MARGIN_TO_CLOSE_OUTER = 0.68
PROFIT_MARGIN = 0.005
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

    # Place an order on testnet
    short_market(POSITION_SIZE, LEVERAGE, MARGIN_MODE)  # 5x leverage and isolated margin mode

    while True:
        logging.info('******************************************')
        current_price = get_bitcoin_future_market_price()
        logging.info(f'current_price:{current_price}, PNL:{position_opening_price-current_price}'
                     f' profit_point:{profit_point},stop_loss:{stop_loss} ')

        # Check if we meet profit or stop loss
        if current_price < profit_point:
            close_shorts_open_positions(SYMBOL)
            profit = int(position_opening_price - current_price)
            logging.info('&&&&&&&&&&&&&& TARGET HIT &&&&&&&&&&&&&&&&&&&&&')
            return profit, loss
        elif current_price > stop_loss:
            close_shorts_open_positions(SYMBOL)
            loss = int(current_price - position_opening_price)
            logging.info('&&&&&&&&&&&&&& STOP LOSS &&&&&&&&&&&&&&&&&&&&&')
            return profit, loss

        # order  book Hit
        probabilities_hit = order_book_hit_target(SYMBOLS, 1000, stop_loss, profit_point)
        assert probabilities_hit is not None, "get_probabilities_hit_profit_or_stop returned None"
        probability_to_hit_stop_loss, probability_to_hit_target = probabilities_hit

        logging.info(f'profit_probability: {probability_to_hit_target}'
                     f'stop_probability: {probability_to_hit_stop_loss}')

        # 1 Get the prediction
        prediction_bullish, prediction_bearish = decision_tree_predictor()

        # 2 Get probabilities of price going up or down
        probabilities = order_book(SYMBOLS, bid_multiplier=0.99, ask_multiplier=1.01)
        assert probabilities is not None, "get_probabilities returned None"
        order_book_bullish, order_book_bearish = probabilities

        # 3 Monitor the richest Bitcoin addresses
        richest_addresses_bullish, richest_addresses_bearish = richest_addresses_()

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

        logging.info(f'weighted_score_up: {round(weighted_score_up, 2)}, '
                     f'weighted_score_down: {round(weighted_score_down, 2)}')

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
        get_open_futures_positions()
        sleep(TRADING_LOOP_SLEEP_TIME)


if __name__ == "__main__":
    profit_after_trade_outer, loss_after_trade_outer = short_position(SCORE_MARGIN_TO_CLOSE_OUTER, PROFIT_MARGIN)
    logging.info(f"profit_after_trade:{profit_after_trade_outer}, loss_after_trade:{loss_after_trade_outer}")
