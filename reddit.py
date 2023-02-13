import praw
import time


def monitor_activity(previous_activity_in_function):
    reddit_in_function = praw.Reddit(client_id='KiayZQKazH6eL_hTwlSgQw',
                                     client_secret='25JDkyyvbbAP-osqrzXykVK65w86mw',
                                     user_agent='btc_monitor_app:com.www.btc1231231:v1.0 (by /u/will7i7am)')

    bitcoin_subreddit = reddit_in_function.subreddit("Bitcoin")
    current_activity = bitcoin_subreddit.active_user_count
    if current_activity > previous_activity_in_function:
        print("Activity level increased from {} to {}".format(previous_activity_in_function, current_activity))
    return current_activity


def count_bitcoin_posts(reddit_in_function):
    subreddit = reddit_in_function.subreddit("all")
    bitcoin_posts = subreddit.search("#Crypto ", limit=1000)
    count = 0
    for post in bitcoin_posts:
        if post.created_utc > (time.time() - 7 * 24 * 60 * 60):
            count += 1
    print("Number of posts containing the 'Bitcoin' hashtag in the last week: ", count)


reddit = praw.Reddit(client_id='KiayZQKazH6eL_hTwlSgQw',
                     client_secret='25JDkyyvbbAP-osqrzXykVK65w86mw',
                     user_agent='btc_monitor_app:com.www.btc1231231:v1.0 (by /u/will7i7am)')

previous_activity = 0
while True:
    previous_activity = monitor_activity(previous_activity)
    count_bitcoin_posts(reddit)
    time.sleep(30)  # Change this to set the time between each iteration
