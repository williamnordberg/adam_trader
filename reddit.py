import praw
import time
import pandas as pd
import logging
from datetime import datetime, timedelta
import configparser

ONE_DAYS_IN_SECONDS = 24 * 60 * 60


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def compare(current_activity, previous_activity):

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
        if previous_activity <= 50:
            return 0, 1
        elif previous_activity <= 40:
            return 0.1, 0.9
        elif previous_activity <= 30:
            return 0.2, 0.8
        elif previous_activity <= 20:
            return 0.3, 0.7
        elif previous_activity <= 10:
            return 0.4, 0.6

    return 0, 0


def count_bitcoin_posts(reddit):
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


def reddit_check():

    config = configparser.ConfigParser()
    config.read('config.ini')

    reddit_config = config['reddit']
    reddit = praw.Reddit(
        client_id=reddit_config['client_id'],
        client_secret=reddit_config['client_secret'],
        user_agent=reddit_config['user_agent']
    )
    latest_info_saved = pd.read_csv('latest_info_saved.csv').squeeze("columns")
    last_reddit_update_time_str = latest_info_saved['last_reddit_update_time'][0]
    last_reddit_update_time = datetime.strptime(last_reddit_update_time_str, '%Y-%m-%d %H:%M:%S')

    if datetime.now() - last_reddit_update_time < timedelta(hours=24):
        logging.info('Last Reddit update was less than 24 hours ago. Skipping...')
        last_activity_increase = latest_info_saved['reddit_bullish'][0]
        last_count_increase = latest_info_saved['reddit_bearish'][0]
        return last_activity_increase, last_count_increase

    else:
        previous_activity = float(latest_info_saved['previous_activity'][0])
        previous_count = float(latest_info_saved['previous_count'][0])
        current_activity = reddit.subreddit("Bitcoin").active_user_count
        current_count = count_bitcoin_posts(reddit)
        reddit_bullish, reddit_bearish = compare(current_activity, previous_activity)

        print('current_activity / previous_activity', current_activity, previous_activity)
        print('current_count / previous_count', current_count, previous_count)

        latest_info_saved.loc[0, 'reddit_bullish'] = reddit_bullish
        latest_info_saved.loc[0, 'reddit_bearish'] = reddit_bearish
        latest_info_saved.loc[0, 'previous_activity'] = current_activity
        latest_info_saved.loc[0, 'previous_count'] = current_count

        # Save the update time to disk
        now = datetime.now()
        now_str = now.strftime('%Y-%m-%d %H:%M:%S')
        latest_info_saved.loc[0, 'last_reddit_update_time'] = now_str
        latest_info_saved.to_csv('latest_info_saved.csv', index=False)

        return reddit_bullish, reddit_bearish


if __name__ == '__main__':
    reddit_bullish_outer, reddit_bearish_outer = reddit_check()
    logging.info(f", reddit_bullish: {reddit_bullish_outer}, reddit_bearish: {reddit_bearish_outer}")
