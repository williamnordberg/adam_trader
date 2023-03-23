import unittest
import pandas as pd
import numpy as np
from indicator_calculator import exponential_moving_average, bollinger_bands, relative_strength_index, macd


class TestIndicatorCalculator(unittest.TestCase):

    def test_exponential_moving_average(self):
        """
        Tests the `exponential_moving_average` function with a sample data and window size.
        The expected EMA values are calculated manually and compared with the actual values computed by the function.
        The function should return an array of EMA values for the input data and window size.

        Args:
            self: the unittest.TestCase object.

        Returns:
            None. The test passes if the EMA values computed by the function match the expected values.
        """
        data = [11, 12, 14, 18, 12, 15, 13, 16, 10]
        window_size = 2
        expected_ema = np.array([11., 11.6667, 13.2222, 16.4074, 13.4691, 14.4897, 13.4966, 15.1655, 11.7218])
        actual_ema = exponential_moving_average(data, window_size)
        np.testing.assert_array_almost_equal(expected_ema, actual_ema, decimal=4)

    def test_bollinger_bands_values(self):
        """
        Tests the `bollinger_bands` function with a sample data, window size, and standard deviation.
        The expected values for the upper band, rolling mean, and lower band are calculated manually and compared
        with the actual values computed by the function.
        The function should return three series of values for the upper band, rolling mean, and lower band,
        respectively, based on the input data, window size, and standard deviation.

        Args:
            self: the unittest.TestCase object.

        Returns:
            None. The test passes if the upper band, rolling mean, and lower band values computed by the function
            match the expected values.
        """
        data = pd.Series([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        window = 3
        std_dev = 1
        upper_band, rolling_mean, lower_band = bollinger_bands(data, window, std_dev)

        # Updated expected values for the upper Bollinger Band
        expected_upper_band = pd.Series([np.nan, np.nan, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0])

        expected_rolling_mean = pd.Series([np.nan, np.nan, 2., 3., 4., 5., 6., 7., 8., 9.])
        expected_lower_band = pd.Series([np.nan, np.nan, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0])

        pd.testing.assert_series_equal(upper_band, expected_upper_band, check_exact=False, rtol=1e-3, atol=1e-3)
        pd.testing.assert_series_equal(rolling_mean, expected_rolling_mean, check_exact=False, rtol=1e-3, atol=1e-3)
        pd.testing.assert_series_equal(lower_band, expected_lower_band, check_exact=False, rtol=1e-3, atol=1e-3)
        self.assertEqual(len(upper_band), len(data))
        self.assertEqual(len(rolling_mean), len(data))
        self.assertEqual(len(lower_band), len(data))

    def test_relative_strength_index(self):
        """
        Tests the `relative_strength_index` function with a sample data and window size.
        The expected RSI values are calculated manually and compared with the actual values computed by the function.
        The function should return a series of RSI values for the input data and window size.

        Args:
            self: the unittest.TestCase object.

        Returns:
            None. The test passes if the RSI values computed by the function match the expected values.
        """
        data = pd.Series([1, 20, 3, 40, 5, 60, 7, 80, 90, 10])
        window = 3
        rsi = relative_strength_index(data, window)

        # Expected values for RSI
        expected_rsi = pd.Series([0., 67.857143, 30.645161, 79.52381, 34.081633,
                                  76.423358, 34.148728, 73.907987, 77.611444, 23.727032])

        # Check the length of the RSI
        # self.assertEqual(len(rsi), len(data))

        # Compare the values of the calculated RSI and the expected RSI
        np.testing.assert_allclose(rsi, expected_rsi, rtol=1e-3, atol=1e-3)

    def test_macd(self):
        """
        Tests the `macd` function with a sample data and window sizes for the fast, slow, and signal lines.
        The expected MACD line, signal line, and histogram values are calculated manually and compared
        with the actual values computed by the function.
        The function should return three series of values for the MACD line, signal line, and histogram,
        respectively, based on the input data and window sizes.

        Args:
            self: the unittest.TestCase object.

        Returns:
            None. The test passes if the MACD line, signal line, and histogram values computed by the function
            match the expected values.
        """
        data = pd.Series([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        fast_window = 2
        slow_window = 4
        signal_window = 3
        macd_line, signal_line, histogram = macd(data, fast_window, slow_window, signal_window)

        # Expected values for MACD line, signal line, and histogram
        expected_macd_line = pd.Series([0., 0.266667, 0.515556, 0.694519, 0.811773, 0.885418,
                                        0.930702, 0.958238, 0.974882, 0.984909])
        expected_signal_line = pd.Series([0., 0.133333, 0.324444, 0.509481, 0.660627, 0.773022,
                                          0.851862, 0.90505, 0.939966, 0.962437])
        expected_histogram = pd.Series([0., 0.133333, 0.191111, 0.185037, 0.151146, 0.112395,
                                        0.07884, 0.053188, 0.034916, 0.022471])

        # Check the length of MACD line, signal line, and histogram
        self.assertEqual(len(macd_line), len(data))
        self.assertEqual(len(signal_line), len(data))
        self.assertEqual(len(histogram), len(data))

        # Compare the values of the calculated MACD line, signal line, and histogram with the expected values
        np.testing.assert_allclose(macd_line, expected_macd_line, rtol=1e-3, atol=1e-3)
        np.testing.assert_allclose(signal_line, expected_signal_line, rtol=1e-3, atol=1e-3)
        np.testing.assert_allclose(histogram, expected_histogram, rtol=1e-3, atol=1e-3)


if __name__ == '__main__':
    unittest.main()
