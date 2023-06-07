import requests
import logging
from typing import Tuple
import pandas as pd
from functools import wraps
from time import sleep
import plotly.graph_objects as go

from datetime import datetime, timedelta
from database import read_database
from binance.exceptions import BinanceAPIException, BinanceRequestException
from testnet_future_short_trade import initialized_future_client


BINANCE_ENDPOINT_PRICE = "https://api.binance.com/api/v3/ticker/price"
GECKO_ENDPOINT_PRICE = 'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd'
LATEST_INFO_FILE = "data/latest_info_saved.csv"
SYMBOL = 'BTCUSDT'
TRADE_RESULT_PATH = 'data/trades_results.csv'
TRADE_DETAILS_PATH = 'data/trades_details.csv'

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

update_intervals = {
    "dataset": timedelta(hours=24),
    "macro": timedelta(hours=24),
    "order_book": timedelta(minutes=10),
    "predicted_price": timedelta(hours=12),
    "technical_analysis": timedelta(hours=4),
    "richest_addresses": timedelta(minutes=20),
    "google_search": timedelta(hours=3),
    "reddit": timedelta(hours=8),
    "youtube": timedelta(hours=4),
    "sentiment_of_news": timedelta(hours=1),
    "richest_addresses_scrap": timedelta(hours=12),
    "weighted_score": timedelta(minutes=10),
}


def retry_on_error_fallback_0_0(max_retries: int = 3, delay: int = 5, allowed_exceptions: tuple = ()):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except allowed_exceptions as e:
                    retries += 1
                    logging.warning(f"Attempt {retries} failed with error: {e}. Retrying in {delay} seconds...")
                    sleep(delay)
            logging.error(f"All {max_retries} attempts failed. Returning fallback values (0, 0).")
            return 0, 0

        return wrapper

    return decorator


def retry_on_error_with_fallback(max_retries: int = 3, delay: int = 5,
                                 allowed_exceptions: tuple = (), fallback_values=None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except allowed_exceptions as e:
                    retries += 1
                    logging.warning(f"Attempt {retries} failed with error: {e}. Retrying in {delay} seconds...")
                    sleep(delay)
            logging.error(f"All {max_retries} attempts failed.")
            if fallback_values is not None:
                if fallback_values == "pass":
                    logging.error("Fallback value is 'pass'. Skipping this function.")
                    return
                else:
                    logging.error(f"Returning fallback values {fallback_values}.")
                    return fallback_values
            else:
                raise Exception(f"All {max_retries} attempts failed without a fallback value.")

        return wrapper

    return decorator


@retry_on_error_with_fallback(max_retries=3, delay=5, allowed_exceptions=(
        requests.ConnectionError,), fallback_values=False)
def check_internet_connection() -> bool:
    """
    Check if there is an internet connection.

    Returns:
        bool: True if there is an internet connection, False otherwise.
    """
    try:
        requests.get("http://www.google.com", timeout=5)
        return True
    except (requests.ConnectionError, requests.exceptions.Timeout, requests.exceptions.ReadTimeout):
        logging.warning("No internet connection available.")
        return False


def get_bitcoin_future_market_price() -> int:
    while True:
        if check_internet_connection():
            client = initialized_future_client()
            try:
                ticker = client.futures_ticker(symbol=SYMBOL)
                current_price = int(float(ticker['lastPrice']))
                return current_price
            except (BinanceAPIException, BinanceRequestException) as e:
                logging.error(f"Error: Could not connect to Binance API:{e}")
        else:
            logging.error("No internet connection.")
        logging.error('Sleep 61 Sec and try again to retrieve Bitcoin price')
        sleep(61)  # wait for 61 seconds before retrying


def get_bitcoin_price() -> int:
    """
    Retrieves the current Bitcoin price in USD from the CoinGecko API and Binance API.
    Continuously retries until a valid price is obtained.

    Returns:
        Int: The current Bitcoin price in USD or None if an error occurred.
    """
    while True:
        if check_internet_connection():
            try:
                response = requests.get(GECKO_ENDPOINT_PRICE)
                if response.status_code == 200:
                    data = response.json()
                    current_price = int(data['bitcoin']['usd'])
                    return current_price
            except requests.exceptions.RequestException as e:
                logging.error(f"Error: Could not connect to CoinGecko API:{e}")

            try:
                response = requests.get(BINANCE_ENDPOINT_PRICE, params={'symbol': 'BTCUSDT'})
                if response.status_code == 200:
                    return int(float(response.json()['price']))
            except requests.exceptions.RequestException as e:
                logging.error(f"Error: Could not connect to Binance API:{e}")
        else:
            logging.error("No internet connection.")
        logging.error(f"Error: Could not retrieve BTC price, Sleep for 61 seconds ")
        sleep(61)  # wait for 61 seconds before retrying


def compare_predicted_price(predicted_price: int, current_price: int) -> Tuple[float, float]:
    """
    Compare the predicted price to the current price and calculate the percentage difference.

    Args:
        predicted_price (int): The predicted price of Bitcoin.
        current_price (int): The current price of Bitcoin.

    Returns:
        tuple: bullish and bearish probabilities based on the price difference percentage.
    """
    activity_percentage = (predicted_price - current_price) / current_price * 100

    if activity_percentage > 0:
        if activity_percentage >= 5:
            return 1, 0
        elif activity_percentage >= 4:
            return 0.9, 0.1
        elif activity_percentage >= 3:
            return 0.8, 0.2
        elif activity_percentage >= 2:
            return 0.7, 0.3
        elif activity_percentage >= 1:
            return 0.6, 0.4
    elif activity_percentage <= 0:
        if activity_percentage <= -5:
            return 0, 1
        elif activity_percentage <= -4:
            return 0.1, 0.9
        elif activity_percentage <= -3:
            return 0.2, 0.8
        elif activity_percentage <= -2:
            return 0.3, 0.7
        elif activity_percentage <= -1:
            return 0.4, 0.6

    return 0, 0


def compare_google_search_trends(last_hour: int, two_hours_before: int) -> Tuple[float, float]:
    """
    Compare the search trends between the last hour and two hours before.

    Args:
        last_hour (int): The search volume of the last hour.
        two_hours_before (int): The search volume of two hours before the last hour.

    Returns:
        tuple: bullish and bearish probabilities based on the search trends.
    """
    if last_hour >= two_hours_before:
        if last_hour >= (two_hours_before * 1.25):
            return 1, 0
        elif last_hour >= (two_hours_before * 1.20):
            return 0.85, 0.15
        elif last_hour >= (two_hours_before * 1.15):
            return 0.75, 0.25
        elif last_hour >= (two_hours_before * 1.1):
            return 0.6, 0.4
        return 0, 0

    elif last_hour <= two_hours_before:
        if two_hours_before >= (last_hour * 1.25):
            return 0, 1
        elif two_hours_before >= (last_hour * 1.2):
            return 0.15, 0.85
        elif two_hours_before >= (last_hour * 1.15):
            return 0.25, 0.75
        elif two_hours_before >= (last_hour * 1.1):
            return 0.4, 0.6
        return 0, 0

    return 0, 0


def compare_send_receive_richest_addresses_wrapper() -> Tuple[float, float]:
    latest_info_saved = pd.read_csv(LATEST_INFO_FILE)
    total_received = latest_info_saved['total_received_coins_in_last_24'][0]
    total_sent = latest_info_saved['total_sent_coins_in_last_24'][0]

    # Save latest update time
    save_update_time('richest_addresses')

    activity_percentage = (total_received - total_sent) / total_sent * 100

    if activity_percentage > 0:
        if activity_percentage >= 50:
            return 1, 0
        elif activity_percentage >= 40:
            return 0.9, 0.1
        elif activity_percentage >= 30:
            return 0.8, 0.2
        elif activity_percentage >= 20:
            return 0.7, 0.3
        elif activity_percentage >= 10:
            return 0.6, 0.4

    elif activity_percentage <= 0:
        if activity_percentage <= -50:
            return 0, 1
        elif activity_percentage <= -40:
            return 0.1, 0.9
        elif activity_percentage <= -30:
            return 0.2, 0.8
        elif activity_percentage <= -20:
            return 0.3, 0.7
        elif activity_percentage <= -10:
            return 0.4, 0.6

    return 0, 0


def compare_send_receive_richest_addresses() -> Tuple[float, float]:
    database = read_database()
    richest_addresses_bullish = database['richest_addresses_bullish'][-1]
    richest_addresses_bearish = database['richest_addresses_bearish'][-1]
    return richest_addresses_bullish, richest_addresses_bearish


def should_update(factor: str) -> bool:
    latest_info_saved = pd.read_csv(LATEST_INFO_FILE)
    last_update_time_str = latest_info_saved.iloc[0][f'latest_{factor}_update']
    last_update_time = datetime.strptime(last_update_time_str, '%Y-%m-%d %H:%M:%S')

    return datetime.now() - last_update_time > update_intervals[factor]


def save_update_time(factor_name: str):
    """
    save update time

    Args:
        factor_name (str): the factor that get updated

    """

    latest_info_saved = pd.read_csv(LATEST_INFO_FILE)
    latest_info_saved.loc[0, f'latest_{factor_name}_update'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    latest_info_saved.to_csv(LATEST_INFO_FILE, index=False)


def save_trading_state(state: str):
    latest_info_saved = pd.read_csv(LATEST_INFO_FILE)
    latest_info_saved.loc[0, 'latest_trading_state'] = state
    latest_info_saved.to_csv(LATEST_INFO_FILE, index=False)


def read_current_trading_state() -> str:
    latest_info_saved = pd.read_csv(LATEST_INFO_FILE)
    state = latest_info_saved.iloc[0]['latest_trading_state']
    latest_info_saved.to_csv(LATEST_INFO_FILE, index=False)
    return state


def save_float_to_latest_saved(column: str, value: float):
    latest_info_saved = pd.read_csv(LATEST_INFO_FILE)
    latest_info_saved.loc[0, f'{column}'] = round(value, 2)
    latest_info_saved.to_csv(LATEST_INFO_FILE, index=False)


def save_int_to_latest_saved(column: str, value: int):
    latest_info_saved = pd.read_csv(LATEST_INFO_FILE)
    latest_info_saved.loc[0, f'{column}'] = value
    latest_info_saved.to_csv(LATEST_INFO_FILE, index=False)


def read_float_from_latest_saved(column: str) -> float:
    latest_info_saved = pd.read_csv(LATEST_INFO_FILE)
    retrieved_value = latest_info_saved.iloc[0][f'{column}']
    latest_info_saved.to_csv(LATEST_INFO_FILE, index=False)
    return retrieved_value


def compare_reddit(current_activity: float, previous_activity: float) -> Tuple[float, float]:

    activity_percentage = (current_activity - previous_activity) / previous_activity * 100
    if activity_percentage > 0:
        if activity_percentage >= 30:
            return 1, 0
        elif activity_percentage >= 20:
            return 0.9, 0.1
        elif activity_percentage >= 15:
            return 0.8, 0.2
        elif activity_percentage >= 10:
            return 0.7, 0.3
        elif activity_percentage >= 5:
            return 0.6, 0.4

    elif activity_percentage <= 0:
        if activity_percentage <= -30:
            return 0, 1
        elif activity_percentage <= -20:
            return 0.1, 0.9
        elif activity_percentage <= -15:
            return 0.2, 0.8
        elif activity_percentage <= -10:
            return 0.3, 0.7
        elif activity_percentage <= -5:
            return 0.4, 0.6

    return 0, 0


def save_trade_details(weighted_score: float, position_opening_time: str,
                       position_closing_time: str, position_type: str,
                       opening_price: int, close_price: int, pnl: float):

    # Read the existing trade details CSV
    df = pd.read_csv(TRADE_DETAILS_PATH)

    # Create a new row with the provided trade details
    new_row = {
        'weighted_score': weighted_score,
        'position_opening_time': position_opening_time,
        'position_closing_time': position_closing_time,
        'position_type': position_type,
        'opening_price': opening_price,
        'close_price': close_price,
        'PNL': pnl
    }

    # Use a list to store new rows
    new_rows = [new_row]

    # Create a new DataFrame from the list of new rows
    df_new = pd.DataFrame(new_rows)

    # Concatenate the new DataFrame with the original DataFrame
    df = pd.concat([df, df_new], ignore_index=True)

    # Save the updated DataFrame to the CSV file
    df.to_csv(TRADE_DETAILS_PATH, index=False)


def save_trade_result(pnl: float, weighted_score: float, trade_type: str):
    df = pd.read_csv(TRADE_RESULT_PATH)

    if 0.65 <= weighted_score < 0.70:
        weighted_score_category = '65to70'
    elif 0.70 <= weighted_score < 0.75:
        weighted_score_category = '70to75'
    elif 0.75 <= weighted_score < 0.80:
        weighted_score_category = '75to80'
    else:
        weighted_score_category = '80to100'

    # Locate the row with the specific model_name
    row_index = df[df['weighted_score_category'] == weighted_score_category].index[0]

    # Update the number_of_trades and PNL values for the specific model
    df.loc[row_index, 'total_trades'] += 1
    df.loc[row_index, 'PNL'] += pnl

    if trade_type == 'short':
        df.loc[row_index, 'short_trades'] += 1
    else:
        df.loc[row_index, 'long_trades'] += 1

    if pnl >= 0:
        df.loc[row_index, 'win_trades'] += 1
    else:
        df.loc[row_index, 'loss_trades'] += 1

    # Save the updated DataFrame to the CSV file
    df.to_csv(TRADE_RESULT_PATH, index=False)


def calculate_score_margin(weighted_score):
    if 0.65 <= weighted_score < 0.70:
        return 0.65
    elif 0.70 <= weighted_score < 0.75:
        return 0.68
    elif 0.75 <= weighted_score < 0.80:
        return 0.7
    else:
        return 0.65


def calculate_upcoming_events():
    latest_info_saved = pd.read_csv(LATEST_INFO_FILE).squeeze("columns")
    fed = datetime.strptime(latest_info_saved['interest_rate_announcement_date'][0], "%Y-%m-%d %H:%M:%S")
    cpi = datetime.strptime(latest_info_saved['cpi_announcement_date'][0], "%Y-%m-%d %H:%M:%S")
    ppi = datetime.strptime(latest_info_saved['ppi_announcement_date'][0], "%Y-%m-%d %H:%M:%S")

    now = datetime.utcnow()

    time_until_fed = fed - now
    time_until_cpi = cpi - now
    time_until_ppi = ppi - now

    fed_announcement = ''
    cpi_fed_announcement = ''
    ppi_fed_announcement = ''

    if time_until_fed.days >= 0:
        hours, remainder = divmod(time_until_fed.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        fed_announcement = f"Next FED: {time_until_fed.days}D, {hours}H,, {minutes}m"

    if time_until_cpi.days >= 0:
        hours, remainder = divmod(time_until_cpi.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        cpi_fed_announcement = f"Next CPI: {time_until_cpi.days}D, {hours}H, {minutes}m"

    if time_until_ppi.days >= 0:
        hours, remainder = divmod(time_until_ppi.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        ppi_fed_announcement = f"Next PPI: {time_until_ppi.days}D, {hours}H, {minutes}m"
    return fed_announcement if time_until_fed.days <= 2 else '',\
        cpi_fed_announcement if time_until_cpi.days <= 2 else '',\
        ppi_fed_announcement if time_until_ppi.days <= 2 else ''


def last_and_next_update(factor: str) -> Tuple[timedelta, timedelta]:
    latest_info_saved = pd.read_csv(LATEST_INFO_FILE)
    last_update_time_str = latest_info_saved.iloc[0][f'latest_{factor}_update']
    last_update_time = datetime.strptime(last_update_time_str, '%Y-%m-%d %H:%M:%S')

    # Calculate the time difference between now and the last update time
    time_since_last_update = datetime.now() - last_update_time

    if update_intervals[factor] < time_since_last_update:
        next_update = timedelta(seconds=0)  # equivalent to zero
    else:
        next_update = update_intervals[factor] - time_since_last_update
    return time_since_last_update, next_update


COLORS = {
    'red_chart': '#ca3f64',
    'green_chart': '#25a750',
    'white': '#FFFFFF',
    'black': '#000000',
    'lightgray': '#545454',
    'gray_text': '#fff'
}


def convert_time_to_str(timedelta_obj):
    total_seconds = timedelta_obj.total_seconds()
    hours = total_seconds // 3600
    minutes = (total_seconds // 60) % 60

    if int(hours) == 0:
        return f"{int(minutes)}m"
    else:
        return f"{int(hours)}h {int(minutes)}m ago"


def create_gauge_chart(bullish, bearish, factor):
    last_update_time, next_update = last_and_next_update(factor)

    last_update_time_str = convert_time_to_str(last_update_time)
    next_update_str = convert_time_to_str(next_update)

    if bullish == 0 and bearish == 0:
        value = 0
        gauge_steps = [
            {"range": [0, 1], "color": COLORS['lightgray']},
        ]
        bar_thickness = 0
    else:
        value = round(((bullish / (bullish + bearish)) * 1), 2)
        gauge_steps = [
            {"range": [0, 1], "color": COLORS['red_chart']}
        ]
        bar_thickness = 1

    mode_str = "gauge+number+delta"

    return go.Indicator(
        mode=mode_str,
        value=value,
        delta={"reference": 1},
        title={
            "text": f"L: {last_update_time_str},   N: {next_update_str}",
            "font": {"size": 12, "color": COLORS['gray_text']}
        },
        domain={"x": [0, 1], "y": [0, 1]},
        gauge={
            "axis": {"range": [0, 1], "showticklabels": False},
            "bar": {"color": COLORS['green_chart'], "thickness": bar_thickness},
            "steps": gauge_steps,
            "bgcolor": COLORS['black']
        },
        number={"font": {"size": 12, "color": COLORS['white']}},
    )


if __name__ == '__main__':
    create_gauge_chart(0.8, 0.2, 'weighted_score')
