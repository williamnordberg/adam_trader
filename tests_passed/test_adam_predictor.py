import unittest
from unittest.mock import patch
import pandas as pd
import numpy as np
from adam_predictor import decision_tree_predictor


class TestDecisionTreePredictor(unittest.TestCase):

    @patch("adam_predictor.update_internal_factors")
    @patch("adam_predictor.update_yahoo_data")
    @patch("adam_predictor.update_macro_economic")
    @patch("adam_predictor.pd.read_csv")
    @patch("adam_predictor.pd.DataFrame.to_csv")
    def test_decision_tree_predictor(self, mock_to_csv, mock_read_csv, mock_update_macro, mock_update_yahoo,
                                     mock_update_internal):
        """
        Tests the `decision_tree_predictor` function with mocked data.
        The function should read data from CSV files, update the internal factors and external data, train a decision tree
        model, and make predictions using the latest data.

        Args:
            self: the unittest.TestCase object.
            mock_to_csv: the mocked pd.DataFrame.to_csv method.
            mock_read_csv: the mocked pd.read_csv method.
            mock_update_macro: the mocked update_macro_economic function.
            mock_update_yahoo: the mocked update_yahoo_data function.
            mock_update_internal: the mocked update_internal_factors function.

        Returns:
            None. The test passes if the function returns a numpy array of predictions, and calls the expected functions.
        """
        # Mock the data read
        latest_info_saved = pd.DataFrame({"latest_dataset_update": ["2022-01-01 00:00:00"]})
        main_dataset = pd.DataFrame({
            "Date": pd.date_range("2022-01-01", periods=5),
            "DiffLast": np.random.randn(5),
            "DiffMean": np.random.randn(5),
            "CapAct1yrUSD": np.random.randn(5),
            "HashRate": np.random.randn(5),
            "Open": np.random.randn(5),
            "Rate": np.random.randn(5),
            "Close": np.random.randn(5)
        })

        def side_effect(filename):
            if filename == "latest_info_saved.csv":
                return latest_info_saved
            elif filename == "main_dataset.csv":
                return main_dataset

        mock_read_csv.side_effect = side_effect
        mock_to_csv.return_value = None
        mock_update_internal.return_value = None
        mock_update_yahoo.return_value = None
        mock_update_macro.return_value = None

        # Call the function
        predictions_tree = decision_tree_predictor()

        # Check if the predictions are a numpy array
        self.assertIsInstance(predictions_tree, np.ndarray)

        # Check if the correct functions are called
        mock_update_internal.assert_called_once()
        mock_update_yahoo.assert_called_once()
        mock_update_macro.assert_called_once()
        mock_read_csv.assert_called()
        mock_to_csv.assert_called()


if __name__ == "__main__":
    unittest.main()
