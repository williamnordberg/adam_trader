import logging
import pandas as pd
from datetime import datetime, timedelta

from handy_modules import should_update, save_update_time
from typing import Tuple
from database import read_database
from news_compare_polarity import compare_polarity
from newsAPI import check_news_api_sentiment
from news_aggregate import aggregate_news
from database import save_value_to_database

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

LATEST_INFO_SAVED_PATH = 'data/latest_info_saved.csv'


def update_latest_info_saved(df, positive_polarity, negative_polarity,
                             positive_count, negative_count, news_bullish, news_bearish):
    df.loc[0, 'positive_polarity_score'] = positive_polarity
    df.loc[0, 'negative_polarity_score'] = negative_polarity
    df.loc[0, 'positive_news_count'] = positive_count
    df.loc[0, 'negative_news_count'] = negative_count
    df.loc[0, 'news_bullish'] = news_bullish
    df.loc[0, 'news_bearish'] = news_bearish

    now = datetime.now()
    now_str = now.strftime('%Y-%m-%d %H:%M:%S')
    df.loc[0, 'last_news_update_time'] = now_str
    df.to_csv('latest_info_saved.csv', index=False)


def check_sentiment_of_news_wrapper() -> Tuple[float, float]:
    # Save latest update time
    save_update_time('sentiment_of_news')

    latest_info_saved = pd.read_csv(LATEST_INFO_SAVED_PATH).squeeze("columns")
    last_news_sentiment_str = latest_info_saved['last_news_update_time'][0]
    last_news_sentiment = datetime.strptime(last_news_sentiment_str, '%Y-%m-%d %H:%M:%S')
    last_update_time_difference = datetime.now() - last_news_sentiment

    if timedelta(hours=24) > last_update_time_difference < timedelta(hours=48):
        # Get aggregated value from 3 function for the last 24 hours
        positive_polarity_24_hours_before, negative_polarity_24_hours_before, \
            positive_count_24_hours_before, negative_count_24_hours_before = aggregate_news()

        # Compare last 24 hours polarity with last 48 hours polarity
        latest_positive_polarity_score = latest_info_saved['positive_polarity_score'][0]
        latest_negative_polarity_score = latest_info_saved['negative_polarity_score'][0]
        news_bullish, news_bearish = compare_polarity(positive_polarity_24_hours_before, latest_positive_polarity_score,
                                                      negative_polarity_24_hours_before, latest_negative_polarity_score)

        # Update latest_info_saved
        update_latest_info_saved(latest_info_saved, positive_polarity_24_hours_before,
                                 negative_polarity_24_hours_before,
                                 positive_count_24_hours_before, negative_count_24_hours_before, news_bullish,
                                 news_bearish)

        # Save data on database
        save_value_to_database('news_positive_polarity', round(positive_polarity_24_hours_before, 3))
        save_value_to_database('news_negative_polarity', round(negative_polarity_24_hours_before, 3))
        save_value_to_database('news_positive_count', positive_count_24_hours_before)
        save_value_to_database('news_negative_count', negative_count_24_hours_before)

        return news_bullish, news_bearish

    elif last_update_time_difference > timedelta(hours=48):
        # Get the values for 48 to 24 hours before
        start = datetime.now() - timedelta(days=2)
        end = datetime.now() - timedelta(days=1)
        positive_polarity_48_hours_before, negative_polarity_48_hours_before, \
            positive_count_outer_48_hours_before, negative_count_48_hours_before = \
            check_news_api_sentiment(start, end)

        # Get the values for the last 24 hours
        start = datetime.now() - timedelta(days=1)
        end = datetime.now()
        positive_polarity_24_hours_before, negative_polarity_24_hours_before, \
            positive_count_24_hours_before, negative_count_24_hours_before = \
            check_news_api_sentiment(start, end)

        # Compare
        news_bullish, news_bearish = compare_polarity(
            positive_polarity_24_hours_before, positive_polarity_48_hours_before,
            negative_polarity_24_hours_before, negative_polarity_48_hours_before)

        # Get aggregated value from 3 function for the last 24 hours
        positive_polarity_24_hours_to_save, negative_polarity_24_hours_to_save, \
            positive_count_24_hours_to_save, negative_count_24_hours_to_save = aggregate_news()

        # Update latest_info_saved
        update_latest_info_saved(latest_info_saved, positive_polarity_24_hours_to_save,
                                 negative_polarity_24_hours_to_save,
                                 positive_count_24_hours_to_save, negative_count_24_hours_to_save, news_bullish,
                                 news_bearish)

        logging.info(f'news data has been updated')

        # Save on database, we do not save news_positive_polarity,
        # news_negative_polarity, news_positive_count, news_negative_count to keep consistency in database
        return news_bullish, news_bearish

    return 0, 0


def check_sentiment_of_news() -> Tuple[float, float]:
    if should_update('sentiment_of_news'):
        news_bullish, news_bearish = check_sentiment_of_news_wrapper()
        save_value_to_database('news_bullish', news_bullish)
        save_value_to_database('news_bearish', news_bearish)
        return news_bullish, news_bearish
    else:
        database = read_database()
        news_bullish = database['news_bullish'][-1]
        news_bearish = database['news_bearish'][-1]
        return news_bullish, news_bearish


if __name__ == "__main__":
    news_bullish_outer, news_bearish_outer = check_sentiment_of_news()
    logging.info(f'news_bullish: {news_bullish_outer}, and news_bearish: {news_bearish_outer}')
