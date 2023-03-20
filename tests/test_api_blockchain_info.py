from unittest import TestCase
from unittest.mock import patch, MagicMock
from api_blockchain_info import check_address_transactions_blockchain_info


class TestApiBlockchainInfo(TestCase):
    @patch('api_blockchain_info.session.get')
    def test_check_address_transactions_blockchain_info(self, mock_get):
        # Define the mock response JSON
        mock_response_json = {
            "txs": [
                {
                    "time": 1679072298,
                    "inputs": [
                        {
                            "prev_out": {
                                "addr": "bc1q0584qslzdwmjh8et2gaazls6d6e6g7sqejwlxj",
                                "value": 500600356695
                            }
                        }
                    ],
                    "out": [
                        {
                            "addr": "bc1q9z9zn87tz0xrs7yv299geqtx3ed7q8f9se4xfn",
                            "value": 250000000000
                        },
                        {
                            "addr": "bc1q0584qslzdwmjh8et2gaazls6d6e6g7sqejwlxj",
                            "value": 250600300295
                        }
                    ],
                    "hash": "11c8d77185d04eb43374fb7a717685242be1c3d88af13733a4fedda672dd1f56"
                }
            ]
        }

        # Configure the mock to return the mock response JSON
        mock_get.return_value = MagicMock(status_code=200, json=lambda: mock_response_json)

        # Call the function with the test address
        total_received, total_sent = check_address_transactions_blockchain_info("bc1q0584qslzdwmjh8et2gaazls6d6e6g7sqejwlxj")

        # Assert the expected values
        self.assertEqual(total_received, 0.0)
        self.assertEqual(total_sent, 0.0)
