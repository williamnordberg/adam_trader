import praw
import time
import pandas as pd
import logging
import configparser
from typing import Tuple
from praw import Reddit
from database import save_value_to_database
from handy_modules import save_update_time, should_update
from database import read_database
ONE_DAYS_IN_SECONDS = 24 * 60 * 60


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def compare(current_activity: float, previous_activity: float) -> Tuple[float, float]:

    activity_percentage = (current_activity - previous_activity) / previous_activity * 100

    if activity_percentage > 0:
        if activity_percentage >= 50:
            return 1, 0
        elif activity_percentage >= 40:
            return 0.9, 0.1
        elif activity_percentage >= 30:
            return 0.8, 0.2
        elif activity_percentage >= 20:
            return 0.7, 0.3
        elif activity_percentage >= 10:
            return 0.6, 0.4

    elif activity_percentage <= 0:
        if activity_percentage <= -50:
            return 0, 1
        elif activity_percentage <= -40:
            return 0.1, 0.9
        elif activity_percentage <= -30:
            return 0.2, 0.8
        elif activity_percentage <= -20:
            return 0.3, 0.7
        elif activity_percentage <= -10:
            return 0.4, 0.6

    return 0, 0


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


def reddit_check_wrapper() -> Tuple[float, float]:

    config = configparser.ConfigParser()
    config.read('config.ini')

    reddit_config = config['reddit']
    reddit = praw.Reddit(
        client_id=reddit_config['client_id'],
        client_secret=reddit_config['client_secret'],
        user_agent=reddit_config['user_agent']
    )
    latest_info_saved = pd.read_csv('latest_info_saved.csv').squeeze("columns")

    previous_activity = float(latest_info_saved['previous_activity'][0])
    # previous_count = float(latest_info_saved['previous_count'][0])
    current_activity = reddit.subreddit("Bitcoin").active_user_count
    current_count = count_bitcoin_posts(reddit)
    reddit_bullish, reddit_bearish = compare(current_activity, previous_activity)

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
    reddit_bullish_outer, reddit_bearish_outer = reddit_check()
    logging.info(f", reddit_bullish: {reddit_bullish_outer}, reddit_bearish: {reddit_bearish_outer}")
