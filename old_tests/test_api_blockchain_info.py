from unittest import TestCase
from unittest.mock import patch, MagicMock
from api_blockchain_info import get_address_transactions_24h


class TestApiBlockchainInfo(TestCase):
    @patch('api_blockchain_info.session.get')
    def test_check_address_transactions_blockchain_info(self, mock_get):
        """
                Tests the `check_address_transactions_blockchain_info` function with a mocked GET request.
                The mocked response contains a sample transaction history for a given test address.
                The function should extract the total received and total sent amounts from the transaction history.

                Args:
                    self: the unittest.TestCase object.
                    mock_get: the mocked session.get function, which is patched using the @patch decorator.

                Returns:
                    None. The test passes if the function returns the expected total received and total sent amounts.
        """
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
        total_received, total_sent = get_address_transactions_24h(
            "bc1q0584qslzdwmjh8et2gaazls6d6e6g7sqejwlxj")

        # Assert the expected values
        self.assertEqual(total_received, 0.0)
        self.assertEqual(total_sent, 0.0)
