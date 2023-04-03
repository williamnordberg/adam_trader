import unittest
from unittest.mock import MagicMock, patch
import pandas as pd
import update_dataset_macro as udm
from fredapi import Fred


class TestUpdateDatasetMacro(unittest.TestCase):

    @patch("update_dataset_macro.Fred")
    @patch("update_dataset_macro.pd.read_csv")
    @patch("update_dataset_macro.pd.DataFrame.to_csv")
    def test_update_macro_economic(self, mock_to_csv, mock_read_csv, mock_fred):
        # Set up the mock objects
        test_main_dataset = pd.DataFrame({
            "Date": ["2022-01-01", "2022-01-02", "2022-01-03"],
            "Rate": [0.08, 0.08, 0.08],
            "Close": [1, 2, 3],
        })

        mock_read_csv.return_value = test_main_dataset
        mock_fred_instance = MagicMock(spec=Fred)
        mock_fred.return_value = mock_fred_instance
        mock_fred_instance.get_series.return_value = pd.Series(
            [0.08, 0.08, 0.09], index=pd.date_range('2022-01-01', periods=3, closed='left'))

        # Run the function
        udm.update_macro_economic()

        # Check if the function has updated the main dataset
        main_dataset_updated = pd.read_csv('../tests/main_dataset.csv')

        # Create the expected updated dataset
        expected_updated_dataset = test_main_dataset.copy()
        expected_updated_dataset.loc[expected_updated_dataset['Date'] == "2022-01-03", 'Rate'] = 0.09

        # Assert that the main dataset has been updated correctly
        pd.testing.assert_frame_equal(main_dataset_updated, expected_updated_dataset)

        # Assert that the updated dataset has been saved to a CSV file
        mock_to_csv.assert_called_once_with('main_dataset.csv', index=False)


if __name__ == "__main__":
    unittest.main()
