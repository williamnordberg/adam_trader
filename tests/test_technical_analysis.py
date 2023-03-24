import unittest
from unittest.mock import patch
import pandas as pd

import technical_analysis as ta


class TestTechnicalAnalysis(unittest.TestCase):

    def setUp(self):
        self.sample_data = pd.Series([10000, 10100, 10200, 10300, 10400, 10500, 10600, 10700, 10800, 10900])

    @patch('technical_analysis.get_bitcoin_price', return_value=10900)
    def test_get_bitcoin_price(self, mocked_get_bitcoin_price):
        price = ta.get_bitcoin_price()
        self.assertEqual(price, 10900)
        mocked_get_bitcoin_price.assert_called_once()

    def test_potential_reversal(self):
        with patch('technical_analysis.data_close', self.sample_data):
            potential_up_reversal_bullish, Potential_down_reversal_bearish = ta.potential_reversal()
            self.assertIsInstance(potential_up_reversal_bullish, bool)
            self.assertIsInstance(Potential_down_reversal_bearish, bool)

    def test_potential_up_trending(self):
        with patch('technical_analysis.data_close', self.sample_data):
            potential_up_trend = ta.potential_up_trending()
            self.assertIsInstance(potential_up_trend, bool)

