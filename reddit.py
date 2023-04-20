import praw
import time
import pandas as pd
import logging
import configparser
from typing import Tuple
from prawcore.exceptions import RequestException
from requests.exceptions import SSLError
from urllib3.exceptions import MaxRetryError
from praw import Reddit
from prawcore import Requestor


from database import save_value_to_database
from handy_modules import save_update_time, should_update, retry_on_error_with_fallback, compare_reddit
from database import read_database
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

ONE_DAYS_IN_SECONDS = 24 * 60 * 60
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class ProxyRequestor(Requestor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.proxies = {
            'http': 'http://137.74.167.5:9898',
            'https': 'http://137.74.167.5:9898'
        }

    def request(self, *args, **kwargs):
        kwargs['verify'] = False  # Bypass SSL certificate verification
        return super().request(*args, proxies=self.proxies, **kwargs)

    def _prepare(self, *args, **kwargs):
        request = super()._prepare(*args, **kwargs)
        request.proxies = self.proxies
        return request


@retry_on_error_with_fallback(
    max_retries=3, delay=5, allowed_exceptions=(RequestException,), fallback_values=0)
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


@retry_on_error_with_fallback(
    max_retries=3, delay=5, allowed_exceptions=(SSLError, MaxRetryError,), fallback_values=(0, 0))
def reddit_check_wrapper() -> Tuple[float, float]:

    config = configparser.ConfigParser()
    config.read('config.ini')

    reddit_config = config['reddit']

    reddit = Reddit(
        client_id=reddit_config['client_id'],
        client_secret=reddit_config['client_secret'],
        user_agent=reddit_config['user_agent'],
        password=reddit_config['password'],
        username=reddit_config['username'],
        requestor_class=ProxyRequestor
    )

    latest_info_saved = pd.read_csv('latest_info_saved.csv').squeeze("columns")

    previous_activity = float(latest_info_saved['previous_activity'][0])
    # previous_count = float(latest_info_saved['previous_count'][0])
    try:
        current_activity = reddit.subreddit("Bitcoin").active_user_count
        current_count = count_bitcoin_posts(reddit)
        reddit_bullish, reddit_bearish = compare_reddit(current_activity, previous_activity)

        latest_info_saved.loc[0, 'previous_activity'] = current_activity
        latest_info_saved.loc[0, 'previous_count'] = current_count

        latest_info_saved.to_csv('latest_info_saved.csv', index=False)

        # Save latest update time
        save_update_time('reddit')

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
        database = read_database()
        reddit_bullish = database['reddit_bullish'][-1]
        reddit_bearish = database['reddit_bearish'][-1]
        return reddit_bullish, reddit_bearish


if __name__ == '__main__':
    reddit_bullish_outer, reddit_bearish_outer = reddit_check_wrapper()
    logging.info(f", reddit_bullish: {reddit_bullish_outer}, reddit_bearish: {reddit_bearish_outer}")
