import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from monitor_2000_richest import read_addresses_from_csv, check_multiple_addresses,\
    monitor_bitcoin_richest_addresses
from api_blockcypher import get_address_transactions_24h_blockcypher
from api_blockchain_info import  get_address_transactions_24h


class TestMonitor2000Richest(unittest.TestCase):
    def test_read_addresses_from_csv(self):
        with patch('builtins.open', unittest.mock.mock_open(read_data="address1,address2,address3")) as mock_file:
            addresses = read_addresses_from_csv('fake_path')
            self.assertEqual(len(addresses), 1)
            self.assertIn("address1", addresses)

    @patch('monitor_2000_richest.check_address_transactions_blockchain_info')
    @patch('monitor_2000_richest.check_address_transactions_blockcypher')
    def test_check_multiple_addresses(self, mock_blockchain_info, mock_blockcypher):
        addresses = ['address1', 'address2', 'address3']
        mock_blockcypher.side_effect = [(1, 2), (3, 4), (5, 6)]
        mock_blockchain_info.side_effect = [(7, 8), (9, 10), (11, 12)]

        total_received, total_sent = check_multiple_addresses(addresses)

        self.assertEqual(total_received, 17)
        self.assertEqual(total_sent, 20)

    @patch('monitor_2000_richest.read_addresses_from_csv')
    @patch('monitor_2000_richest.check_multiple_addresses')
    @patch('pandas.read_csv')
    @patch('datetime.datetime')
    def test_monitor_bitcoin_richest_addresses(self, mock_datetime, mock_read_csv, mock_check_multiple_addresses,
                                               mock_read_addresses_from_csv):
        mock_datetime.now.return_value = mock_datetime.strptime("2023-03-23 12:00:00", '%Y-%m-%d %H:%M:%S')
        mock_read_csv.return_value = pd.DataFrame({'latest_richest_addresses_update': ['2023-03-23 07:00:00']})
        mock_read_addresses_from_csv.return_value = ['address1', 'address2', 'address3']
        mock_check_multiple_addresses.return_value = (10, 20)

        total_received, total_sent = monitor_bitcoin_richest_addresses()

        self.assertEqual(total_received, 10)
        self.assertEqual(total_sent, 20)


if __name__ == "__main__":
    unittest.main()
