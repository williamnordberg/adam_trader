import numpy as np
import pandas as pd
import requests


def get_bitcoin_price():
    """
    Retrieves the current Bitcoin price in USD from the CoinGecko API.
    """
    try:
        url = 'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd'
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            current_price_local = data['bitcoin']['usd']
            return current_price_local
        else:
            print("Error: Could not retrieve Bitcoin price data")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error: Could not connect to CoinGecko API:{e}")
        return None


# read the data
dataset = pd.read_csv('main_dataset.csv', index_col='Date')
data_close = dataset['Close']


def exponential_moving_average(data, window_size):
    """
    Calculates the exponential moving average (EMA) of a dataset with a specified window size.
    Args:
        data (list or numpy array): The input dataset.
        window_size (int): The size of the moving window used to calculate the EMA.
    Returns:
        The EMA of the input dataset as a numpy array.
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


def bollinger_bands(data, window=20, std_dev=1):
    # Calculate rolling mean and standard deviation
    rolling_mean = data.rolling(window=window).mean()
    rolling_std = data.rolling(window=window).std()

    # Calculate upper and lower bands
    upper_band = rolling_mean + (rolling_std * std_dev)
    lower_band = rolling_mean - (rolling_std * std_dev)

    return upper_band, rolling_mean, lower_band


def relative_strength_index(data_rsi, window):
    delta = data_rsi - np.roll(data_rsi, 1)
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)
    avg_gain = exponential_moving_average(gain, window)
    avg_loss = exponential_moving_average(loss, window)

    # Replace NaN values with zero to avoid division by zero error
    avg_gain = np.nan_to_num(avg_gain)
    avg_loss = np.nan_to_num(avg_loss)

    # Check for consecutive zero values in avg_loss
    zero_runs = np.split(avg_loss, np.where(avg_loss != 0)[0])
    for zero_run in zero_runs:
        if len(zero_run) > 1:
            # If there is a run of consecutive zero values, replace them with the previous non-zero value
            zero_start_idx = np.where(avg_loss == zero_run[0])[0][0]
            prev_non_zero = avg_loss[zero_start_idx - 1]
            avg_loss[zero_start_idx:zero_start_idx + len(zero_run)] = prev_non_zero

    # Add a small constant to avoid division by zero
    avg_loss = np.nan_to_num(avg_loss) + 1e-10

    # Calculate RS and RSI
    rs = avg_gain / avg_loss
    rsi = 100.0 - (100.0 / (1.0 + rs))
    return rsi


def macd(data_macd, fast_window=12, slow_window=26, signal_window=9):
    fast_ema = exponential_moving_average(data_macd, fast_window)
    slow_ema = exponential_moving_average(data_macd, slow_window)
    macd_in_func = fast_ema - slow_ema
    signal = exponential_moving_average(macd_in_func, signal_window)
    histogram = macd_in_func - signal
    return macd_in_func, signal, histogram


def potential_reversal():
    potential_up_reversal_bullish, Potential_down_reversal_bearish = False, False
    upper_band, moving_average, lower_band = bollinger_bands(data_close)
    current_price = data_close[-1]

    # MACD:  Calculate 70 percent between bands and moving averages
    distance_middle_lower = (moving_average[-1] - lower_band[-1]) * 0.7
    distance_middle_upper = (upper_band[-1] - moving_average[-1]) * 0.7

    # Check if price fill 70 percent of distance between bands and moving average
    rsi = relative_strength_index(data_close, 14)
    if current_price < moving_average[-1]:
        if (moving_average[-1] - current_price) > distance_middle_lower:
            potential_up_reversal_bullish = True
    elif current_price > moving_average[-1]:
        if (current_price-moving_average[-1]) > distance_middle_upper:
            Potential_down_reversal_bearish = True

    # check if today rsi is bigger than yesterday,and macd is over signal
    if rsi[-1] > 30:
        potential_up_reversal_bullish = True
    elif rsi[-1] > 70:
        Potential_down_reversal_bearish = True

    return potential_up_reversal_bullish, Potential_down_reversal_bearish


def potential_up_trending():
    rsi = relative_strength_index(data_close, 14)
    macd_line, signal, histogram = macd(data_close)

    # check if today rsi is bigger than yesterday,and macd is over signal
    if rsi[-1] > rsi[-2] or macd_line[-1] > signal[-1]:
        potential_up_trend = True
    else:
        potential_up_trend = False

    return potential_up_trend


def technical_analyse():
    potential_up_trend = potential_up_trending()
    potential_up_reversal_bullish, Potential_down_reversal_bearish = potential_reversal()
    technical_bullish, technical_bearish = False, False

    # Set initial value base on ema200
    ema200 = exponential_moving_average(data_close, 200)
    current_price = get_bitcoin_price()
    if current_price >= ema200[-1]:
        technical_bullish = True
    else:
        technical_bearish = True

    # check potentials
    if potential_up_reversal_bullish:
        technical_bullish = True
    elif potential_up_reversal_bullish:
        technical_bearish = True
    elif potential_up_trend:
        technical_bullish = True
    elif not potential_up_trend:
        technical_bearish = True

    return technical_bullish, technical_bearish


#technical_bullish1, technical_bearish1 = technical_analyse()
#print(technical_bullish1, technical_bearish1)
