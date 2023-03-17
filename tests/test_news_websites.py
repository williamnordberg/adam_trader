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
        mock_get.return_value = self.mock_response

        result = check_sentiment_of_news()
        self.assertEqual(result, False)


if __name__ == "__main__":
    unittest.main()
