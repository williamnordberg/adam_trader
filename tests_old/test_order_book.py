import unittest
from unittest.mock import patch, MagicMock
from order_book import get_price, get_order_book, get_probabilities, get_probabilities_hit_profit_or_stop


class TestOrderBook(unittest.TestCase):
    @patch('order_book.requests.Session')
    def test_get_price(self, mock_session):
        mock_session.get.return_value.json.return_value = {'price': '100'}
        price = get_price('BTCUSDT', mock_session)
        self.assertEqual(price, 100)

    @patch('order_book.requests.Session')
    def test_get_order_book(self, mock_session):
        mock_session.get.return_value.json.return_value = {'some_key': 'some_value'}
        order_book = get_order_book('BTCUSDT', 1000, mock_session)
        self.assertEqual(order_book, {'some_key': 'some_value'})

    @patch('order_book.get_order_book')
    @patch('order_book.get_price')
    def test_get_probabilities(self, mock_get_price, mock_get_order_book):
        mock_get_price.return_value = 100
        mock_get_order_book.return_value = {
            'bids': [['99', '1'], ['95', '2'], ['91', '3']],
            'asks': [['101', '1'], ['105', '2'], ['109', '3']]
        }
        prob_down, prob_up = get_probabilities(['BTCUSDT'], 1000, 0.9, 1.1)
        self.assertAlmostEqual(prob_down, 0.4999999958333333, places=2)
        self.assertAlmostEqual(prob_up, 0.5000000041666666, places=2)

    @patch('order_book.get_order_book')
    @patch('order_book.get_price')
    def test_get_probabilities_hit_profit_or_stop(self, mock_get_price, mock_get_order_book):
        mock_get_price.return_value = 12345.67
        mock_get_order_book.return_value = {
            'bids': [['10000', '1'], ['12000', '2'], ['12200', '3']],
            'asks': [['12500', '4'], ['13000', '5'], ['13500', '6']]
        }
        prob_target, prob_stop_loss = get_probabilities_hit_profit_or_stop(['BTCUSDT'], 1000, 13000, 10000)
        self.assertAlmostEqual(prob_target, 0.4, places=2)
        self.assertAlmostEqual(prob_stop_loss, 0.6, places=2)


if __name__ == '__main__':
    unittest.main()
