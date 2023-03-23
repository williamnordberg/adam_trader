import unittest
from unittest.mock import patch, MagicMock
from position import long_position_is_open, short_position_is_open


class TestPosition(unittest.TestCase):

    @patch('position.get_bitcoin_price')
    @patch('position.get_probabilities')
    @patch('position.get_probabilities_hit_profit_or_stop')
    @patch('position.reddit_check')
    @patch('position.check_bitcoin_youtube_videos_increase')  # Add a patch for check_bitcoin_youtube_videos_increase
    @patch('position.decision_tree_predictor')
    def test_long_position_is_open(self, mock_youtube_increase, mock_reddit_check,
                                   mock_get_probabilities_hit_profit_or_stop,
                                   mock_get_probabilities, mock_get_bitcoin_price, mock_decision_tree_predictor):
        # Set up mock values
        mock_get_bitcoin_price.return_value = 30000.0
        mock_get_probabilities.return_value = (0.4, 0.6)
        mock_get_probabilities_hit_profit_or_stop.return_value = (0.7, 0.3)
        mock_reddit_check.return_value = (1, 1)  # Set a mock return value for reddit_check with only 2 values
        mock_youtube_increase.return_value = False  # Set a mock return value for check_bitcoin_youtube_videos_increase
        mock_decision_tree_predictor.return_value = 31000.0

        # Call the function and check the results
        profit, loss = long_position_is_open()
        self.assertGreater(profit, 0)
        self.assertEqual(loss, 0)

    @patch('position.get_bitcoin_price')
    @patch('position.get_probabilities')
    @patch('position.get_probabilities_hit_profit_or_stop')
    @patch('position.reddit_check')
    @patch('position.check_bitcoin_youtube_videos_increase')
    @patch('position.decision_tree_predictor')
    def test_short_position_is_open(self, mock_youtube_increase, mock_reddit_check,
                                    mock_get_probabilities_hit_profit_or_stop,
                                    mock_get_probabilities, mock_get_bitcoin_price,
                                    mock_decision_tree_predictor):
        # Set up mock values
        mock_get_bitcoin_price.return_value = 30000
        mock_get_probabilities.return_value = (0.6, 0.4)
        mock_get_probabilities_hit_profit_or_stop.return_value = (0.7, 0.3)
        mock_reddit_check.return_value = (1, 1)  # Set a mock return value for reddit_check with only 2 values
        mock_youtube_increase.return_value = False  # Set a mock return value for check_bitcoin_youtube_videos_increase
        mock_decision_tree_predictor.return_value = 29000.0

        # Call the function and check the results
        profit, loss = short_position_is_open()
        self.assertGreater(profit, 0)
        self.assertEqual(loss, 0)


if __name__ == '__main__':
    unittest.main()
