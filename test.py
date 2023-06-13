from datetime import datetime, timedelta
import logging

from newsAPI import check_news_api_sentiment
from news_crypto_compare import check_news_cryptocompare_sentiment
from news_scrapper import check_news_sentiment_scrapper
from typing import Tuple
from handy_modules import read_float_from_latest_saved

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def calculate_market_sentiment() -> (float, float):

    positive_polarity_24h, negative_polarity_24h, \
        positive_count_24h, negative_count_24h = aggregate_news()

    positive_polarity_48h = round(read_float_from_latest_saved('positive_polarity_score'), 2)
    positive_count_48h = read_float_from_latest_saved('positive_news_count')
    negative_polarity_48h = round(read_float_from_latest_saved('negative_polarity_score'), 2)
    negative_count_48h = read_float_from_latest_saved('negative_news_count')

    print('positive_polarity_48h', positive_polarity_48h)
    print('positive_polarity_24h', positive_polarity_24h)

    print('positive_count_48h', positive_count_48h)
    print('positive_count_24h', positive_count_24h)

    print('negative_polarity_48h', negative_polarity_48h)
    print('negative_polarity_24h', negative_polarity_24h)

    print('negative_count_48h', negative_count_48h)
    print('negative_count_24h', negative_count_24h)

    # Calculate changes in counts and polarities
    positive_pol_change = positive_polarity_24h - positive_polarity_48h
    positive_count_change = positive_count_24h - positive_count_48h
    negative_pol_change = negative_polarity_24h - negative_polarity_48h
    negative_count_change = negative_count_24h - negative_count_48h

    score, news_bullish, news_bearish = 0, 0, 0
    if positive_pol_change > 0:
        score += 0.1
    elif positive_pol_change < 0:
        score -= 0.1

    if positive_count_change > 0:
        score += 0.1
    elif positive_count_change < 0:
        score -= 0.1

    if negative_pol_change > 0:
        score -= 0.2
    elif negative_pol_change < 0:
        score += 0.2

    if negative_count_change > 0:
        score -= 0.1
    elif negative_count_change < 0:
        score += 0.1

    if score > 0:
        news_bullish = 0.5 + score
    elif score < 0:
        news_bearish = 0.5 + abs(score)
    else:
        news_bullish, news_bearish = 0, 0

    return news_bullish, news_bearish


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


if __name__ == "__main__":
    x, y = calculate_market_sentiment()
    print(f'bullish: {x}, bearish: {y}')
