from time import sleep
import logging
from typing import Tuple

from order_book import get_probabilities, get_probabilities_hit_profit_or_stop
from macro_analyser import macro_sentiment, print_upcoming_events
from technical_analysis import technical_analyse
from news_analyser import check_sentiment_of_news
from google_search import check_search_trend
from reddit import reddit_check
from youtube import check_bitcoin_youtube_videos_increase
from adam_predictor import decision_tree_predictor
from position_decision_maker import position_decision
from handy_modules import get_bitcoin_price, compare_send_receive_richest_addresses
from database import save_value_to_database

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

SCORE_MARGIN_TO_CLOSE = 0.7
PROFIT_MARGIN = 0.01
SYMBOLS = ['BTCUSDT', 'BTCBUSD']
LATEST_INFO_FILE = 'latest_info_saved.csv'


def short_position() -> Tuple[int, int]:
    """
       Monitors a short position for various factors to decide when to close the position.
       The function continuously checks various factors like probabilities, technical analysis,
       news sentiment, search trends, Reddit activity, and YouTube trends.
       It also checks for stop loss and profit points.
       Returns:
           float: The profit made after closing the position.
           float: The loss made after closing the position.
       """
    current_price = get_bitcoin_price()
    position_opening_price = current_price
    profit_point = current_price - (current_price * PROFIT_MARGIN)
    stop_loss = current_price + (current_price * PROFIT_MARGIN)
    logging.info(f'current_price:{current_price}, profit_point:{profit_point},stop_loss:{stop_loss} ')
    profit, loss = 0, 0

    while True:
        logging.info('******************************************')
        current_price = get_bitcoin_price()
        logging.info(f'current_price:{current_price}, profit_point:{profit_point},stop_loss:{stop_loss} ')
        # Check if we meet profit or stop loss
        if current_price < profit_point:
            profit = position_opening_price - current_price
            logging.info('&&&&&&&&&&&&&& TARGET HIT &&&&&&&&&&&&&&&&&&&&&')
            return profit, loss
        elif current_price > stop_loss:
            loss = current_price - position_opening_price
            logging.info('&&&&&&&&&&&&&& STOP LOSS &&&&&&&&&&&&&&&&&&&&&')
            return profit, loss

        # order  book Hit
        probabilities_hit = get_probabilities_hit_profit_or_stop(SYMBOLS, 1000, stop_loss, profit_point)
        assert probabilities_hit is not None, "get_probabilities_hit_profit_or_stop returned None"
        probability_to_hit_stop_loss, probability_to_hit_target = probabilities_hit

        logging.info(f'profit_probability: {probability_to_hit_target}'
                     f'stop_probability: {probability_to_hit_stop_loss}')

        # 1 Get the prediction
        prediction_bullish, prediction_bearish = decision_tree_predictor()

        # 2 Get probabilities of price going up or down
        probabilities = get_probabilities(SYMBOLS, bid_multiplier=0.99, ask_multiplier=1.01)
        assert probabilities is not None, "get_probabilities returned None"
        order_book_bullish, order_book_bearish = probabilities

        logging.info(f'order_book_bullish: {order_book_bullish}'
                     f'  order_book_bearish: {order_book_bearish}')

        # 3 Monitor the richest Bitcoin addresses
        richest_addresses_bullish, richest_addresses_bearish = compare_send_receive_richest_addresses()

        # Save to database
        save_value_to_database('richest_addresses_bullish', richest_addresses_bullish)
        save_value_to_database('richest_addresses_bearish', richest_addresses_bearish)

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

        print('weighted_score_up, weighted_score_down', weighted_score_up, weighted_score_down)

        if weighted_score_up > weighted_score_down and weighted_score_up > SCORE_MARGIN_TO_CLOSE:
            logging.info('short position clos')
            if current_price < position_opening_price:
                profit = position_opening_price - current_price
                logging.info('short position closed with profit')
            elif current_price > position_opening_price:
                loss = position_opening_price - current_price
                logging.info('short position closed with loss')
            return profit, loss

        sleep(5)


if __name__ == "__main__":
    profit_after_trade1, loss_after_trade1 = short_position()
    logging.info(f"profit_after_trade:{profit_after_trade1}, loss_after_trade:{loss_after_trade1}")
