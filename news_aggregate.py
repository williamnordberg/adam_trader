import datetime
from datetime import datetime, timedelta

from newsAPI import check_news_api_sentiment
from news_crypto_compare import check_news_cryptocompare_sentiment
from news_scrapper import check_news_sentiment_scrapper


def aggregate_news():
    # Get aggregated value from 3 function for las 24 hours

    start = datetime.datetime.now() - datetime.timedelta(days=1)
    end = datetime.datetime.now()
    positive_polarity_24_hours_before1, negative_polarity_24_hours_before1, \
        positive_count_24_hours_before1, negative_count_24_hours_before1 = \
        check_news_api_sentiment(start, end)

    positive_polarity_24_hours_before2, negative_polarity_24_hours_before2, \
        positive_count_24_hours_before2, negative_count_24_hours_before2 = \
        check_news_cryptocompare_sentiment()

    positive_polarity_24_hours_before3, negative_polarity_24_hours_before3, \
        positive_count_24_hours_before3, negative_count_24_hours_before3 = \
        check_news_sentiment_scrapper()

    positive_polarity_24_hours_before = (positive_polarity_24_hours_before1 + positive_polarity_24_hours_before2
                                         + positive_polarity_24_hours_before3) / 3

    negative_polarity_24_hours_before = (negative_count_24_hours_before1 + negative_polarity_24_hours_before2
                                         + negative_polarity_24_hours_before3) / 3

    positive_count_24_hours_before = (positive_count_24_hours_before1 + positive_count_24_hours_before2
                                      + positive_count_24_hours_before3) / 3

    negative_count_24_hours_before = (negative_polarity_24_hours_before1 + negative_count_24_hours_before2
                                      + negative_count_24_hours_before3) / 3
    return positive_polarity_24_hours_before, negative_polarity_24_hours_before,\
        positive_count_24_hours_before, negative_count_24_hours_before

