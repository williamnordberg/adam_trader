# Standard library
import time
import csv
import logging

# Third-party libraries
import pandas as pd
from typing import Tuple, List
import configparser

# Local imports
from bs4_scraper import scrape_bitcoin_rich_list
from api_blockchain_info import get_address_transactions_24h
from api_blockcypher import get_address_transactions_24h_blockcypher
from handy_modules import should_update, save_value_to_database

SATOSHI_TO_BITCOIN = 100000000
LATEST_INFO_FILE = 'data/latest_info_saved.csv'
BITCOIN_RICH_LIST_FILE = 'data/bitcoin_rich_list2000.csv'
UPDATE_INTERVAL_HOURS = 8

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load the config file
config = configparser.ConfigParser()
config.read('config/config.ini')


def read_addresses_from_csv(file_path: str) -> List[str]:
    """
        Read Bitcoin addresses from a CSV file.
        Args:
            file_path (str): The path to the CSV file containing Bitcoin addresses.
        Returns:
            addresses (list): A list of Bitcoin addresses.
        """
    addresses = []
    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            addresses.append(row[0])
    return addresses


def check_multiple_addresses(addresses: List[str]) -> Tuple[float, float]:
    """
    Check the total Bitcoin received and sent in the last 24 hours for a list of addresses.
    Args:
        addresses (list): A list of Bitcoin addresses.
    Returns:
        total_received (float): Total Bitcoin received in the last 24 hours for all addresses.
        total_sent (float): Total Bitcoin sent in the last 24 hours for all addresses.
    """
    total_received = 0.0001
    total_sent = 0.0001
    logging.info('Start monitoring richest addresses')

    for i, address in enumerate(addresses):
        if i % 3 == 0:
            # Use the Blockcypher API
            received, sent = get_address_transactions_24h_blockcypher(address)

        elif i % 3 == 1:
            # Use the Blockchain.info API
            received, sent = get_address_transactions_24h_blockcypher(address)
            # received, sent = get_address_transactions_24h(address)

        else:
            # Use the Blockcypher API again
            received, sent = get_address_transactions_24h_blockcypher(address)

        total_received += received
        total_sent += sent
        time.sleep(0.2)

    logging.info(f"Total received: {total_received} BTC")
    logging.info(f"Total sent: {total_sent} BTC")
    return total_received, total_sent


def monitor_bitcoin_richest_addresses() -> Tuple[float, float]:
    """
    Monitor the richest Bitcoin addresses and calculate the total received and sent in the last 24 hours.
    Returns:
        total_received (float): Total Bitcoin received in the last 24 hours for the richest addresses.
        total_sent (float): Total Bitcoin sent in the last 24 hours for the richest addresses.
    """
    if should_update('richest_addresses_scrap'):
        scrape_bitcoin_rich_list()
    else:
        logging.info(f'list of richest addresses is already updated')

    # Read addresses from the CSV file
    addresses = read_addresses_from_csv(BITCOIN_RICH_LIST_FILE)

    # Check the total Bitcoin received and sent in the last 24 hours for all addresses
    total_received, total_sent = check_multiple_addresses(addresses)

    # Save to database
    save_value_to_database('richest_addresses_total_received', total_received)
    save_value_to_database('richest_addresses_total_sent', total_sent)

    return total_received, total_sent


if __name__ == "__main__":
    # call function to get total send and total receive in last 24 hours
    total_received1, total_sent1 = monitor_bitcoin_richest_addresses()

    latest_info_saved_outer = pd.read_csv(LATEST_INFO_FILE)
    latest_info_saved_outer.loc[0, 'total_received_coins_in_last_24'] = int(total_received1)
    latest_info_saved_outer.loc[0, 'total_sent_coins_in_last_24'] = int(total_sent1)
    latest_info_saved_outer.to_csv(LATEST_INFO_FILE, index=False)
