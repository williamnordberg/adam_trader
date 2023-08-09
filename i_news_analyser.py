import requests.exceptions
import json

from i_news_sentiment import calculate_news_sentiment
from z_handy_modules import retry_on_error, get_bitcoin_price
from z_read_write_csv import save_value_to_database, \
    should_update, save_update_time, retrieve_latest_factor_values_database

ALLOWED_EXCEPTIONS = (requests.exceptions.RequestException, ValueError)


def normalize_scores(positive_score, negative_score):
    total_score = positive_score + negative_score
    if total_score == 0:  # avoid dividing by 0
        news_bullish = 0.5
    else:
        news_bullish = positive_score / total_score

    return round(news_bullish, 2)


@retry_on_error(max_retries=3, delay=5,
                allowed_exceptions=ALLOWED_EXCEPTIONS, fallback_values='pass')
def update_bitcoin_price_in_database():
    price = get_bitcoin_price()
    save_value_to_database('bitcoin_price', price)


@retry_on_error(3, 5, (requests.exceptions.RequestException,
                       json.JSONDecodeError, ValueError, KeyError), 0.5)
def check_sentiment_of_news_wrapper() -> float:

    # We need to update Bitcoin price hourly (same as news)
    update_bitcoin_price_in_database()

    positive_polarity, negative_polarity, positive_count, negative_count = calculate_news_sentiment()

    # Save data on database
    save_value_to_database('news_positive_polarity', round(positive_polarity, 2))
    save_value_to_database('news_negative_polarity', round(negative_polarity, 2))
    save_value_to_database('news_positive_count', positive_count)
    save_value_to_database('news_negative_count', negative_count)

    save_update_time('sentiment_of_news')

    # calculate news_bullish and bearish
    news_bullish = normalize_scores(positive_polarity, negative_polarity)

    return news_bullish


def check_sentiment_of_news() -> float:
    if should_update('sentiment_of_news'):
        news_bullish = check_sentiment_of_news_wrapper()
        save_value_to_database('news_bullish', news_bullish)
        return news_bullish
    else:
        return retrieve_latest_factor_values_database('news')


if __name__ == "__main__":
    news_bullish_outer = check_sentiment_of_news_wrapper()
    print(f'news_bullish: {news_bullish_outer}')
