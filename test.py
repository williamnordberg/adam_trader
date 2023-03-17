import praw
import time
import pandas as pd
import logging
from datetime import datetime, timedelta


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def count_bitcoin_posts(reddit):
    subreddit = reddit.subreddit("all")
    bitcoin_posts = subreddit.search("#Crypto ", limit=1000)
    count = 0
    for post in bitcoin_posts:
        if post.created_utc > (time.time() - 7 * 24 * 60 * 60):
            count += 1

    return count


def reddit_check():
    reddit = praw.Reddit(client_id='KiayZQKazH6eL_hTwlSgQw',
                         client_secret='25JDkyyvbbAP-osqrzXykVK65w86mw',
                         user_agent='btc_monitor_app:com.www.btc1231231:v1.0 (by /u/will7i7am)')

    latest_info_saved = pd.read_csv('latest_info_saved.csv')
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
