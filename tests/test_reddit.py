import unittest
from unittest.mock import patch, MagicMock

import pandas as pd

from reddit import reddit_check
from datetime import datetime


class TestReddit(unittest.TestCase):
    @patch('reddit.datetime')
    @patch('reddit.pd.read_csv')
    @patch('reddit.praw.Reddit')
    def test_reddit_check(self, mock_reddit, mock_read_csv, mock_datetime):
        # Mock the return values for pd.read_csv and praw.Reddit
        mock_read_csv.return_value = pd.DataFrame({'last_reddit_update_time': ['2023-03-21 08:30:00'],
                                                   'previous_activity': [110],
                                                   'previous_count': [1],
                                                   'last_activity_increase': [True],
                                                   'last_count_increase': [False]})
        mock_reddit_instance = MagicMock()
        mock_reddit_instance.subreddit('Bitcoin').active_user_count = 150
        mock_reddit_instance.subreddit('all').search.return_value = [
            MagicMock(created_utc=1646951025), MagicMock(created_utc=1646951026)]
        mock_reddit.return_value = mock_reddit_instance

        # Set up the datetime mocks
        mock_datetime.now.return_value = datetime(2023, 3, 25, 9, 30, 0)
        mock_datetime.strptime.return_value = datetime(2023, 3, 23, 8, 30, 0)

        # Call the function
        activity_increase, count_increase = reddit_check()

        # Check the return values
        self.assertEqual(activity_increase, True)
        self.assertEqual(count_increase, False)

        # Check that pd.read_csv was called with the correct file name
        mock_read_csv.assert_called_once_with('latest_info_saved.csv', squeeze=True)

        # Check that praw.Reddit was called with the correct arguments
        mock_reddit.assert_called_once_with(client_id='KiayZQKazH6eL_hTwlSgQw',
                                            client_secret='25JDkyyvbbAP-osqrzXykVK65w86mw',
                                            user_agent='btc_monitor_app:com.www.btc1231231:v1.0 (by /u/will7i7am)')

        # Check that praw.Reddit.subreddit was called with the correct arguments
        mock_reddit_instance.subreddit.assert_any_call('Bitcoin')
        mock_reddit_instance.subreddit.assert_any_call('all')

        # Check that praw.Reddit.subreddit.search was called with the correct arguments
        mock_reddit_instance.subreddit('all').search.assert_called_once_with(
            '#Crypto ', limit=1000)


if __name__ == '__main__':
    unittest.main()
