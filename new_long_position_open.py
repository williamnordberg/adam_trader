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


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


SCORE_MARGIN_TO_CLOSE = 0.65
PROFIT_MARGIN = 0.01
SYMBOLS = ['BTCUSDT', 'BTCBUSD']


def long_position(score_margin_to_close: float, profit_margin: float) -> Tuple[int, int]:
    current_price = get_bitcoin_price()
    position_opening_price = current_price
    profit_point = int(current_price + (current_price * profit_margin))
    stop_loss = int(current_price - (current_price * profit_margin))
    logging.info(f'Current price: {current_price}, Profit point: {profit_point}, Stop loss: {stop_loss}')
    profit, loss = 0, 0

    while True:
        logging.info('******************************************')
        current_price = get_bitcoin_price()
        logging.info(f'Current_price:{current_price}, Profit_point:{profit_point},Stop_loss:{stop_loss}')

        # Check if we meet profit or stop loss
        if current_price >= profit_point:
            profit = int(current_price - position_opening_price)
            logging.info('&&&&&&&&&&&&&& target hit &&&&&&&&&&&&&&&&&&&&&')
            return profit, loss
        elif current_price < stop_loss:
            loss = int(position_opening_price - current_price)
            logging.info('&&&&&&&&&&&&&& STOP LOSS &&&&&&&&&&&&&&&&&&&&&')
            return profit, loss

        # Order book Hit
        probabilities_hit = get_probabilities_hit_profit_or_stop(SYMBOLS, 1000, profit_point, stop_loss)
        assert probabilities_hit is not None, "get_probabilities_hit_profit_or_stop returned None"
        probability_to_hit_target, probability_to_hit_stop_loss = probabilities_hit

        logging.info(f'Profit probability: {round(probability_to_hit_target, 2)}'
                     f' Stop probability: {round(probability_to_hit_stop_loss, 2)}')

        # 1 Get the prediction
        prediction_bullish, prediction_bearish = decision_tree_predictor()

        # 2 Get probabilities of price going up or down
        probabilities = get_probabilities(SYMBOLS, bid_multiplier=0.99, ask_multiplier=1.01)
        assert probabilities is not None, "get_probabilities returned None"
        order_book_bullish, order_book_bearish = probabilities

        # 3 Monitor the richest Bitcoin addresses
        richest_addresses_bullish, richest_addresses_bearish = compare_send_receive_richest_addresses()

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

        # Check if weighed score show high chance to position loss
        if weighted_score_down > weighted_score_up and weighted_score_down > score_margin_to_close:
            logging.info('long position clos')
            if current_price > position_opening_price:
                profit = int(current_price - position_opening_price)
                logging.info('long position closed with profit')
            elif current_price <= position_opening_price:
                loss = int(position_opening_price - current_price)
                logging.info('long position closed with loss')
            return profit, loss

        sleep(60 * 5)


if __name__ == "__main__":
    profit_after_trade, loss_after_trade = long_position(SCORE_MARGIN_TO_CLOSE, PROFIT_MARGIN)
    logging.info(f"profit_after_trade:{profit_after_trade}, loss_after_trade:{loss_after_trade}")
