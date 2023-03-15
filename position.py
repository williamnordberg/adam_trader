from time import sleep
import requests
import pandas as pd
from order_book import get_probabilities, get_probabilities_hit_profit_or_stop
from macro_expected import get_macro_expected_and_real_compare, print_upcoming_events
from technical_analysis import technical_analyse
from news_websites import check_sentiment_of_news
from google_search import check_search_trend
from reddit import reddit_check
from youtube import check_bitcoin_youtube_videos_increase
from adam_predictor import decision_tree_predictor
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
PROFIT_MARGIN = 0.01
SYMBOLS = ['BTCUSDT', 'BTCBUSD']


def get_bitcoin_price():
    """
    Retrieves the current Bitcoin price in USD from the CoinGecko API.
    """
    try:
        url = 'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd'
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            current_price_local = data['bitcoin']['usd']
            return current_price_local
        else:
            logging.error("Error: Could not retrieve Bitcoin price data")
            return 0
    except requests.exceptions.RequestException as e:
        logging.error(f"Error: Could not connect to CoinGecko API:{e}")
        return 0


def long_position_is_open():
    current_price = get_bitcoin_price()
    position_opening_price = current_price
    profit_point = current_price + (current_price * PROFIT_MARGIN)
    stop_loss = current_price - (current_price * PROFIT_MARGIN)
    logging.info(f'current_price:{current_price}, profit_point:{profit_point},stop_loss:{stop_loss} ')
    profit, loss = 0, 0

    while True:
        logging.info('******************************************')
        current_price = get_bitcoin_price()
        logging.info(f'current_price:{current_price}, profit_point:{profit_point},stop_loss:{stop_loss} ')
        # Check if we meet profit or stop loss
        if current_price > profit_point:
            profit = current_price - position_opening_price
            logging.info('&&&&&&&&&&&&&& target hit &&&&&&&&&&&&&&&&&&&&&')
            return profit, loss
        elif current_price < stop_loss:
            loss = position_opening_price - current_price
            logging.info('&&&&&&&&&&&&&& STOP LOSS &&&&&&&&&&&&&&&&&&&&&')
            return profit, loss

        # 1.Order book
        probability_down, probability_up = get_probabilities(
            SYMBOLS, bid_multiplier=0.995, ask_multiplier=1.005)
        logging.info(f'Probability of price down: {probability_down} and up:{probability_up}')

        probability_to_hit_target, probability_to_hit_stop_loss = \
            get_probabilities_hit_profit_or_stop(SYMBOLS, 1000, profit_point, stop_loss)
        logging.info(f'profit:{probability_to_hit_target}stop:{probability_to_hit_stop_loss}')

        # 2. Blockchain monitoring(is the richest addresses accumulating?)
        last_24_accumulation = pd.read_csv('last_24_accumulation.csv')
        total_received, total_sent = last_24_accumulation['total_received']\
            .values[0], last_24_accumulation['total_sent'].values[0]

        # 3. Macroeconomics data
        cpi_better_than_expected, ppi_better_than_expected, interest_rate_better_than_expected, \
            events_dates = get_macro_expected_and_real_compare()

        # remind upcoming macro events
        print_upcoming_events(events_dates)

        # 4. Technical Analysis
        technical_bullish, technical_bearish = technical_analyse()

        # 5.News and Events(positive > negative * 1.6)
        sentiment_of_news = check_sentiment_of_news()

        # 6. Twitter

        # 7.Google search (is that increase?)
        increase_google_search = check_search_trend(["Bitcoin", "Cryptocurrency"], threshold=1.2)

        # 8.Reddit
        current_activity, current_count, activity_increase, count_increase = reddit_check()

        # 9.Youtube
        bitcoin_youtube_increase_15_percent = check_bitcoin_youtube_videos_increase()

        # 10. Adam predictor (is prediction is positive)
        predicted_price = decision_tree_predictor()
        logging.info(f"The predicted price is: {predicted_price}")

        # decision to close long position
        if probability_to_hit_target < 40 or probability_up < 40:
            if total_received < total_sent:
                if technical_bearish:
                    if sentiment_of_news:
                        if not increase_google_search:
                            if not activity_increase or not count_increase:
                                if bitcoin_youtube_increase_15_percent:
                                    if predicted_price < current_price * 1.01:
                                        logging.info('close long position at loss')
                return profit, loss
        sleep(5)


def short_position_is_open():
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

        # 1.Order book
        probability_down, probability_up = get_probabilities(
            SYMBOLS, bid_multiplier=0.995, ask_multiplier=1.005)
        logging.info(f'Probability of price down: {probability_down} and up:{probability_up}')

        probability_to_hit_target, probability_to_hit_stop_loss = \
            get_probabilities_hit_profit_or_stop(SYMBOLS, 1000, profit_point, stop_loss)
        logging.info(f'profit:{probability_to_hit_target}stop:{probability_to_hit_stop_loss}')

        # 2. Blockchain monitoring(is the richest addresses accumulating?)
        last_24_accumulation = pd.read_csv('last_24_accumulation.csv')
        total_received, total_sent = last_24_accumulation['total_received'] \
            .values[0], last_24_accumulation['total_sent'].values[0]

        # 3. Macroeconomics data
        cpi_better_than_expected, ppi_better_than_expected, interest_rate_better_than_expected, \
            events_dates = get_macro_expected_and_real_compare()

        # remind upcoming macro events
        print_upcoming_events(events_dates)

        # 4. Technical Analysis
        technical_bullish, technical_bearish = technical_analyse()

        # 5.News and Events(positive > negative * 1.6)
        sentiment_of_news = check_sentiment_of_news()

        # 6. Twitter
        # TODO

        # 7.Google search (is that increase?)
        increase_google_search = check_search_trend(["Bitcoin", "Cryptocurrency"], threshold=1.2)

        # 8.Reddit
        current_activity, current_count, activity_increase, count_increase = reddit_check()

        # 9.Youtube
        bitcoin_youtube_increase_15_percent = check_bitcoin_youtube_videos_increase()

        # 10. Adam predictor (is prediction is positive)
        predicted_price = decision_tree_predictor()
        logging.info(f"The predicted price is: {predicted_price}")

        # decision to close long position
        if probability_to_hit_target < 40 or probability_up < 40:
            if total_received > total_sent:
                if technical_bullish:
                    if not sentiment_of_news:
                        if increase_google_search:
                            if activity_increase or count_increase:
                                if not bitcoin_youtube_increase_15_percent:
                                    if predicted_price > current_price * 1.01:
                                        logging.info('close short position at loss')
                return profit, loss
        sleep(5)


if __name__ == "__main__":
    profit_after_trade, loss_after_trade = long_position_is_open()
    logging.info(f"profit_after_trade:{profit_after_trade}, loss_after_trade:{loss_after_trade}")
