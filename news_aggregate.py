from datetime import datetime, timedelta
import logging
from typing import Tuple

from newsAPI import check_news_api_sentiment
from news_crypto_compare import check_news_cryptocompare_sentiment
from news_scrapper import check_news_sentiment_scrapper


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


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

    positive_polarity_score_outer, negative_polarity_score_outer, \
        positive_count_outer, negative_count_outer = aggregate_news()

    logging.info(f'positive_polarity: {positive_polarity_score_outer}'
                 f' and negative_polarity: {negative_polarity_score_outer}')
    logging.info(f'positive_count: {positive_count_outer} '
                 f' and negative_count: {negative_count_outer}')
