import praw
import time
import pandas as pd
import logging
from datetime import datetime, timedelta
import configparser

SEVEN_DAYS_IN_SECONDS = 7 * 24 * 60 * 60


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


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
        if post.created_utc > (time.time() - SEVEN_DAYS_IN_SECONDS):
            count += 1

    return count


def reddit_check():
    """
      Checks the current activity and post count of the Bitcoin subreddit on Reddit.
      If the last check was less than 24 hours ago, returns the activity and count increase
      from the last check. Otherwise, calculates the activity and count increase from the
      previous check and updates the saved information file.

      Returns:
          tuple: A tuple containing the activity increase and count increase as booleans.
              The activity increase is True if the current activity is at least 15% higher than
              the previous activity, and False otherwise. The count increase is True if the
              current post count is at least 15% higher than the previous post count, and False
              otherwise.

      """
    config = configparser.ConfigParser()
    config.read('config.ini')

    reddit_config = config['reddit']
    reddit = praw.Reddit(
        client_id=reddit_config['client_id'],
        client_secret=reddit_config['client_secret'],
        user_agent=reddit_config['user_agent']
    )
    latest_info_saved = pd.read_csv('latest_info_saved.csv', squeeze=True)
    last_reddit_update_time_str = latest_info_saved['last_reddit_update_time'][0]
    last_reddit_update_time = datetime.strptime(last_reddit_update_time_str, '%Y-%m-%d %H:%M:%S')

    if datetime.now() - last_reddit_update_time < timedelta(hours=24):
        logging.info('Last Reddit update was less than 24 hours ago. Skipping...')
        last_activity_increase = latest_info_saved['last_activity_increase'][0]
        last_count_increase = latest_info_saved['last_count_increase'][0]
        return last_activity_increase, last_count_increase

    else:
        previous_activity = float(latest_info_saved['previous_activity'][0])
        previous_count = float(latest_info_saved['previous_count'][0])
        current_activity = reddit.subreddit("Bitcoin").active_user_count
        current_count = count_bitcoin_posts(reddit)
        last_activity_increase = (current_activity / previous_activity) > 1.15
        last_count_increase = (current_count / previous_count) > 1.15

        latest_info_saved.loc[0, 'previous_activity'] = current_activity
        latest_info_saved.loc[0, 'previous_count'] = current_count

        # Save the update time to disk
        now = datetime.now()
        now_str = now.strftime('%Y-%m-%d %H:%M:%S')
        latest_info_saved.loc[0, 'last_reddit_update_time'] = now_str
        latest_info_saved.to_csv('latest_info_saved.csv', index=False)

        return last_activity_increase, last_count_increase


if __name__ == '__main__':
    activity_increase1, count_increase1 = reddit_check()
    logging.info(f", activity_increase: {activity_increase1}, count_increase: {count_increase1}")
