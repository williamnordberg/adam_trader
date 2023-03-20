import unittest
from unittest.mock import patch
import json

from api_blockcypher import check_address_transactions_blockcypher

class TestAPIBlockcypher(unittest.TestCase):

    def test_successful_response(self):
        mock_response_json = {
            "txs": [
                {
                    "received": "2023-03-18T09:55:24",
                    "outputs": [
                        {
                            "addresses": ["bc1q0584qslzdwmjh8et2gaazls6d6e6g7sqejwlxj"],
                            "value": 1000000000  # 10 BTC in satoshi
                        }
                    ],
                    "inputs": [
                        {
                            "addresses": ["bc1q0584qslzdwmjh8et2gaazls6d6e6g7sqejwlxj"],
                            "output_value": 5000000000  # 50 BTC in satoshi
                        }
                    ]
                }
            ]
        }

        with patch('api_blockcypher.session.get') as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = mock_response_json

            received, sent = check_address_transactions_blockcypher('bc1q0584qslzdwmjh8et2gaazls6d6e6g7sqejwlxj')

        self.assertEqual(received, 10)
        self.assertEqual(sent, 50)

    def test_rate_limit_response(self):
        with patch('api_blockcypher.session.get') as mock_get:
            mock_get.return_value.status_code = 429

            with patch('api_blockcypher.time.sleep'):  # To avoid waiting during the test
                received, sent = check_address_transactions_blockcypher('bc1q0584qslzdwmjh8et2gaazls6d6e6g7sqejwlxj')

        self.assertEqual(received, 0)
        self.assertEqual(sent, 0)

    def test_error_response(self):
        with patch('api_blockcypher.session.get') as mock_get:
            mock_get.return_value.status_code = 400

            received, sent = check_address_transactions_blockcypher('bc1q0584qslzdwmjh8et2gaazls6d6e6g7sqejwlxj')

        self.assertEqual(received, 0)
        self.assertEqual(sent, 0)


if __name__ == '__main__':
    unittest.main()
