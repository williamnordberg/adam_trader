import numpy as np


def exponential_moving_average(data_in_function, window):
    weights = np.exp(np.linspace(-1., 0., window))
    weights /= weights.sum()
    a = np.convolve(data_in_function, weights, mode='full')[:len(data_in_function)]
    a[:window] = a[window]
    return a


def bollinger_bands(data_to_bb, window, num_std_dev):
    moving_average = exponential_moving_average(data_to_bb, window)
    std_dev = np.std(data_to_bb)
    upper_band = moving_average + num_std_dev * std_dev
    lower_band = moving_average - num_std_dev * std_dev
    return upper_band, moving_average, lower_band


def relative_strength_index(data_rsi, window):
    delta = data_rsi - np.roll(data_rsi, 1)
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)
    avg_gain = exponential_moving_average(gain, window)
    avg_loss = exponential_moving_average(loss, window)
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