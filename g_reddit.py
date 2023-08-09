import pandas as pd
from textblob import TextBlob
import praw
import configparser
from requests.exceptions import SSLError
from urllib3.exceptions import MaxRetryError
from prawcore.exceptions import RequestException

from z_read_write_csv import save_value_to_database, save_update_time, \
    should_update, retrieve_latest_factor_values_database, read_database
from z_handy_modules import retry_on_error


SHORT_MOVING_AVERAGE_WINDOW = 5
LONG_MOVING_AVERAGE_WINDOW = 20
CONFIG_PATH = 'config/config.ini'


def calculate_reddit_trend(reddit_bullish, short_ma, long_ma, factor_type):
    adjustment = 0.125

    if factor_type == 'positive_polarity' or factor_type == 'positive_count':
        if short_ma > long_ma:
            reddit_bullish += adjustment
    elif factor_type == 'negative_polarity' or factor_type == 'negative_count':
        if short_ma > long_ma:
            reddit_bullish -= adjustment

    return reddit_bullish


def calculate_reddit_sentiments():
    reddit_bullish, reddit_bearish = 0.5, 0.5
    data = read_database()
    df = pd.DataFrame(data, columns=['reddit_positive_polarity',
                                     'reddit_negative_polarity', 'reddit_positive_count',
                                     'reddit_negative_count'])

    for col in df.columns:
        short_ma = df[col].rolling(window=SHORT_MOVING_AVERAGE_WINDOW, min_periods=1).mean()
        long_ma = df[col].rolling(window=LONG_MOVING_AVERAGE_WINDOW, min_periods=1).mean()
        reddit_bullish = calculate_reddit_trend(
            reddit_bullish, short_ma.iloc[-1], long_ma.iloc[-1], col)
    return reddit_bullish


def calculate_sentiment_score(content: str) -> float:
    blob = TextBlob(content)
    return blob.sentiment.polarity


def preprocess_and_save_reddit_data(reddit, subreddit_name):
    positive_polarity_score, negative_polarity_score = 0.0, 0.0
    positive_count, negative_count = 0, 0
    subreddit = reddit.subreddit(subreddit_name)

    for post in subreddit.hot(limit=50):
        content = post.title + " " + post.selftext
        sentiment_score = calculate_sentiment_score(content)
        if sentiment_score > 0:
            positive_polarity_score += sentiment_score
            positive_count += 1
        elif sentiment_score < 0:
            negative_polarity_score += sentiment_score
            negative_count += 1

    # Calculate average positive and negative sentiments
    positive_polarity = positive_polarity_score / positive_count if positive_count != 0 else 0
    negative_polarity = abs(negative_polarity_score / negative_count) if negative_count != 0 else 0

    # save all value in database to calculate later
    save_value_to_database('reddit_positive_polarity', positive_polarity)
    save_value_to_database('reddit_negative_polarity', negative_polarity)
    save_value_to_database('reddit_positive_count', positive_count)
    save_value_to_database('reddit_negative_count', negative_count)


@retry_on_error(max_retries=3, delay=5, allowed_exceptions=(
        SSLError, MaxRetryError, RequestException), fallback_values=0.5)
def reddit_check_wrapper() -> float:

    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)

    reddit_config = config['reddit']
    reddit = praw.Reddit(
        client_id=reddit_config['client_id'],
        client_secret=reddit_config['client_secret'],
        user_agent=reddit_config['user_agent']
    )

    # We save this just for visualization
    current_activity = reddit.subreddit("Bitcoin").active_user_count
    save_value_to_database('reddit_activity_24h', current_activity)

    preprocess_and_save_reddit_data(reddit, "Bitcoin")

    reddit_bullish = calculate_reddit_sentiments()

    save_update_time('reddit')

    return reddit_bullish


def reddit_check() -> float:
    if should_update('reddit'):
        reddit_bullish = reddit_check_wrapper()
        save_value_to_database('reddit_bullish', reddit_bullish)
        return reddit_bullish

    else:
        return retrieve_latest_factor_values_database('reddit')


if __name__ == '__main__':
    reddit_bullish_outer = reddit_check_wrapper()
    print(f"reddit_bullish: {reddit_bullish_outer}")
