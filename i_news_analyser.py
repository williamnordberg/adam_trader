import requests.exceptions
import json
from typing import Tuple

from i_newsAPI import check_news_api_sentiment
from i_news_crypto_compare import check_news_cryptocompare_sentiment
from i_news_coin_desk import check_news_coin_desk
from i_news_coin_telegraph import check_news_coin_telegraph

from z_handy_modules import retry_on_error, get_bitcoin_price
from z_compares import compare_news
from z_read_write_csv import save_value_to_database, \
    should_update, save_update_time, retrieve_latest_factor_values_database

# remove last_news_update_time, news_bullish, news_bearish,
# positive_news_polarity_change, negative_percentage_increase  from latest data


ALLOWED_EXCEPTIONS = (requests.exceptions.RequestException, ValueError)


@retry_on_error(max_retries=3, delay=5,
                allowed_exceptions=ALLOWED_EXCEPTIONS, fallback_values='pass')
def update_bitcoin_price_in_database():
    price = get_bitcoin_price()
    save_value_to_database('bitcoin_price', price)


def aggregate_news() -> Tuple[float, float, int, int]:
    """
    Aggregates news sentiment from different sources for the last 24 hours.

    Returns:
        positive_polarity_24_hours_before (float): Average positive polarity score.
        negative_polarity_24_hours_before (float): Average negative polarity score.
        positive_count_24_hours_before (int): Total number of positive news articles.
        negative_count_24_hours_before (int): Total number of negative news articles.
    """

    # Create a list of the functions that will be used to check sentiment
    check_functions = [check_news_api_sentiment, check_news_cryptocompare_sentiment,
                       check_news_coin_desk, check_news_coin_telegraph]

    # Initialize accumulators
    total_positive_polarity, total_negative_polarity, total_positive_count, total_negative_count = 0, 0, 0, 0

    # Loop through the functions, call them, and add their results to the accumulators
    for check_func in check_functions:
        positive_polarity, negative_polarity, positive_count, negative_count = check_func()
        total_positive_polarity += positive_polarity
        total_negative_polarity += negative_polarity
        total_positive_count += positive_count
        total_negative_count += negative_count

    # Compute averages
    num_functions = len(check_functions)
    avg_positive_polarity = round(total_positive_polarity / num_functions, 2)
    avg_negative_polarity = round(total_negative_polarity / num_functions, 2)
    avg_positive_count = total_positive_count // num_functions
    avg_negative_count = total_negative_count // num_functions

    return avg_positive_polarity, avg_negative_polarity, avg_positive_count, avg_negative_count


@retry_on_error(3, 5, (requests.exceptions.RequestException,
                       json.JSONDecodeError, ValueError, KeyError), (0.0, 0.0))
def check_sentiment_of_news_wrapper() -> Tuple[float, float]:

    # We need to update Bitcoin price hourly (same as news)
    update_bitcoin_price_in_database()

    # Get aggregated value from 3 function for las 24 hours
    last_24_hours_positive_polarity, last_24_hours_negative_polarity,\
        positive_count_24_hours_before, negative_count_24_hours_before = aggregate_news()

    news_bullish, news_bearish = compare_news(last_24_hours_positive_polarity, last_24_hours_negative_polarity,
                                              positive_count_24_hours_before, negative_count_24_hours_before)

    # Save data on database
    save_value_to_database('news_positive_polarity', round(last_24_hours_positive_polarity, 2))
    save_value_to_database('news_negative_polarity', round(last_24_hours_negative_polarity, 2))
    save_value_to_database('news_positive_count', positive_count_24_hours_before)
    save_value_to_database('news_negative_count', negative_count_24_hours_before)

    save_update_time('sentiment_of_news')

    return news_bullish, news_bearish


def check_sentiment_of_news() -> Tuple[float, float]:
    if should_update('sentiment_of_news'):
        news_bullish, news_bearish = check_sentiment_of_news_wrapper()
        save_value_to_database('news_bullish', news_bullish)
        save_value_to_database('news_bearish', news_bearish)
        return news_bullish, news_bearish
    else:
        return retrieve_latest_factor_values_database('news')


if __name__ == "__main__":
    news_bullish_outer, news_bearish_outer = check_sentiment_of_news_wrapper()
    print(f'news_bullish: {news_bullish_outer}, and news_bearish: {news_bearish_outer}')
