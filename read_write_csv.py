from typing import TypeVar, Type, Any, Dict, Tuple
import pandas as pd
import logging
from functools import wraps
from time import sleep
from datetime import datetime, timedelta

LATEST_INFO_FILE = "data/latest_info_saved.csv"
DATABASE_PATH = 'data/database.csv'
DATASET_PATH = 'data/dataset.csv'
CSV_ALLOWED_EXCEPTIONS = (pd.errors.EmptyDataError, FileNotFoundError, PermissionError, pd.errors.ParserError, IOError)
T = TypeVar('T')
fallback_values_types = {str: '', int: 0, float: 0.0, datetime: datetime.min}


def read_fed_announcement() -> str:
    latest_info_saved = pd.read_csv(LATEST_INFO_FILE)
    value = str(latest_info_saved.iloc[0]['next-fed-announcement'])
    return value


time_to_announce = datetime.strptime(read_fed_announcement(), '%Y-%m-%d %H:%M:%S')

update_intervals = {
    "dataset": timedelta(hours=24),
    "macro": timedelta(hours=1) if datetime.now() <= time_to_announce else timedelta(hours=24),
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
    return data_type(retrieved_value)


@retry_on_error(max_retries=3, delay=5, allowed_exceptions=CSV_ALLOWED_EXCEPTIONS,
                fallback_values=None)
def write_latest_data(column: str, value: Any):
    latest_info_saved = pd.read_csv(LATEST_INFO_FILE)
    latest_info_saved.at[0, column] = value
    latest_info_saved.to_csv(LATEST_INFO_FILE, index=False)


def parse_date(date_str):
    if not date_str:
        return None
    return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')


@retry_on_error(max_retries=3, delay=5, allowed_exceptions=CSV_ALLOWED_EXCEPTIONS,
                fallback_values=None)
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
    df.to_csv(DATABASE_PATH, index=False)


def should_update(factor: str) -> bool:
    last_update_time = datetime.strptime(read_latest_data(f'latest_{factor}_update', str), '%Y-%m-%d %H:%M:%S')
    return datetime.now() - last_update_time > update_intervals[factor]


def save_update_time(factor_name: str):
    write_latest_data(f'latest_{factor_name}_update', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))


def retrieve_latest_factor_values_database(factor: str) -> Tuple[float, float]:
    database = read_database()
    macro_bullish = database[f'{factor}_bullish'][-1]
    macro_bearish = database[f'{factor}_bearish'][-1]
    return macro_bullish, macro_bearish


def load_dataset() -> pd.DataFrame:
    """Load the main dataset, set index, and fill missing values."""
    main_dataset = pd.read_csv(DATASET_PATH)
    main_dataset['Date'] = pd.to_datetime(main_dataset['Date'])
    main_dataset = main_dataset.set_index('Date')
    return main_dataset


def save_dataset(dataset: pd.DataFrame):
    dataset.to_csv(DATASET_PATH, index=True)


if __name__ == '__main__':
    fed_announcement = read_latest_data('latest_weighted_score_up', str)
    print(type(fed_announcement))
    df1 = read_database()
    print(df1)
