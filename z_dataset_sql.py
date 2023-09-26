import sqlite3
import pandas as pd
from binance.client import Client
from datetime import datetime
import time
from bitcoinrpc.authproxy import AuthServiceProxy
import pandas_datareader.data as web
import configparser
import os
import ccxt
from time import sleep
from d_technical_indicators import relative_strength_index
import numpy as np
from statsmodels.tsa.seasonal import seasonal_decompose
import matplotlib.pyplot as plt

config = configparser.ConfigParser()
config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config/config.ini')

with open(config_path, 'r') as f:
    config_string = f.read()

config.read_string(config_string)
API_KEY_FRED = config.get('API', 'freed')

DATASET_PATH = 'data/dataset.db'
TABLE_NAME = 'dataset'
BACKUP_TABLE_NAME = 'backup_dataset'
TABLE_NAME_ALL_DATA = 'full_dataset'
rpc_user = "delta"
rpc_password = "delta1"
rpc_ip = "127.0.0.1"  # Localhost, or replace with your node's IP
rpc_url = f"http://{rpc_user}:{rpc_password}@{rpc_ip}:8332"
July_2019_block = 583237  # mined Jul 1, 2019 12:17 AM UTC
last_known_good_block_address = None
last_known_good_block = None

DATABASE_PATH = 'data/database.csv'


def load_dataset(dataset_path, table_name) -> pd.DataFrame:
    """Load the main dataset, set index, and fill missing values."""
    conn = sqlite3.connect(dataset_path)
    main_dataset = pd.read_sql(f'SELECT * FROM {table_name}', conn, parse_dates=['Date'])
    conn.close()
    return main_dataset


def list_tables(db_path):
    # Establish a connection to the SQLite database
    conn = sqlite3.connect(db_path)

    # Create a cursor object to execute SQL queries
    cursor = conn.cursor()

    # Execute SQL query to get list of tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")

    # Fetch all table names
    tables = cursor.fetchall()

    # Close the cursor and the connection
    cursor.close()
    conn.close()

    # Extract table names from the tuples and return as a list
    return [table[0] for table in tables]


def remove_table(db_path, table_name):
    # Establish a connection to the SQLite database
    conn = sqlite3.connect(db_path)

    # Create a cursor object to execute SQL queries
    cursor = conn.cursor()

    # Execute SQL query to remove a table
    cursor.execute(f"DROP TABLE IF EXISTS {table_name};")

    # Commit changes and close the cursor and the connection
    conn.commit()
    cursor.close()
    conn.close()

    print(f"Table {table_name} has been removed.")


def fetch_and_update_price_data():
    # Initialize Binance Client
    client = Client()
    symbol = "BTCUSDT"
    interval = Client.KLINE_INTERVAL_1HOUR
    limit = 500  # Maximum allowed per request

    # Initialize SQLite
    conn = sqlite3.connect(DATASET_PATH)
    cursor = conn.cursor()

    # Set the oldest point to January 1, 2016
    oldest_point = int(datetime.strptime("2016-01-01 00:00:00",
                                         '%Y-%m-%d %H:%M:%S').timestamp()) * 1000

    while True:
        # Fetch new candlesticks
        new_candlesticks = client.get_klines(
            symbol=symbol,
            interval=interval,
            limit=limit,
            startTime=oldest_point
        )

        if not new_candlesticks:
            break

        # Insert new data into SQLite database
        for candlestick in new_candlesticks:
            time_open = candlestick[0]
            open_price = candlestick[1]
            high = candlestick[2]
            low = candlestick[3]
            close = candlestick[4]

            new_timestamp = int(time_open / 1000)
            readable_date = datetime.utcfromtimestamp(new_timestamp).strftime('%Y-%m-%d %H:%M:%S')

            cursor.execute(f'''
                INSERT OR IGNORE INTO {TABLE_NAME} (Unix, Date, Open, High, Low, Close)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (new_timestamp, readable_date, open_price, high, low, close))

        conn.commit()

        # Update the oldest_point to just after the last fetched candle
        oldest_point = new_candlesticks[-1][0] + 1

        # Sleep a bit to prevent getting rate-limited
        time.sleep(1)

    conn.close()


def update_last_hour_transaction_count():
    # Read CSV into a DataFrame
    df_csv = pd.read_csv('combined_bitcoin_blocks.csv')
    df_csv['time'] = pd.to_datetime(df_csv['time'])  # Convert 'time' column to datetime objects

    # Connect to SQLite database
    conn = sqlite3.connect('data/dataset.db')
    df_sql = pd.read_sql_query(f"SELECT * from dataset", conn)
    df_sql['Date'] = pd.to_datetime(df_sql['Date'])  # Convert 'Date' column to datetime objects

    for index, row in df_sql.iterrows():
        # Find the last 6 blocks before the 'Date' in the SQLite DataFrame
        mask = (df_csv['time'] < row['Date'])
        filtered_df = df_csv[mask]
        last_6_blocks = filtered_df.tail(6)  # Get the last 6 blocks before the 'Date'

        # Calculate the sum of transactions in the last 6 blocks
        transaction_sum = int(last_6_blocks['transaction_count'].sum())  # Cast sum to int

        # Update the 'Last_hour_transaction_count' in SQLite DataFrame
        df_sql.at[index, 'Last_hour_transaction_count'] = transaction_sum
        print('transaction_sum', transaction_sum)
        # Update the SQLite database
        cursor = conn.cursor()
        timestamp_str = row['Date'].strftime('%Y-%m-%d %H:%M:%S')
        print(timestamp_str)

        cursor.execute(f"UPDATE dataset SET Last_hour_transaction_count = ? WHERE Date = ?",
                       (transaction_sum, timestamp_str))
        conn.commit()

    conn.close()


def fetch_and_save_fred_data(column_name, series_id, api_key, start='2019-07-01', end='2023-09-07'):
    # Fetch FRED data
    fred_data = web.DataReader(series_id, 'fred', start, end, api_key=api_key)
    fred_data = fred_data.resample('H').ffill()  # Resampling to hourly and forward filling

    # Connect to SQLite database
    conn = sqlite3.connect(DATASET_PATH)
    cursor = conn.cursor()

    # Check if column exists
    cursor.execute(f"PRAGMA table_info({TABLE_NAME});")
    columns = [column[1] for column in cursor.fetchall()]
    if column_name not in columns:
        cursor.execute(f"ALTER TABLE {TABLE_NAME} ADD COLUMN {column_name} REAL;")

    # Loop to update each row
    for index, row in fred_data.iterrows():
        value = row[series_id]
        start_time = pd.Timestamp(index).strftime('%Y-%m-%d 00:00:00')
        end_time = pd.Timestamp(index).strftime('%Y-%m-%d 23:59:59')
        print(row)
        cursor.execute(f"""
            UPDATE {TABLE_NAME} 
            SET {column_name} = ? 
            WHERE Date BETWEEN ? AND ?;
            """, (value, start_time, end_time))

    # Commit and close
    conn.commit()
    conn.close()


def update_columns(column_mappings):
    # Read CSV into a DataFrame
    df_csv = pd.read_csv('combined_bitcoin_blocks.csv')
    df_csv['time'] = pd.to_datetime(df_csv['time'])

    # Connect to SQLite database
    conn = sqlite3.connect('data/dataset.db')
    cursor = conn.cursor()

    # Check if columns exist in SQL table, if not create them
    cursor.execute("PRAGMA table_info(dataset)")
    columns = [column[1] for column in cursor.fetchall()]

    for sql_col_name in column_mappings.values():
        if sql_col_name not in columns:
            cursor.execute(f"ALTER TABLE dataset ADD COLUMN {sql_col_name} INTEGER")
            conn.commit()

    df_sql = pd.read_sql_query("SELECT * from dataset", conn)
    df_sql['Date'] = pd.to_datetime(df_sql['Date'])

    for index, row in df_sql.iterrows():
        mask = (df_csv['time'] < row['Date'])
        filtered_df = df_csv[mask]
        last_6_blocks = filtered_df.tail(6)

        timestamp_str = row['Date'].strftime('%Y-%m-%d %H:%M:%S')
        print(timestamp_str)
        for csv_col_name, sql_col_name in column_mappings.items():
            column_sum = int(last_6_blocks[csv_col_name].sum())
            cursor.execute(f"UPDATE dataset SET {sql_col_name} = ? WHERE Date = ?", (column_sum, timestamp_str))

        conn.commit()

    conn.close()


def remove_column_from_sqlite_table(db_path, table_name, column_name):
    # Connect to SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Fetch existing columns
    cursor.execute(f"PRAGMA table_info({table_name})")
    existing_columns = [col[1] for col in cursor.fetchall()]

    if column_name not in existing_columns:
        print(f"Column {column_name} does not exist.")
        return

    # Create a new temporary table without the unwanted column
    existing_columns.remove(column_name)
    columns_str = ', '.join(existing_columns)
    cursor.execute(f"CREATE TABLE temp_table AS SELECT {columns_str} FROM {table_name}")

    # Drop the original table
    cursor.execute(f"DROP TABLE {table_name}")

    # Rename the temporary table
    cursor.execute(f"ALTER TABLE temp_table RENAME TO {table_name}")

    # Commit changes and close the connection
    conn.commit()
    conn.close()
    print(f"Column {column_name} has been removed.")


def rename_columns_in_sqlite_table(database_path, table_name, column_mappings):
    conn = None  # Initialize conn to None

    try:
        # Connect to SQLite database
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()

        # Loop through each column mapping and rename
        for old_name, new_name in column_mappings.items():
            query = f"ALTER TABLE {table_name} RENAME COLUMN {old_name} TO {new_name};"
            cursor.execute(query)

        # Commit changes and close connection
        conn.commit()
        print("Columns renamed successfully.")
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
    finally:
        if conn:
            conn.close()


def count_unique_receive_addresses_in_block(block_hash):
    rpc_connection = AuthServiceProxy(rpc_url)
    block_data = rpc_connection.getblock(block_hash)

    unique_receiving_addresses = set()
    receiving_addresses = []

    x = 0

    for txid in block_data['tx']:
        tx_data = rpc_connection.getrawtransaction(txid, True, block_hash)  # Fetch individual transaction details
        x = x + 1
        if x == 100:
            break

        # Count unique receiving addresses
        for vout in tx_data.get('vout', []):
            address = vout.get('scriptPubKey', {}).get('address', None)
            if address:
                receiving_addresses.append(address)
                unique_receiving_addresses.add(address)

    print(f"receiving addresses: {len(receiving_addresses)}")
    print(f"Unique receiving addresses: {len(unique_receiving_addresses)}")


def calc_vol_within_range(order_list, min_price, max_price):
    volume = 0
    for price, vol in order_list:
        if min_price <= price <= max_price:
            volume += vol
    return volume


def update_rsi_in_sqlite_hourly(db_path: str, table_name: str):
    # Connect to SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Fetch data
    cursor.execute(f"SELECT Unix, Date, Open FROM {table_name}")
    rows = cursor.fetchall()
    df = pd.DataFrame(rows, columns=['Unix', 'Date', 'Open'])

    # Calculate hourly RSI
    df['Rsi_hourly'] = relative_strength_index(df['Open'], 14)

    # Backward fill NaNs
    df.fillna(method='bfill', inplace=True)

    # Add Rsi_hourly column to SQLite if not present
    try:
        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN Rsi_hourly REAL")
    except sqlite3.OperationalError as e:
        if 'duplicate column name' not in str(e):
            raise e

    # Update the SQLite database
    for index, row in df.iterrows():
        cursor.execute(
            f"UPDATE {table_name} SET Rsi_hourly = ? WHERE Date = ?",
            (row['Rsi_hourly'], row['Date']))
        conn.commit()

    # Close the connection
    conn.close()


def update_rsi_in_sqlite_4h_daily(db_path: str, table_name: str):
    # Connect to SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Fetch data
    cursor.execute(f"SELECT Unix, Date, Open FROM {table_name}")
    rows = cursor.fetchall()
    df = pd.DataFrame(rows, columns=['Unix', 'Date', 'Open'])

    # Convert 'Date' to datetime and set as index
    df['Date'] = pd.to_datetime(df['Date'])
    df.set_index('Date', inplace=True)

    # Now resampling should work as expected
    daily_rsi_np = relative_strength_index(df['Open'].resample('D').first().dropna(), 14)
    four_hour_rsi_np = relative_strength_index(df['Open'].resample('4H').first().dropna(), 14)

    # Create pandas Series and resample to hourly
    daily_rsi_series = pd.Series(daily_rsi_np, index=df['Open'].resample('D').first().
                                 dropna().index).resample('H').ffill()
    four_hour_rsi_series = pd.Series(four_hour_rsi_np, index=df['Open'].resample('4H').
                                     first().dropna().index).resample('H').ffill()

    # Assign back to DataFrame
    df['Rsi_daily'] = daily_rsi_series.reindex(df.index, method='ffill')
    df['Rsi_four_hour'] = four_hour_rsi_series.reindex(df.index, method='ffill')

    # Update SQLite schema if needed
    try:
        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN Rsi_daily REAL")
        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN Rsi_four_hour REAL")
    except sqlite3.OperationalError as e:
        if 'duplicate column name' not in str(e):
            raise e

    # Update the SQLite database
    for index, row in df.iterrows():
        print(index, row)
        cursor.execute(
            f"UPDATE {table_name} SET Rsi_daily = ?, Rsi_four_hour = ? WHERE Date = ?",
            #  #################### (row['Rsi_daily'], row['Rsi_four_hour'], row.name.strftime('%Y-%m-%d %H:%M:%S'))
        )
        conn.commit()

    # Close connection
    conn.close()


def update_sqlite_with_order_book_volumes(db_path, table_name):
    # Connect to SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Initialize Binance API
    binance = ccxt.binance()

    # Fetch rows from SQLite database
    cursor.execute(f"SELECT Date FROM {table_name} WHERE Date >= '2020-08-04 07aq:00:00'")
    dates = cursor.fetchall()

    for date_tuple in dates:
        date = date_tuple[0]

        try:
            order_book = binance.fetch_order_book('BTC/USDT', limit=10000)
        except Exception:
            print("Rate limit exceeded. Waiting for 20 seconds before retrying.")
            time.sleep(10)
            continue  # This will skip the rest of the loop and try again

        best_bid = order_book['bids'][0][0] if order_book['bids'] else 0
        best_ask = order_book['asks'][0][0] if order_book['asks'] else 0

        mid_price = (best_bid + best_ask) / 2
        one_percent = mid_price * 0.01

        bid_vol = calc_vol_within_range(order_book['bids'], mid_price - one_percent, mid_price)
        ask_vol = calc_vol_within_range(order_book['asks'], mid_price, mid_price + one_percent)

        # Update the SQLite database
        cursor.execute(
            f"UPDATE {table_name} "
            f"SET bid_vol_one_percent_distance = ?, ask_vol_one_percent_distance = ? WHERE Date = ?",
            (bid_vol, ask_vol, date))
        conn.commit()

        print(f"Updated for {date}")
        sleep(0.1)

    # Close the connection
    conn.close()


def calculate_bb_hourly(df, window_size=20):
    middle_band = df['Open'].rolling(window=window_size).mean()
    rolling_std = df['Open'].rolling(window=window_size).std()
    upper_band = middle_band + (rolling_std * 2)
    lower_band = middle_band - (rolling_std * 2)
    return lower_band, middle_band, upper_band


def calculate_bband_hourly(df):
    lower_band, middle_band, upper_band = calculate_bb_hourly(df)

    df['Bband_hourly'] = np.where(df['Open'] <= lower_band, 0,
                                  np.where(df['Open'] >= upper_band, 1,
                                           (df['Open'] - lower_band) / (upper_band - lower_band)))

    df['Bband_hourly'] = df['Bband_hourly'].fillna(0.5)  # Assuming 0.5 when NaN
    return df['Bband_hourly']


def add_column_to_sqlite_table(conn, table_name, df):
    cursor = conn.cursor()

    # Check if column exists
    cursor.execute(f"PRAGMA table_info({table_name});")
    columns = [column[1] for column in cursor.fetchall()]

    if 'Bband_hourly' not in columns:
        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN Bband_hourly REAL;")
        conn.commit()

    # Update the new column with DataFrame values
    for index, row in df.iterrows():
        cursor.execute(f"""
            UPDATE {table_name}
            SET Bband_hourly = ?
            WHERE Unix = ?;
        """, (row['Bband_hourly'], row['Unix']))

    conn.commit()


def update_bband_hourly_in_sqlite(path, table_name):
    df = load_dataset(path, table_name)
    df['Bband_hourly'] = calculate_bband_hourly(df)

    # Update the SQLite database
    conn = sqlite3.connect(path)
    add_column_to_sqlite_table(conn, table_name, df)
    conn.close()


def categorize_price_movement(row, threshold=0.2):
    percentage_change = ((row['Close'] - row['Open']) / row['Open']) * 100

    if percentage_change > threshold:
        return 'Up'
    elif percentage_change < -threshold:
        return 'Down'
    else:
        return 'Neutral'


def decomposition_():
    # Your time-series data should be in a Pandas DataFrame with a DatetimeIndex.
    # Assuming df['Price'] is your time series data:
    df = load_dataset(DATASET_PATH, TABLE_NAME)
    df.set_index(df['Date'], inplace=True)
    decomposition = seasonal_decompose(df['Open'].tail(7 * 24), model='additive', period=24)

    trend = decomposition.trend
    seasonal = decomposition.seasonal
    residual = decomposition.resid

    # Plotting
    plt.figure(figsize=(10, 8))

    plt.subplot(411)
    plt.plot(df['Open'], label='Original')
    plt.legend()

    plt.subplot(412)
    plt.plot(trend, label='Trend')
    plt.legend()

    plt.subplot(413)
    plt.plot(seasonal, label='Seasonal')
    plt.legend()

    plt.subplot(414)
    plt.plot(residual, label='Residuals')
    plt.legend()

    plt.tight_layout()
    plt.show()


def add_columns_to_table(dataset_path, table_name, column_name):
    conn = sqlite3.connect(dataset_path)
    cursor = conn.cursor()

    cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} REAL")

    conn.commit()
    conn.close()


def update_with_decomposed_features():
    # Load dataset and set Date as index
    df = load_dataset(DATASET_PATH, TABLE_NAME)
    df.set_index(df['Date'], inplace=True)

    # Create a connection to SQLite
    conn = sqlite3.connect(DATASET_PATH)
    cursor = conn.cursor()

    # Loop through each row and perform time-series decomposition based on last 7*24 hours
    for i in range(7 * 24, len(df)):
        time_window = df.iloc[i - 7 * 24: i]['Open']
        decomposition = seasonal_decompose(time_window, model='additive', period=24)

        # Drop NA values generated during decomposition
        trend = decomposition.trend.dropna().iloc[-1]
        seasonal = decomposition.seasonal.dropna().iloc[-1]
        residual = decomposition.resid.dropna().iloc[-1]

        idx = df.index[i]

        # Update the corresponding columns
        cursor.execute(f"""UPDATE {TABLE_NAME} 
                        SET Trend_open_weekly = ? 
                        WHERE Date = ?""", (trend, str(idx)))

        cursor.execute(f"""UPDATE {TABLE_NAME} 
                        SET Seasonal_open_weekly = ? 
                        WHERE Date = ?""", (seasonal, str(idx)))

        cursor.execute(f"""UPDATE {TABLE_NAME} 
                        SET Residual_open_weekly = ? 
                        WHERE Date = ?""", (residual, str(idx)))

    # Commit changes and close the connection
    conn.commit()
    conn.close()


def add_directional_movement_to_db():
    df = load_dataset(DATASET_PATH, TABLE_NAME)

    # Calculate the Price_Movement
    df['directional_movement'] = df.apply(categorize_price_movement, axis=1)

    conn = sqlite3.connect(DATASET_PATH)
    cursor = conn.cursor()

    # Update SQLite database with the new "directional_movement" values
    for index, row in df.iterrows():
        date_str = row['Date'].strftime('%Y-%m-%d %H:%M:%S')  # Convert Timestamp to string

        cursor.execute(f"""UPDATE {TABLE_NAME} SET directional_movement = ? WHERE Date = ?""",
                       (row['directional_movement'], date_str))

    conn.commit()
    conn.close()


def check_nan_values():
    df = load_dataset(DATASET_PATH, TABLE_NAME)
    nan_counts = df.isna().sum()
    print("Number of NaN values in each column:")
    print(nan_counts)


def backfill_nan_values(database_path, table_name):
    # Connect to SQLite database
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    # Find the minimum date where the values are not null
    cursor.execute(f"""SELECT MIN(Date) FROM {table_name}
                       WHERE Trend_open_weekly IS NOT NULL 
                       AND Seasonal_open_weekly IS NOT NULL 
                       AND Residual_open_weekly IS NOT NULL""")
    min_valid_date = cursor.fetchone()[0]

    # Fetch the values at the minimum valid date
    cursor.execute(f"""SELECT Trend_open_weekly, Seasonal_open_weekly, Residual_open_weekly 
                       FROM {table_name} WHERE Date = ?""", (min_valid_date,))
    trend, seasonal, residual = cursor.fetchone()

    # Backfill NaN values for the first 7 days with the values at min_valid_date
    cursor.execute(f"""UPDATE {table_name} 
                       SET Trend_open_weekly = ?, 
                           Seasonal_open_weekly = ?, 
                           Residual_open_weekly = ? 
                       WHERE Date < ?""",
                   (trend, seasonal, residual, min_valid_date))

    # Commit the changes and close the connection
    conn.commit()
    conn.close()


def create_and_merge_tables(
        dataset_path: str,
        table_name: str,
        new_table_name: str,
        csv_path: str):

    # Load SQLite dataset
    conn = sqlite3.connect(dataset_path)
    df = pd.read_sql(f'SELECT * FROM {table_name}', conn, parse_dates=['Date'])
    conn.close()

    # Filter data after July 2, 2023
    df_filtered = df[df['Date'] > '2023-07-02']

    # Create new SQLite table with filtered data
    conn = sqlite3.connect(dataset_path)
    df_filtered.to_sql(new_table_name, conn, if_exists='replace', index=False)
    conn.close()

    # Read CSV
    df_csv = pd.read_csv(csv_path, converters={"date": pd.to_datetime})

    # Rename 'date' column to 'Date' to match SQLite table
    df_csv.rename(columns={'date': 'Date'}, inplace=True)

    # Merge SQLite and CSV data
    df_merged = pd.merge(df_filtered, df_csv, on='Date', how='left')

    # Create new SQLite table with merged data
    conn = sqlite3.connect(dataset_path)
    df_merged.to_sql(new_table_name, conn, if_exists='replace', index=False)
    conn.close()


if __name__ == '__main__':
    df22 = load_dataset(DATASET_PATH, TABLE_NAME_ALL_DATA)
    print(df22['Date'].iloc[0])
    print(df22['Date'].iloc[-1])

'''
df22 = load_dataset(DATASET_PATH, TABLE_NAME_ALL_DATA)
    print(df22['Date'].iloc[0])
    print(df22['Date'].iloc[-1])
    print(df22)


    split_date = pd.Timestamp('2023-02-01')
    train = df22.loc[df22['Date'] < split_date]
    test = df22.loc[df22['Date'] >= split_date]
    print('train\n', train['Directional_movement'].value_counts())
    print('test\n', test['Directional_movement'].value_counts())
'''