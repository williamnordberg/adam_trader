from z_read_write_csv import read_database
import pandas as pd
from typing import Any, Dict


DATABASE_PATH = 'data/database.csv'


def save_value_to_database(column: str):

    df = read_database()

    df[column] = df[column].apply(lambda x: 0 if x < 0 or x > 1 else x)

    # Save the updated DataFrame back to the CSV file without the index
    df.reset_index(inplace=True)
    df.rename(columns={'index': 'date'}, inplace=True)
    df.to_csv(DATABASE_PATH, index=False)


if __name__ == '__main__':
    save_value_to_database('prediction_bullish')
