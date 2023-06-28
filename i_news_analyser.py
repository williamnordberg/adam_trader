import logging
from datetime import datetime, timedelta
from typing import Tuple
import requests.exceptions
import json


from i_newsAPI import check_news_api_sentiment
from i_news_crypto_compare import check_news_cryptocompare_sentiment
from i_news_scrapper import check_news_sentiment_scrapper

from z_handy_modules import retry_on_error
from z_compares import compare_news
from z_update_bitcoin_price import update_bitcoin_price_in_database
from z_read_write_csv import write_latest_data, save_value_to_database, \
    should_update, save_update_time, retrieve_latest_factor_values_database


# remove last_news_update_time, news_bullish, news_bearish,
# positive_news_polarity_change, negative_percentage_increase  from latest data


def aggregate_news() -> Tuple[float, float, int, int]:
    """
        Aggregates news sentiment from different sources for the last 24 hours.

        Returns:
            positive_polarity_24_hours_before (float): Average positive polarity score.
            negative_polarity_24_hours_before (float): Average negative polarity score.
            positive_count_24_hours_before (int): Total number of positive news articles.
            negative_count_24_hours_before (int): Total number of negative news articles.
        """

    start = datetime.now() - timedelta(days=1)
    end = datetime.now()
    positive_polarity_24_hours_before1, negative_polarity_24_hours_before1, \
        positive_count_24_hours_before1, negative_count_24_hours_before1 = \
        check_news_api_sentiment(start, end)

    positive_polarity_24_hours_before2, negative_polarity_24_hours_before2, \
        positive_count_24_hours_before2, negative_count_24_hours_before2 = \
        check_news_cryptocompare_sentiment()

    positive_polarity_24_hours_before3, negative_polarity_24_hours_before3, \
        positive_count_24_hours_before3, negative_count_24_hours_before3 = \
        check_news_sentiment_scrapper()

    # divide by number of news aggregates
    positive_polarity_24_hours_before = (positive_polarity_24_hours_before1 + positive_polarity_24_hours_before2
                                         + positive_polarity_24_hours_before3) / 3

    negative_polarity_24_hours_before = (negative_polarity_24_hours_before1 + negative_polarity_24_hours_before2
                                         + negative_polarity_24_hours_before3) / 3

    positive_count_24_hours_before = int((positive_count_24_hours_before1 + positive_count_24_hours_before2
                                          + positive_count_24_hours_before3) / 3)

    negative_count_24_hours_before = int((negative_count_24_hours_before1 + negative_count_24_hours_before2
                                          + negative_count_24_hours_before3) / 3)

    return round(positive_polarity_24_hours_before, 2), round(negative_polarity_24_hours_before, 2), \
        positive_count_24_hours_before, negative_count_24_hours_before


@retry_on_error(3, 5, (requests.exceptions.RequestException,
                       json.JSONDecodeError, ValueError, KeyError), (0.0, 0.0))
def check_sentiment_of_news_wrapper() -> Tuple[float, float]:

    # We need to update Bitcoin price hourly (same as news)
    update_bitcoin_price_in_database()

    save_update_time('sentiment_of_news')

    # Get aggregated value from 3 function for las 24 hours
    last_24_hours_positive_polarity, last_24_hours_negative_polarity,\
        positive_count_24_hours_before, negative_count_24_hours_before = aggregate_news()

    news_bullish, news_bearish = compare_news(last_24_hours_positive_polarity, last_24_hours_negative_polarity,
                                              positive_count_24_hours_before, negative_count_24_hours_before)

    # Save data on disk for later compare
    write_latest_data('positive_polarity_score', round(last_24_hours_positive_polarity, 2))
    write_latest_data('negative_polarity_score', round(last_24_hours_negative_polarity, 2))
    write_latest_data('positive_news_count', positive_count_24_hours_before)
    write_latest_data('negative_news_count', negative_count_24_hours_before)

    # Save data on database
    save_value_to_database('news_positive_polarity', round(last_24_hours_positive_polarity, 2))
    save_value_to_database('news_negative_polarity', round(last_24_hours_negative_polarity, 2))
    save_value_to_database('news_positive_count', positive_count_24_hours_before)
    save_value_to_database('news_negative_count', negative_count_24_hours_before)
    save_value_to_database('news_bullish', news_bullish)
    save_value_to_database('news_bearish', news_bearish)

    return news_bullish, news_bearish


def check_sentiment_of_news() -> Tuple[float, float]:
    if should_update('sentiment_of_news'):
        return check_sentiment_of_news_wrapper()
    else:
        return retrieve_latest_factor_values_database('news')


if __name__ == "__main__":
    news_bullish_outer, news_bearish_outer = check_sentiment_of_news_wrapper()
    logging.info(f'news_bullish: {news_bullish_outer}, and news_bearish: {news_bearish_outer}')
