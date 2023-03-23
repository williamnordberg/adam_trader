import unittest
from unittest.mock import patch
import requests
from google_search import check_internet_connection, check_search_trend, TrendReq
from pytrends.request import TrendReq as OriginalTrendReq
import pandas as pd


class TestGooglesearch(unittest.TestCase):
    @patch('requests.get')
    def test_check_internet_connection(self, mock_get):
        mock_get.return_value.ok = True
        self.assertTrue(check_internet_connection())

    @patch('requests.get')
    def test_check_internet_connection_no_connection(self, mock_get):
        mock_get.side_effect = requests.ConnectionError()
        self.assertFalse(check_internet_connection())

    @patch("google_search.TrendReq")
    def test_check_search_trend(self, mock_trend_req):
        """
        Tests the `check_internet_connection` function with a mocked GET request.
        The mocked response has a status code of 200 to simulate a successful connection.
        The function should return True if the GET request is successful and False otherwise.

        Args:
            self: the unittest.TestCase object.
            mock_trend_req: the mocked requests.get function, which is patched using the @patch decorator.

        Returns:
            None. The test passes if the function returns True for a successful connection.
        """
        mock_trend_req.return_value.interest_over_time.return_value = pd.DataFrame({
            "Bitcoin": [50, 60, 70, 80, 100],
            "isPartial": [False, False, False, False, False]
        })
        self.assertTrue(check_search_trend(["Bitcoin"], threshold=1.2))

    @patch("google_search.TrendReq")
    def test_check_search_trend_no_increase(self, mock_trend_req):
        mock_trend_req.return_value.interest_over_time.return_value = pd.DataFrame({
            "Bitcoin": [50, 60, 70, 80, 90],
            "isPartial": [False, False, False, False, False]
        })
        self.assertFalse(check_search_trend(["Bitcoin"], threshold=1.2))

    @patch("google_search.TrendReq")
    def test_check_search_trend_no_connection(self, mock_trend_req):
        with patch("google_search.check_internet_connection", return_value=False):
            mock_trend_req.side_effect = Exception("An error occurred.")
            self.assertFalse(check_search_trend(["Bitcoin"], threshold=1.2))

    def test_TrendReq_inherits_UTrendReq(self):
        self.assertTrue(issubclass(TrendReq, OriginalTrendReq))


if __name__ == "__main__":
    unittest.main()
