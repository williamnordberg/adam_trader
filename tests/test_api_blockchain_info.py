import unittest
from unittest.mock import patch, MagicMock
from api_blockchain_info import check_address_transactions_blockchain_info


class TestCheckAddressTransactionsBlockchainInfo(unittest.TestCase):

    @patch("api_blockchain_info.session.get")
    def test_check_address_transactions_blockchain_info(self, mock_get):
        # Mock the API response
        response = MagicMock()
        response.status_code = 200
        response.json.return_value = {
            "txs": [
                {
                    "time": 1628697600,  # A timestamp within the last 24 hours
                    "inputs": [
                        {
                            "prev_out": {
                                "addr": "test_address",
                                "value": 5 * 100000000  # 5 BTC in Satoshi
                            }
                        }
                    ],
                    "out": [
                        {
                            "addr": "other_address",  # Change this to a different address
                            "value": 5 * 100000000  # 5 BTC in Satoshi
                        }
                    ],
                    "hash": "test_tx_hash"
                }
            ]
        }
        mock_get.return_value = response

        # Call the function
        total_received, total_sent = check_address_transactions_blockchain_info("test_address")

        # Check if the returned values are correct
        self.assertEqual(total_received, 0)  # Change this to 0, since no BTC was received
        self.assertEqual(total_sent, 5)

    # ... (the other test case remains the same)


    @patch("api_blockchain_info.session.get")
    @patch("api_blockchain_info.time.sleep", side_effect=lambda x: None)
    def test_check_address_transactions_blockchain_info_rate_limited(self, mock_get, mock_sleep):
        # Mock the API response with a rate limit status code
        response = MagicMock()
        response.status_code = 429
        mock_get.return_value = response

        # Call the function
        total_received, total_sent = check_address_transactions_blockchain_info("test_address")

        # Check if the returned values are 0
        self.assertEqual(total_received, 0)
        self.assertEqual(total_sent, 0)
        # Check if sleep was called
        mock_sleep.assert_called()


if __name__ == "__main__":
    unittest.main()
