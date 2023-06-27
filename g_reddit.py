import praw
import time
import logging
import configparser
from typing import Tuple
from praw import Reddit
from prawcore.exceptions import RequestException
from requests.exceptions import SSLError
from urllib3.exceptions import MaxRetryError

from read_write_csv import save_value_to_database, save_update_time, \
    should_update, read_latest_data, write_latest_data, retrieve_latest_factor_values_database
from z_handy_modules import retry_on_error
from z_compares import compare_google_reddit_youtube

ONE_DAYS_IN_SECONDS = 24 * 60 * 60
CONFIG_PATH = 'config/config.ini'


@retry_on_error(max_retries=3, delay=5, allowed_exceptions=(RequestException,), fallback_values=0)
def count_bitcoin_posts(reddit: Reddit) -> int:
    """
        Counts the number of Bitcoin-related posts on Reddit in the last 7 days.

        Args:
            reddit (praw.Reddit): An authenticated Reddit instance.

        Returns:
            int: The number of Bitcoin-related posts in the last 7 days.

        """
    subreddit = reddit.subreddit("all")
    bitcoin_posts = subreddit.search("#Crypto ", limit=1000)
    count = 0
    for post in bitcoin_posts:
        if post.created_utc > (time.time() - ONE_DAYS_IN_SECONDS):
            count += 1

    return count


@retry_on_error(max_retries=3, delay=5, allowed_exceptions=(
        SSLError, MaxRetryError,), fallback_values=(0.0, 0.0))
def reddit_check_wrapper() -> Tuple[float, float]:
    save_update_time('reddit')

    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)

    reddit_config = config['reddit']
    reddit = praw.Reddit(
        client_id=reddit_config['client_id'],
        client_secret=reddit_config['client_secret'],
        user_agent=reddit_config['user_agent']
    )
    previous_activity = read_latest_data('previous_activity', int)
    # read_latest_data('previous_count', int)

    try:
        current_activity = reddit.subreddit("Bitcoin").active_user_count
        current_count = count_bitcoin_posts(reddit)
        reddit_bullish, reddit_bearish = compare_google_reddit_youtube(int(current_activity), int(previous_activity))

        write_latest_data('previous_activity', current_activity)
        write_latest_data('previous_count', current_count)

        # Save to database
        save_value_to_database('reddit_bullish', reddit_bullish)
        save_value_to_database('reddit_bearish', reddit_bearish)
        save_value_to_database('reddit_count_bitcoin_posts_24h', current_count)
        save_value_to_database('reddit_activity_24h', current_activity)
    except Exception as e:
        logging.error(f"Error occurred: {e}")
        reddit_bullish, reddit_bearish = 0, 0

    return reddit_bullish, reddit_bearish


def reddit_check() -> Tuple[float, float]:
    if should_update('reddit'):
        return reddit_check_wrapper()
    else:
        return retrieve_latest_factor_values_database('reddit')


if __name__ == '__main__':
    reddit_bullish_outer, reddit_bearish_outer = reddit_check_wrapper()
    logging.info(f", reddit_bullish: {reddit_bullish_outer}, reddit_bearish: {reddit_bearish_outer}")
