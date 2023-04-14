import pandas as pd
import ccxt
import logging
from typing import Tuple

from indicator_calculator import bollinger_bands, exponential_moving_average, macd, relative_strength_index
from handy_modules import get_bitcoin_price
from database import save_value_to_database


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def get_historical_data(symbol: str, timeframe: str, limit: int) -> pd.Series:
    """
      Retrieves historical price data for a cryptocurrency from the Binance API.

      Args:
          symbol (str): The symbol of the cryptocurrency to retrieve data for.
          timeframe (str): The timeframe to retrieve data for (e.g. '1d' for daily data).
          limit (int): The number of data points to retrieve.

      Returns:
          pandas.Series: A pandas Series containing the historical price data.
      """
    exchange = ccxt.binance()
    ohlcv = exchange.fetch_ohlcv(symbol=symbol, timeframe=timeframe, limit=limit)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    close_series = df['close']
    return close_series


def potential_reversal(data_close: pd.Series) -> Tuple[bool, bool]:
    """
       Identifies whether a potential bullish or bearish reversal is forming.

       Returns:
           tuple: A tuple containing the potential bullish and bearish reversal flags as booleans.
       """
    potential_up_reversal_bullish, potential_down_reversal_bearish = False, False
    upper_band, moving_average, lower_band = bollinger_bands(data_close)
    current_price = int(data_close.iloc[-1])

    # Check if price fill 70 percent of distance between bands and moving average
    last_moving_average = int(moving_average.iloc[-1]) if not pd.isna(moving_average.iloc[-1]) else 0
    last_lower_band = int(lower_band.iloc[-1]) if not pd.isna(lower_band.iloc[-1]) else 0
    last_upper_band = int(upper_band.iloc[-1]) if not pd.isna(upper_band.iloc[-1]) else 0

    distance_middle_lower = int((last_moving_average - last_lower_band) * 0.7) if not pd.isna(
        moving_average.iloc[-1]) and not pd.isna(lower_band.iloc[-1]) else 0
    distance_middle_upper = int((last_upper_band - last_moving_average) * 0.7) if not pd.isna(
        upper_band.iloc[-1]) and not pd.isna(moving_average.iloc[-1]) else 0

    if not pd.isna(current_price) and not pd.isna(last_moving_average):
        if current_price < last_moving_average:
            if (last_moving_average - current_price) > distance_middle_lower:
                potential_up_reversal_bullish = True
        elif current_price > last_moving_average:
            if (current_price - last_moving_average) > distance_middle_upper:
                potential_down_reversal_bearish = True

    # RSI overbought or oversold
    rsi = relative_strength_index(data_close, 14)
    if rsi[-1] > 30:
        potential_up_reversal_bullish = True
    elif rsi[-1] > 70:
        potential_down_reversal_bearish = True

    save_value_to_database('technical_potential_up_reversal_bullish', potential_up_reversal_bullish)
    save_value_to_database('technical_potential_down_reversal_bearish',potential_down_reversal_bearish)
    return potential_up_reversal_bullish, potential_down_reversal_bearish


def potential_up_trending(data_close: pd.Series) -> bool:
    """
       Identifies whether a potential uptrend is forming.

       Returns:
           bool: The potential uptrend flag.
       """
    rsi = relative_strength_index(data_close, 14)
    macd_line, signal, histogram = macd(data_close)

    # check if today rsi is bigger than yesterday,and macd is over signal
    if rsi[-1] > rsi[-2] or macd_line[-1] > signal[-1]:
        potential_up_trend = True
    else:
        potential_up_trend = False

    save_value_to_database('technical_potential_up_trend', potential_up_trend)
    return potential_up_trend


def technical_analyse_wrapper() -> Tuple[float, float]:
    """
       Performs a technical analysis of the Bitcoin market using various indicators.

       Returns:
           tuple: A tuple containing the bullish and bearish technical analysis flags as booleans.
       """
    # read the data
    data_close = get_historical_data('BTC/USDT', '1d', 200)

    potential_up_reversal_bullish, potential_down_reversal_bearish = potential_reversal(data_close)
    potential_up_trend = potential_up_trending(data_close)

    # Set initial value base on ema200
    ema200 = exponential_moving_average(data_close, 200)
    current_price = get_bitcoin_price()

    # check potentials
    if potential_up_reversal_bullish and potential_up_trend and (current_price >= ema200[-1]):
        return 1, 0
    elif potential_down_reversal_bearish and not potential_up_trend and (current_price >= ema200[-1]):
        return 0, 1

    # potential and rsi and macd trend
    elif potential_up_reversal_bullish and potential_up_trend and not(current_price >= ema200[-1]):
        return 0.9, 0.1
    elif potential_down_reversal_bearish and not potential_up_trend and (current_price >= ema200[-1]):
        return 0.1, 0.9

    # just reversal
    elif potential_up_reversal_bullish and not potential_up_trend and (current_price >= ema200[-1]):
        return 0.75, 0.25
    elif potential_down_reversal_bearish and potential_up_trend and (current_price >= ema200[-1]):
        return 0.75, 0.25

    # just ris and macd trend
    elif not potential_up_reversal_bullish and potential_up_trend and not (current_price >= ema200[-1]):
        return 0.65, 0.35
    elif not potential_down_reversal_bearish and not potential_up_trend and (current_price >= ema200[-1]):
        return 0.35, 0.65

    # just EMA
    elif not potential_up_reversal_bullish and not potential_up_trend and (current_price >= ema200[-1]):
        return 0.6, 0.4
    elif not potential_down_reversal_bearish and not potential_up_trend and (current_price >= ema200[-1]):
        return 0.4, 0.6

    return 0, 0


def technical_analyse() -> Tuple[float, float]:
    # Call the original technical_analyse function
    technical_bullish, technical_bearish = technical_analyse_wrapper()

    # Save the values to the database
    save_value_to_database('technical_bullish', technical_bullish)
    save_value_to_database('technical_bearish', technical_bearish)

    # Return the same values as the original function
    return technical_bullish, technical_bearish


if __name__ == '__main__':
    technical_bullish1, technical_bearish1 = technical_analyse()
    logging.info(f'Bullish: {technical_bullish1}, Bearish: {technical_bearish1}')
