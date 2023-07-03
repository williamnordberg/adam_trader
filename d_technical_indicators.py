import numpy as np
from typing import Tuple, List, Union
import pandas as pd


def simple_moving_average(data: np.ndarray, window: int) -> np.ndarray:
    sma = np.cumsum(data, dtype=float)
    sma[window:] = sma[window:] - sma[:-window]
    sma[:window - 1] = np.nan
    sma /= window
    return sma


def relative_strength_index(data_rsi: pd.Series, window: int) -> np.ndarray:
    """
        Calculates the Relative Strength Index (RSI) of a dataset.

        Args:
            data_rsi (pandas.Series): The input dataset.
            window (int): The size of the window used to calculate the RSI.

        Returns:
            numpy array: The RSI of the input dataset.
        """
    delta = data_rsi - np.roll(data_rsi, 1)
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)
    avg_gain = simple_moving_average(gain, window)
    avg_loss = simple_moving_average(loss, window)

    # Replace NaN values with zero to avoid division by zero error
    avg_gain = np.nan_to_num(avg_gain)
    avg_loss = np.nan_to_num(avg_loss)

    # Add a small constant to avoid division by zero
    avg_loss = np.nan_to_num(avg_loss) + 1e-10

    # Calculate RS and RSI
    rs = avg_gain / avg_loss
    rsi = 100.0 - (100.0 / (1.0 + rs))

    return rsi


def exponential_moving_average(data: Union[List[float], np.ndarray, pd.Series], window_size: int) -> np.ndarray:
    """
    Calculates the exponential moving average (EMA) of a dataset with a specified window size.

    Args:
        data (list or numpy array): The input dataset.
        window_size (int): The size of the moving window used to calculate the EMA.

    Returns:
        numpy array: The EMA of the input dataset.
    """

    # Convert data to numpy array
    data = np.array(data)

    # Calculate the weighting multiplier
    alpha = 2 / (window_size + 1)

    # Initialize the EMA with the first value of the input data
    ema = [data[0]]

    # Calculate the EMA for the remaining data points
    for i in range(1, len(data)):
        ema.append(alpha * data[i] + (1 - alpha) * ema[i - 1])

    return np.array(ema)


def bollinger_bands(data: pd.Series, window: int = 20, std_dev: int = 2) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """
       Calculates the upper and lower Bollinger Bands for a dataset.

       Args:
           data (pandas.Series): The input dataset.
           window (int): The size of the rolling window used to calculate the rolling mean and standard deviation.
           std_dev (int): The number of standard deviations to add and subtract from the rolling mean to calculate
            the bands.

       Returns:
           tuple: A tuple containing the upper band, rolling mean, and lower band as pandas.Series.
       """
    # Calculate rolling mean and standard deviation
    rolling_mean = data.rolling(window=window).mean()
    rolling_std = data.rolling(window=window).std()

    # Calculate upper and lower bands
    upper_band = rolling_mean + (rolling_std * std_dev)
    lower_band = rolling_mean - (rolling_std * std_dev)

    return upper_band, rolling_mean, lower_band


def macd(data_macd: pd.Series, fast_window: int = 12, slow_window: int = 26, signal_window: int = 9)\
        -> Tuple[np.ndarray, np.ndarray, np.ndarray]:

    """
      Calculates the Moving Average Convergence Divergence (MACD) of a dataset.

      Args:
          data_macd (pandas.Series): The input dataset.
          fast_window (int): The size of the window used to calculate the fast exponential moving average (EMA).
          slow_window (int): The size of the window used to calculate the slow EMA.
          signal_window (int): The size of the window used to calculate the signal line EMA.

      Returns:
          tuple: A tuple containing the MACD line, signal line, and histogram as pandas.Series.
      """
    fast_ema = exponential_moving_average(data_macd, fast_window)
    slow_ema = exponential_moving_average(data_macd, slow_window)
    macd_in_func = fast_ema - slow_ema
    signal = exponential_moving_average(macd_in_func, signal_window)
    histogram = macd_in_func - signal
    return macd_in_func, signal, histogram
