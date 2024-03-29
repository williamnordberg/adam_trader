from typing import TypeVar, Type, Any, Dict, List
import pandas as pd
import logging
from functools import wraps
from time import sleep
from datetime import datetime, timedelta, timezone
import os

LATEST_INFO_FILE = "data/latest_info_saved.csv"
DATABASE_PATH = 'data/database.csv'
DATASET_PATH = 'data/dataset.csv'
TRADE_RESULT_PATH = 'data/trades_results.csv'
TRADE_DETAILS_PATH = 'data/trades_details.csv'
BITCOIN_RICH_LIST_FILE = 'data/bitcoin_rich_list2000.csv'
EXCHANGE_ADDRESSES = 'data/exchange_addresses.csv'

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
        return datetime.strptime(str(retrieved_value), '%Y-%m-%d %H:%M:%S')  # type: ignore
    else:
        return data_type(retrieved_value)  # type: ignore


@retry_on_error(max_retries=3, delay=5, allowed_exceptions=CSV_ALLOWED_EXCEPTIONS,
                fallback_values=None)
def write_latest_data(column: str, value: Any):
    latest_info_saved = pd.read_csv(LATEST_INFO_FILE)
    latest_info_saved.at[0, column] = value
    latest_info_saved.to_csv(LATEST_INFO_FILE, index=False)


def check_macro_announcement():
    now = datetime.now(timezone.utc).replace(tzinfo=None, microsecond=0)
    keys = ['interest_rate_announcement_date', 'cpi_announcement_date', 'ppi_announcement_date']

    for key in keys:
        announcement_date = read_latest_data(key, datetime)
        if announcement_date is not None:
            diff = announcement_date - now
            if diff.total_seconds() >= 0 and diff <= timedelta(days=3):
                return True

    return False


update_intervals = {
    "dataset": timedelta(hours=24),
    "richest_addresses_scrap": timedelta(hours=12),
    "macro": timedelta(hours=1) if check_macro_announcement() else timedelta(hours=24),
    "predicted_price": timedelta(hours=1),
    "technical_analysis": timedelta(hours=1),
    "order_book": timedelta(minutes=10),
    "richest_addresses": timedelta(minutes=20),
    "google_search": timedelta(hours=1),
    "reddit": timedelta(hours=1),
    "youtube": timedelta(hours=1),
    "sentiment_of_news": timedelta(hours=1),
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
    current_hour = pd.Timestamp.now(tz='UTC').floor("H").tz_localize(None)

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
    return datetime.now(timezone.utc).replace(tzinfo=None, microsecond=0) -\
        last_update_time > update_intervals[factor]


@retry_on_error(max_retries=3, delay=5, allowed_exceptions=CSV_ALLOWED_EXCEPTIONS,
                fallback_values=None)
def save_update_time(factor_name: str):
    write_latest_data(f'latest_{factor_name}_update', datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S'))


@retry_on_error(max_retries=3, delay=5, allowed_exceptions=CSV_ALLOWED_EXCEPTIONS,
                fallback_values=(0.0, 0.0))
def retrieve_latest_factor_values_database(factor: str) -> float:
    database = read_database()
    macro_bullish = database[f'{factor}_bullish'][-1]
    return macro_bullish


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
                fallback_values=None)
def save_trade_details(position: dict, factor_values: dict):
    # Define the column order
    column_order = list(position.keys()) + list(factor_values.keys())

    # Create a new row from the dictionaries
    new_row_dict = {**position, **factor_values}
    df_new = pd.DataFrame(new_row_dict, index=[0])

    # If the CSV file exists, read it
    if os.path.exists(TRADE_DETAILS_PATH):
        df = pd.read_csv(TRADE_DETAILS_PATH)
    else:  # If not, create an empty DataFrame with the column order
        df = pd.DataFrame(columns=column_order)

    # Concatenate the new DataFrame with the original DataFrame
    df = pd.concat([df, df_new], ignore_index=True)

    # Save the updated DataFrame to the CSV file
    df.to_csv(TRADE_DETAILS_PATH, index=False)


@retry_on_error(max_retries=3, delay=5, allowed_exceptions=(
        FileNotFoundError,), fallback_values=[])
def read_rich_addresses() -> List[str]:
    """
       Read Bitcoin addresses from a CSV file and remove addresses that exist in 'data/exchange_addresses.csv'.

       Returns:
           addresses (list): A list of Bitcoin addresses.
       """
    # Read Bitcoin rich list addresses
    df1 = pd.read_csv(BITCOIN_RICH_LIST_FILE, header=None, skipinitialspace=True)
    addresses = df1[0].tolist()

    # Read exchange addresses
    df2 = pd.read_csv(EXCHANGE_ADDRESSES, header=None, skipinitialspace=True)
    exchange_addresses = df2[0].tolist()

    # Remove exchange addresses from the rich list addresses
    addresses = [addr for addr in addresses if addr not in exchange_addresses]

    return addresses


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


@retry_on_error(max_retries=3, delay=5, allowed_exceptions=CSV_ALLOWED_EXCEPTIONS,
                fallback_values=pd.DataFrame())
def read_trading_results() -> pd.DataFrame:
    """Read the CSV file into a DataFrame and set the "date" column as the index"""
    df = pd.read_csv(TRADE_RESULT_PATH)
    return df


if __name__ == "__main__":
    df3 = read_database()
    print(df3.isna().sum())
    print(df3.iloc[-1])

