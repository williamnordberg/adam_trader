import pandas as pd
from datetime import datetime

# Define column names
column_names = [
    "date", "interest_rate", "cpi_m_to_m", "ppi_m_to_m",
    "bid_volume", "ask_volume",
    "predicted_price",
    "technical_potential_up_reversal_bullish", "technical_potential_down_reversal_bearish",
    "technical_potential_up_trend",
    "richest_addresses_total_received", "richest_addresses_total_sent",
    "hourly_google_search",
    "reddit_count_bitcoin_posts_24h", "reddit_activity_24h",
    "last_24_youtube",
    "positive_polarity_24_hours", "negative_polarity_24_hours",
    "positive_count_24_hours", "negative_count_24_hours",
    "weighted_score_up",
    "weighted_score_down",
    "macro_bullish", "macro_bearish",
    "order_book_bullish", "order_book_bearish",
    "prediction_bullish", "prediction_bearish",
    "technical_bullish", "technical_bearish",
    "richest_addresses_bullish", "richest_addresses_bearish",
    "google_search_bullish", "google_search_bearish",
    "reddit_bullish", "reddit_bearish",
    "youtube_bullish", "youtube_bearish",
    "news_bullish", "news_bearish"
]

# Define column data types
column_dtypes = {
    "date": "datetime64[ns]",
    "interest_rate": "float",
    "cpi_m_to_m": "float",
    "ppi_m_to_m": "float",
    "bid_volume": "float",
    "ask_volume": "float",
    "predicted_price": "int",
    "technical_potential_up_reversal_bullish": "bool",
    "technical_potential_down_reversal_bearish": "bool",
    "technical_potential_up_trend": "bool",
    "richest_addresses_total_received": "float",
    "richest_addresses_total_sent": "float",
    "hourly_google_search": "int",
    "reddit_count_bitcoin_posts_24h": "int",
    "reddit_activity_24h": "int",
    "last_24_youtube": "int",
    "positive_polarity_24_hours": "float",
    "negative_polarity_24_hours": "float",
    "positive_count_24_hours": "int",
    "negative_count_24_hours": "int",
    "weighted_score_up": "float",
    "weighted_score_down": "float",
    "macro_bullish": "float",
    "macro_bearish": "float",
    "order_book_bullish": "float",
    "order_book_bearish": "float",
    "prediction_bullish": "float",
    "prediction_bearish": "float",
    "technical_bullish": "float",
    "technical_bearish": "float",
    "richest_addresses_bullish": "float",
    "richest_addresses_bearish": "float",
    "google_search_bullish": "float",
    "google_search_bearish": "float",
    "reddit_bullish": "float",
    "reddit_bearish": "float",
    "youtube_bullish": "float",
    "youtube_bearish": "float",
    "news_bullish": "float",
    "news_bearish": "float"}


def parse_date(date_str):
    return datetime.strptime(date_str, '%Y-%m-%d %H')


def read_database() -> pd.DataFrame:
    # Read the CSV file into a DataFrame and set the "date" column as the index
    df = pd.read_csv('database.csv', converters={"date": parse_date})
    df = df.astype(column_dtypes)
    df.set_index("date", inplace=True)
    return df


def save_database(df: pd.DataFrame):
    # Save the DataFrame to a CSV file without the index
    df.to_csv('database.csv', index=False)


def append_to_database_and_save(new_row: pd.DataFrame, df: pd.DataFrame):
    df = df.append(new_row, ignore_index=True)

    # Save the updated DataFrame back to the CSV file without the index
    df.reset_index(inplace=True)
    df.to_csv('database.csv', index=False)
