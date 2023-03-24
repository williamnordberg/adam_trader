import unittest
from unittest.mock import MagicMock, patch
import pandas as pd
import update_dataset_internal_factors as udf


class TestUpdateDatasetInternalFactors(unittest.TestCase):

    @patch("update_dataset_internal_factors.pd.read_csv")
    @patch("update_dataset_internal_factors.webdriver.Firefox")
    @patch("update_dataset_internal_factors.WebDriverWait")
    @patch("update_dataset_internal_factors.Select")
    def test_update_internal_factors(self, mock_select, mock_webdriver_wait, mock_firefox, mock_read_csv):
        # Set up the mock objects
        test_main_dataset = pd.DataFrame({
            "Date": ["2022-01-01", "2022-01-02", "2022-01-03"],
            "DiffLast": [1, 2, 3],
            "DiffMean": [4, 5, 6],
            "CapAct1yrUSD": [7, 8, 9],
            "HashRate": [10, 11, 12],
        })

        test_new_data = pd.DataFrame({
            "time": ["2022-01-04", "2022-01-05"],
            "DiffLast": [13, 14],
            "DiffMean": [15, 16],
            "CapAct1yrUSD": [17, 18],
            "HashRate": [19, 20],
        })

        expected_updated_dataset = pd.concat([test_main_dataset, test_new_data.rename(columns={'time': 'Date'})])
        mock_read_csv.side_effect = [test_main_dataset, test_new_data, expected_updated_dataset]
        mock_driver = MagicMock()
        mock_firefox.return_value = mock_driver
        mock_wait_instance = MagicMock()
        mock_webdriver_wait.return_value = mock_wait_instance
        mock_select_instance = MagicMock()
        mock_select.return_value = mock_select_instance

        # Run the function
        udf.update_internal_factors()

        # Check if the function has updated the main dataset
        main_dataset_updated = pd.read_csv('main_dataset.csv')
        expected_updated_dataset = pd.concat([test_main_dataset, test_new_data.rename(columns={'time': 'Date'})])

        # Assert that the main dataset has been updated correctly
        pd.testing.assert_frame_equal(main_dataset_updated, expected_updated_dataset)


if __name__ == "__main__":
    unittest.main()
