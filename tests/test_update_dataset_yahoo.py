import unittest
from unittest.mock import patch
import pandas as pd
from datetime import datetime
import update_dataset_yahoo as udy


class TestUpdateDatasetYahoo(unittest.TestCase):

    @patch('pandas.read_csv')
    @patch('yfinance.Ticker')
    def test_update_yahoo_data(self, mock_ticker, mock_read_csv):
        # Prepare mock data
        mock_main_dataset = pd.DataFrame({'Date': ['2022-12-01', '2022-12-02'],
                                          'Open': [100, 200],
                                          'Close': [150, 250]})
        mock_new_data = pd.DataFrame({'Date': pd.to_datetime(['2022-12-03', '2022-12-04']),
                                      'Open': [300, 400],
                                      'Close': [350, 450]})

        mock_new_data.set_index('Date', inplace=True)

        # Mock read_csv and Ticker.history method
        mock_read_csv.return_value = mock_main_dataset
        mock_ticker.return_value.history.return_value = mock_new_data

        # Call update_yahoo_data
        udy.update_yahoo_data()

        # Verify that read_csv was called with the correct arguments
        mock_read_csv.assert_called_once_with('main_dataset.csv', dtype={146: str})

        # Verify that Ticker.history was called with the correct arguments
        mock_ticker.return_value.history.assert_called_once_with(
            start=mock_main_dataset.loc[mock_main_dataset['Open'].last_valid_index(), 'Date'],
            end=datetime.today().strftime('%Y-%m-%d'))


if __name__ == "__main__":
    unittest.main()
