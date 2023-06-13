from datetime import datetime, timedelta
import logging

from newsAPI import check_news_api_sentiment
from news_crypto_compare import check_news_cryptocompare_sentiment
from news_scrapper import check_news_sentiment_scrapper
from typing import Tuple

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def compare_polarity(last_24_hours_positive_polarity: float, saved_positive_polarity: float,
                     last_24_hours_negative_polarity: float, saved_negative_polarity: float)\
        -> Tuple[float, float]:
    positive_percentage_increase = (last_24_hours_positive_polarity - saved_positive_polarity
                                    ) / saved_positive_polarity * 100
    negative_percentage_increase = (last_24_hours_negative_polarity - saved_negative_polarity
                                    ) / saved_negative_polarity * 100

    print('positive_percentage_increase', positive_percentage_increase)
    print('negative_percentage_increase', negative_percentage_increase)

    if positive_percentage_increase > negative_percentage_increase:
        positive_percentage_increase = positive_percentage_increase - negative_percentage_increase
        if positive_percentage_increase >= 50:
            return 1, 0
        elif positive_percentage_increase >= 40:
            return 0.9, 0.1
        elif positive_percentage_increase >= 30:
            return 0.8, 0.2
        elif positive_percentage_increase >= 20:
            return 0.7, 0.3
        elif positive_percentage_increase >= 10:
            return 0.6, 0.4

    elif positive_percentage_increase < negative_percentage_increase:
        negative_percentage_increase = negative_percentage_increase - positive_percentage_increase
        if negative_percentage_increase >= 50:
            return 0, 1
        elif negative_percentage_increase >= 40:
            return 0.1, 0.9
        elif negative_percentage_increase >= 30:
            return 0.2, 0.8
        elif negative_percentage_increase >= 20:
            return 0.3, 0.7
        elif negative_percentage_increase >= 10:
            return 0.4, 0.6

    return 0, 0


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

    return positive_polarity_24_hours_before, negative_polarity_24_hours_before, \
        positive_count_24_hours_before, negative_count_24_hours_before


if __name__ == "__main__":

    x, y = compare_polarity(0.13, 0.1,
                            1, 1)
    print(f'bullish: {x}, bearish: {y}')
