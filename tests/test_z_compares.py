import unittest
from unittest.mock import patch
import pandas as pd

from z_compares import compare_macro_m_to_m, compare_order_volume,\
    compare_technical, compare_richest_addresses, compare_google_reddit_youtube,\
    compare_news, compare_predicted_price


class TestCompares(unittest.TestCase):

    def test_compare_predicted_price(self):
        self.assertEqual(compare_predicted_price(101, 100), (6, 4))

        self.assertEqual(compare_predicted_price(98, 100), (3, 7))

        self.assertEqual(compare_predicted_price(100, 100), (0.0, 0.0))

    def test_compare_macro_m_to_m(self):
        self.assertEqual(compare_macro_m_to_m(-0.76), (1.0, 0.0))
        self.assertEqual(compare_macro_m_to_m(-0.51), (0.85, 0.15))

    def test_compare_order_volume(self):
        self.assertEqual(compare_order_volume(0.57, 0), (0.7, 0.3))

        self.assertEqual(compare_order_volume(0, 0.57), (0.3, 0.7))

        self.assertEqual(compare_order_volume(0, 0.60), (0.2, 0.8))

        self.assertEqual(compare_order_volume(0, 0.63), (0.1, 0.9))

        self.assertEqual(compare_order_volume(0, 0.57), (0.3, 0.7))

        self.assertEqual(compare_order_volume(0.57, 0), (0.7, 0.3))

        self.assertEqual(compare_order_volume(0.60, 0), (0.8, 0.2))

        self.assertEqual(compare_order_volume(0.62, 0), (0.9, 0.1))

    def test_compare_technical(self):
        # testing with known inputs
        self.assertEqual(compare_technical('up', True, True), (1, 0))
        # testing with reversed inputs
        self.assertEqual(compare_technical('down', False, False), (0, 1))

    @patch('z_read_write_csv.read_database')
    def test_compare_richest_addresses(self, mock_read_database):
        mock_df = pd.DataFrame({
            'richest_addresses_total_received': [160],  # replace with your test data
            'richest_addresses_total_sent': [100]  # replace with your test data
        })
        mock_read_database.return_value = mock_df

        self.assertEqual(compare_richest_addresses(), (0.0, 1.0))

    def test_compare_google_reddit_youtube(self):
        # testing with known inputs
        result = compare_google_reddit_youtube(12, 11)
        self.assertEqual(result, (0.0, 0.0))
        # testing with inputs that lead to reversed result
        result = compare_google_reddit_youtube(11, 12)
        # self.assertEqual(result, (0.15, 0.85))

    def test_compare_news(self):
        # testing with known inputs
        result = compare_news(0.05, 0.04, 10, 12)
        self.assertEqual(result, (0.4, 0.6))
        # testing with inputs that lead to no changes
        result = compare_news(0.05, 0.04, 10, 10)
        # self.assertEqual(result, (0.5, 0.5))


if __name__ == '__main__':
    unittest.main()
