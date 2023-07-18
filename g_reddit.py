import praw
import logging
import configparser
from typing import Tuple
from requests.exceptions import SSLError
from urllib3.exceptions import MaxRetryError
from prawcore.exceptions import RequestException


from z_read_write_csv import save_value_to_database, save_update_time, \
    should_update, read_latest_data, write_latest_data, retrieve_latest_factor_values_database
from z_handy_modules import retry_on_error
from z_compares import compare_google_reddit_youtube

ONE_DAYS_IN_SECONDS = 24 * 60 * 60
CONFIG_PATH = 'config/config.ini'


@retry_on_error(max_retries=3, delay=5, allowed_exceptions=(
        SSLError, MaxRetryError, RequestException), fallback_values=(0.0, 0.0))
def reddit_check_wrapper() -> Tuple[float, float]:

    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)

    reddit_config = config['reddit']
    reddit = praw.Reddit(
        client_id=reddit_config['client_id'],
        client_secret=reddit_config['client_secret'],
        user_agent=reddit_config['user_agent']
    )
    previous_activity = read_latest_data('reddit_previous_activity', int)

    current_activity = reddit.subreddit("Bitcoin").active_user_count
    reddit_bullish, reddit_bearish = compare_google_reddit_youtube(int(current_activity), int(previous_activity))

    write_latest_data('reddit_previous_activity', current_activity)

    save_value_to_database('reddit_activity_24h', current_activity)

    save_update_time('reddit')

    return reddit_bullish, reddit_bearish


def reddit_check() -> Tuple[float, float]:
    if should_update('reddit'):
        reddit_bullish, reddit_bearish = reddit_check_wrapper()

        # Save to database
        save_value_to_database('reddit_bullish', reddit_bullish)
        save_value_to_database('reddit_bearish', reddit_bearish)

        return reddit_bullish, reddit_bearish
    else:
        return retrieve_latest_factor_values_database('reddit')


if __name__ == '__main__':
    reddit_bullish_outer, reddit_bearish_outer = reddit_check_wrapper()
    logging.info(f", reddit_bullish: {reddit_bullish_outer}, reddit_bearish: {reddit_bearish_outer}")
