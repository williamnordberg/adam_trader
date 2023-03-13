import praw
import pickle
import time


def save_increases(activity_increase, count_increase):
    with open('last_increases.pkl', 'wb') as f:
        data = {'activity_increase': activity_increase, 'count_increase': count_increase}
        pickle.dump(data, f)


def load_last_increases():
    try:
        with open('last_increases.pkl', 'rb') as f:
            data = pickle.load(f)
            last_activity_increase = data['activity_increase']
            last_count_increase = data['count_increase']
        return last_activity_increase, last_count_increase
    except FileNotFoundError:
        return False, False


def save_previous_values(previous_activity, previous_count):
    with open('previous_values.pkl', 'wb') as f:
        data = {'previous_activity': previous_activity, 'previous_count': previous_count}
        pickle.dump(data, f)


def load_previous_values():
    try:
        with open('previous_values.pkl', 'rb') as f:
            data = pickle.load(f)
            previous_activity = data['previous_activity']
            previous_count = data['previous_count']
        return previous_activity, previous_count
    except FileNotFoundError:
        return None, None


def save_current_time():
    with open('last_update_time.txt', 'w') as f:
        f.write(str(time.time()))


def load_last_update_time():
    try:
        with open('last_update_time.txt', 'r') as f:
            last_update_time = float(f.read())
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

    if previous_activity is None:
        previous_activity = reddit.subreddit("Bitcoin").active_user_count
        previous_count = count_bitcoin_posts(reddit)

    if check_last_update_time():
        print('Last Reddit update was less than 24 hours ago. Skipping...')
        last_activity_increase, last_count_increase = load_last_increases()
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

        save_increases(activity_increase, count_increase)
        save_previous_values(current_activity, current_count)
        save_current_time()

        return current_activity, current_count, activity_increase, count_increase


previous_activity, previous_count = load_previous_values()
current_activity, current_count, activity_increase, count_increase = reddit_check(
                                                         previous_activity, previous_count)
print(current_activity, current_count, activity_increase, count_increase)
