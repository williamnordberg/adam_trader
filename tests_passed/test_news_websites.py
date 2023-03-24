import os
import sys
import unittest
from unittest import mock
from unittest.mock import MagicMock
from news_websites import check_sentiment_of_news


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestNewsWebsites(unittest.TestCase):
    def setUp(self):
        self.mock_response = MagicMock()
        self.mock_response.text = '''
        {
            "articles": [
                {
                    "content": "Positive news about cryptocurrency."
                },
                {
                    "content": "Negative news about cryptocurrency."
                }
            ]
        }
        '''
        self.mock_response.raise_for_status.return_value = None

    @mock.patch("news_websites.requests.get")
    def test_sentiment_positive(self, mock_get):
        """
        Tests the `check_sentiment_of_news` function with a mocked GET request response.
        The mocked response contains two news articles with opposite sentiment (positive and negative).
        The function should analyze the sentiment of the news content using a pre-trained machine learning model,
        and return False since the overall sentiment is positive.

        Args:
            self: the unittest.TestCase object.
            mock_get: the mocked requests.get function, which is patched using the @mock.patch decorator.

        Returns:
            None. The test passes if the check_sentiment_of_news function correctly returns False.
        """
        mock_get.return_value = self.mock_response

        result = check_sentiment_of_news()
        self.assertEqual(result, False)


if __name__ == "__main__":
    unittest.main()
