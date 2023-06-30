from typing import TypeVar, Type, Any, Dict, Tuple
import pandas as pd
import logging
from functools import wraps
from time import sleep
from datetime import datetime, timedelta

LATEST_INFO_FILE = "data/latest_info_saved.csv"
DATABASE_PATH = 'data/database.csv'
DATASET_PATH = 'data/dataset.csv'
TRADE_RESULT_PATH = 'data/trades_results.csv'
TRADE_DETAILS_PATH = 'data/trades_details.csv'

CSV_ALLOWED_EXCEPTIONS = (pd.errors.EmptyDataError, FileNotFoundError, PermissionError, pd.errors.ParserError, IOError)
T = TypeVar('T')
fallback_values_types = {str: '', int: 0, float: 0.0, datetime: datetime.min}


def retry_on_error(max_retries: int = 3, delay: int = 5,
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


def retry_latest_file_read(max_retries: int = 3, delay: int = 5,
                           allowed_exceptions: tuple = (), fallback_values=None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            data_type = kwargs.get('data_type') or args[-1]  # assumes data_type is the last arg
            fallback_value = fallback_values.get(data_type, None)
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except allowed_exceptions as e:
                    retries += 1
                    logging.warning(f"Attempt {retries} failed with error: {e}. Retrying in {delay} seconds...")
                    sleep(delay)
            logging.error(f"All {max_retries} attempts failed.")
            if fallback_value is not None:
                logging.error(f"Returning fallback value {fallback_value}.")
                return fallback_value
            else:
                raise Exception(f"All {max_retries} attempts failed without a fallback value.")

        return wrapper

    return decorator


@retry_latest_file_read(max_retries=3, delay=5, allowed_exceptions=CSV_ALLOWED_EXCEPTIONS,
                        fallback_values=fallback_values_types)
def read_latest_data(column: str, data_type: Type[T]) -> T:
    latest_info_saved = pd.read_csv(LATEST_INFO_FILE)
    retrieved_value = latest_info_saved.iloc[0][column]
    if data_type == datetime:
        return datetime.strptime(retrieved_value, '%Y-%m-%d %H:%M:%S')  # type: ignore
    else:
        return data_type(retrieved_value)  # type: ignore


@retry_on_error(max_retries=3, delay=5, allowed_exceptions=CSV_ALLOWED_EXCEPTIONS,
                fallback_values=None)
def write_latest_data(column: str, value: Any):
    latest_info_saved = pd.read_csv(LATEST_INFO_FILE)
    latest_info_saved.at[0, column] = value
    latest_info_saved.to_csv(LATEST_INFO_FILE, index=False)


update_intervals = {
    "dataset": timedelta(hours=24),
    "macro": timedelta(hours=1) if datetime.now() <= read_latest_data('next-fed-announcement', datetime)
    else timedelta(hours=24),
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


def parse_date(date_str):
    if not date_str:
        return None
    return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')


@retry_on_error(max_retries=3, delay=5, allowed_exceptions=CSV_ALLOWED_EXCEPTIONS,
                fallback_values=pd.DataFrame())
def read_database() -> pd.DataFrame:
    """Read the CSV file into a DataFrame and set the "date" column as the index"""
    df = pd.read_csv(DATABASE_PATH, converters={"date": parse_date})
    df.set_index("date", inplace=True)
    return df


@retry_on_error(max_retries=3, delay=5, allowed_exceptions=CSV_ALLOWED_EXCEPTIONS,
                fallback_values=None)
def save_value_to_database(column: str, value: Any):
    """Get the value and column name and save it in the database base of current hour"""
    # Get the current datetime and round it down to the nearest hour
    current_hour = pd.Timestamp.now().floor("H")

    df = read_database()

    # Check if there's an existing row for the current hour
    if current_hour in df.index:
        # Update the existing row with the new value
        df.at[current_hour, column] = value
    else:
        # Initialize a new row with all columns set to None
        new_row_data: Dict[str, Any] = {col: None for col in df.columns}

        # Set the date and the provided column's value
        new_row_data[column] = value

        # Create a new DataFrame with the new row data
        new_row_df = pd.DataFrame(new_row_data, index=[current_hour])

        # Append the new row DataFrame to the existing DataFrame
        df = pd.concat([df, new_row_df])

        # Fill missing values using the forward-fill method
        df.fillna(method='ffill', inplace=True)

    # Save the updated DataFrame back to the CSV file without the index
    df.reset_index(inplace=True)
    df.rename(columns={'index': 'date'}, inplace=True)
    df.to_csv(DATABASE_PATH, index=False)


@retry_on_error(max_retries=3, delay=5, allowed_exceptions=CSV_ALLOWED_EXCEPTIONS,
                fallback_values=datetime.min)
def should_update(factor: str) -> bool:
    last_update_time = datetime.strptime(read_latest_data(f'latest_{factor}_update', str), '%Y-%m-%d %H:%M:%S')
    return datetime.now() - last_update_time > update_intervals[factor]


@retry_on_error(max_retries=3, delay=5, allowed_exceptions=CSV_ALLOWED_EXCEPTIONS,
                fallback_values=None)
def save_update_time(factor_name: str):
    write_latest_data(f'latest_{factor_name}_update', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))


@retry_on_error(max_retries=3, delay=5, allowed_exceptions=CSV_ALLOWED_EXCEPTIONS,
                fallback_values=(0.0, 0.0))
def retrieve_latest_factor_values_database(factor: str) -> Tuple[float, float]:
    database = read_database()
    macro_bullish = database[f'{factor}_bullish'][-1]
    macro_bearish = database[f'{factor}_bearish'][-1]
    return macro_bullish, macro_bearish


@retry_on_error(max_retries=3, delay=5, allowed_exceptions=CSV_ALLOWED_EXCEPTIONS,
                fallback_values=pd.DataFrame())
def load_dataset() -> pd.DataFrame:
    """Load the main dataset, set index, and fill missing values."""
    main_dataset = pd.read_csv(DATASET_PATH)
    main_dataset['Date'] = pd.to_datetime(main_dataset['Date'])
    main_dataset = main_dataset.set_index('Date')
    return main_dataset


@retry_on_error(max_retries=3, delay=5, allowed_exceptions=CSV_ALLOWED_EXCEPTIONS,
                fallback_values=None)
def save_dataset(dataset: pd.DataFrame):
    dataset.to_csv(DATASET_PATH, index=True)


@retry_on_error(max_retries=3, delay=5, allowed_exceptions=CSV_ALLOWED_EXCEPTIONS,
                fallback_values=pd.DataFrame())
def read_trading_details() -> pd.DataFrame:
    """Read the CSV file into a DataFrame and set the "date" column as the index"""
    df = pd.read_csv(TRADE_DETAILS_PATH)
    return df


@retry_on_error(max_retries=3, delay=5, allowed_exceptions=CSV_ALLOWED_EXCEPTIONS,
                fallback_values=pd.DataFrame())
def read_trading_results() -> pd.DataFrame:
    """Read the CSV file into a DataFrame and set the "date" column as the index"""
    df = pd.read_csv(TRADE_RESULT_PATH)
    return df


@retry_on_error(max_retries=3, delay=5, allowed_exceptions=CSV_ALLOWED_EXCEPTIONS,
                fallback_values=None)
def save_trade_details(weighted_score, position_opening_time, position_closing_time,
                       position_type, opening_price, close_price, pnl, factor_values):

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
        'PNL': pnl,
        'macro_bullish': factor_values['macro_bullish'],
        'macro_bearish': factor_values['macro_bearish'],
        'order_book_bullish': factor_values['order_book_bullish'],
        'order_book_bearish': factor_values['order_book_bearish'],
        'prediction_bullish': factor_values['prediction_bullish'],
        'prediction_bearish': factor_values['prediction_bearish'],
        'technical_bullish': factor_values['technical_bullish'],
        'technical_bearish': factor_values['technical_bearish'],
        'richest_bullish': factor_values['richest_bullish'],
        'richest_bearish': factor_values['richest_bearish'],
        'google_bullish': factor_values['google_bullish'],
        'google_bearish': factor_values['google_bearish'],
        'reddit_bullish': factor_values['reddit_bullish'],
        'reddit_bearish': factor_values['reddit_bearish'],
        'youtube_bullish': factor_values['youtube_bullish'],
        'youtube_bearish': factor_values['youtube_bearish'],
        'news_bullish': factor_values['news_bullish'],
        'news_bearish': factor_values['news_bearish'],
        'weighted_score_up': factor_values['weighted_score_up'],
        'weighted_score_down': factor_values['weighted_score_down']
    }

    # Use a list to store new rows
    new_rows = [new_row]

    # Create a new DataFrame from the list of new rows
    df_new = pd.DataFrame(new_rows)

    # Concatenate the new DataFrame with the original DataFrame
    df = pd.concat([df, df_new], ignore_index=True)

    # Save the updated DataFrame to the CSV file
    df.to_csv(TRADE_DETAILS_PATH, index=False)


@retry_on_error(max_retries=3, delay=5, allowed_exceptions=CSV_ALLOWED_EXCEPTIONS,
                fallback_values=None)
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
