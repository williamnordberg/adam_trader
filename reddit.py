import praw
import time
import pandas as pd


def save_current_time():
    latest_info_saved = pd.read_csv('latest_info_saved.csv')
    latest_info_saved.loc[0, 'last_reddit_update_time'] = str(time.time())
    latest_info_saved.to_csv('latest_info_saved.csv', index=False)


def load_last_update_time():
    try:
        latest_info_saved = pd.read_csv('latest_info_saved.csv')
        last_update_time = float(latest_info_saved['last_reddit_update_time'][0])
        return last_update_time
    except FileNotFoundError:
        return None


def check_last_update_time():
    last_update_time = load_last_update_time()
    if last_update_time is None:
        return False
    current_time = time.time()
    time_diff = current_time - last_update_time
    if time_diff < 24*60*60:
        return True
    else:
        return False


def monitor_activity(previous_activity, previous_count):
    reddit = praw.Reddit(client_id='KiayZQKazH6eL_hTwlSgQw',
                         client_secret='25JDkyyvbbAP-osqrzXykVK65w86mw',
                         user_agent='btc_monitor_app:com.www.btc1231231:v1.0 (by /u/will7i7am)')

    current_activity = reddit.subreddit("Bitcoin").active_user_count
    current_count = count_bitcoin_posts(reddit)

    activity_increase = (current_activity / previous_activity) > 1.15
    count_increase = (current_count / previous_count) > 1.15

    return current_activity, current_count, activity_increase, count_increase


def count_bitcoin_posts(reddit):
    subreddit = reddit.subreddit("all")
    bitcoin_posts = subreddit.search("#Crypto ", limit=1000)
    count = 0
    for post in bitcoin_posts:
        if post.created_utc > (time.time() - 7 * 24 * 60 * 60):
            count += 1

    return count


def reddit_check(previous_activity=None, previous_count=None):
    reddit = praw.Reddit(client_id='KiayZQKazH6eL_hTwlSgQw',
                         client_secret='25JDkyyvbbAP-osqrzXykVK65w86mw',
                         user_agent='btc_monitor_app:com.www.btc1231231:v1.0 (by /u/will7i7am)')

    latest_info_saved = pd.read_csv('latest_info_saved.csv')
    if previous_activity is None:
        previous_activity = float(latest_info_saved['previous_activity'][0])
        previous_count = float(latest_info_saved['previous_count'][0])

    if check_last_update_time():
        print('Last Reddit update was less than 24 hours ago. Skipping...')
        last_activity_increase = float(latest_info_saved['last_activity_increase'][0])
        last_count_increase = float(latest_info_saved['last_count_increase'][0])
        return previous_activity, previous_count, last_activity_increase, last_count_increase
    else:
        current_activity = reddit.subreddit("Bitcoin").active_user_count
        current_count = count_bitcoin_posts(reddit)
        if previous_activity is not None:
            activity_increase = (current_activity / previous_activity) > 1.15
        else:
            activity_increase = False
        if previous_count is not None:
            count_increase = (current_count / previous_count) > 1.15
        else:
            count_increase = False

        latest_info_saved.loc[0, 'previous_activity'] = current_activity
        latest_info_saved.loc[0, 'previous_count'] = current_count
        latest_info_saved.loc[0, 'last_activity_increase'] = activity_increase
        latest_info_saved.loc[0, 'last_count_increase'] = count_increase
        latest_info_saved.to_csv('latest_info_saved.csv', index=False)

        save_current_time()

        return current_activity, current_count, activity_increase, count_increase


current_activity1, current_count1, activity_increase1, count_increase1 = reddit_check()
print(current_activity1, current_count1, activity_increase1, count_increase1)
