import pandas as pd
from datetime import datetime
from typing import Any, Dict

DATABASE_PATH = 'data/database.csv'

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
    "news_positive_polarity", "news_negative_polarity",
    "news_positive_count", "news_negative_count",
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
    "news_bullish", "news_bearish",
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
    "news_positive_polarity": "float",
    "news_negative_polarity": "float",
    "news_positive_count": "int",
    "news_negative_count": "int",
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
    "news_bearish": "float",
}


def parse_date(date_str):
    if not date_str:
        return None
    return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')


def read_database() -> pd.DataFrame:
    """Read the CSV file into a DataFrame and set the "date" column as the index"""
    df = pd.read_csv(DATABASE_PATH, converters={"date": parse_date})
    df.set_index("date", inplace=True)
    return df


def save_value_to_database(column: str, value):
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
        new_row_data: Dict[str, Any] = {col: [None] for col in column_names}

        # Set the date and the provided column's value
        new_row_data["date"] = [current_hour]
        new_row_data[column] = [value]

        # Create a new DataFrame with the new row data
        new_row_df = pd.DataFrame(new_row_data)
        new_row_df.set_index("date", inplace=True)

        # Append the new row DataFrame to the existing DataFrame
        df = pd.concat([df, new_row_df])

        # Fill missing values using the forward-fill method
        df.fillna(method='ffill', inplace=True)

    # Save the updated DataFrame back to the CSV file without the index
    df.reset_index(inplace=True)
    df.to_csv(DATABASE_PATH, index=False)


if __name__ == '__main__':
    save_value_to_database('predicted_price', 32289)
