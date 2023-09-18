import sqlite3
import pandas as pd
from datetime import datetime
import time
from bitcoinrpc.authproxy import AuthServiceProxy
import configparser
import os


config = configparser.ConfigParser()
config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config/config.ini')

with open(config_path, 'r') as f:
    config_string = f.read()

config.read_string(config_string)
API_KEY_FRED = config.get('API', 'freed')

DATASET_PATH = 'data/dataset.db'
TABLE_NAME = 'dataset'
rpc_user = "delta"
rpc_password = "delta1"
rpc_ip = "127.0.0.1"  # Localhost, or replace with your node's IP
rpc_url = f"http://{rpc_user}:{rpc_password}@{rpc_ip}:8332"
July_2019_block = 583237  # mined Jul 1, 2019 12:17 AM UTC
last_known_good_block_address = None
last_known_good_block = None


def load_dataset(dataset_path, table_name) -> pd.DataFrame:
    """Load the main dataset, set index, and fill missing values."""
    conn = sqlite3.connect(dataset_path)
    main_dataset = pd.read_sql(f'SELECT * FROM {table_name}', conn, parse_dates=['Date'])
    conn.close()
    return main_dataset


def get_block_info(rpc_connection, current_block):
    block_hash = rpc_connection.getblockhash(current_block)
    return rpc_connection.getblock(block_hash)


def update_addresses_from_block(rpc_connection, block_info, receiving_addresses, unique_receiving_addresses):
    for txid in block_info['tx']:
        tx_data = rpc_connection.getrawtransaction(txid, True, block_info['hash'])
        for vout in tx_data.get('vout', []):
            address = vout.get('scriptPubKey', {}).get('address', None)
            if address:
                print('address')
                receiving_addresses.append(address)
                unique_receiving_addresses.add(address)


def update_sqlite(new_timestamp, unique_count, all_count):
    conn = sqlite3.connect(DATASET_PATH)
    cursor = conn.cursor()
    cursor.execute(f'''
        UPDATE {TABLE_NAME} 
        Last_hour_uniq_output_address_count = ?, 
        Last_hour_output_address_count = ? 
        WHERE Unix = ?
    ''', (unique_count, all_count, new_timestamp))
    conn.commit()
    conn.close()


def count_last_hour_output_addresses(new_timestamp):
    global last_known_good_block_address

    earliest_timestamp = int(time.mktime(datetime.strptime(
        '2017-09-01 00:00:00', '%Y-%m-%d %H:%M:%S').timetuple()))

    rpc_connection = AuthServiceProxy(rpc_url)

    # Initialize values
    current_block = rpc_connection.getblockcount()

    # Find the first block that has a smaller time stamp than unix_time
    while True:
        block_hash = rpc_connection.getblockhash(current_block)
        block_info = rpc_connection.getblock(block_hash)
        if block_info['time'] <= new_timestamp:
            break
        current_block -= 1

    last_known_good_block_address = current_block

    unique_receiving_addresses = set()
    receiving_addresses = []
    blocks_considered = 0

    while blocks_considered < 6:
        block_info = get_block_info(rpc_connection, current_block)
        print(current_block, current_block)

        if new_timestamp > block_info['time'] > earliest_timestamp:
            blocks_considered += 1
            last_known_good_block_address = current_block

            update_addresses_from_block(rpc_connection, block_info, receiving_addresses, unique_receiving_addresses)

        current_block -= 1
        if block_info['time'] <= earliest_timestamp:
            break

    update_sqlite(new_timestamp, len(unique_receiving_addresses), len(receiving_addresses))


def update_rows():
    df1 = load_dataset(DATASET_PATH, TABLE_NAME)

    for index, row in df1.iloc[::-1].iterrows():
        print(f'Updating unix: {row["Unix"]}, {row["Date"]}')
        unix_time = row['Unix']
        count_last_hour_output_addresses(unix_time)
