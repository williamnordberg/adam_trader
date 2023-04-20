# Standard library
from datetime import datetime, timedelta
import time
import csv
import logging

# Third-party libraries
import pandas as pd
from typing import Tuple, List
from scrapy.crawler import CrawlerProcess
import configparser

# Local imports
from spider import BitcoinRichListSpider
from api_blockchain_info import get_address_transactions_24h
from api_blockcypher import get_address_transactions_24h_blockcypher
from database import save_value_to_database

SATOSHI_TO_BITCOIN = 100000000
LATEST_INFO_FILE = 'data/latest_info_saved.csv'
BITCOIN_RICH_LIST_FILE = 'data/bitcoin_rich_list2000.csv'
UPDATE_INTERVAL_HOURS = 8

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load the config file
config = configparser.ConfigParser()
config.read('config/config.ini')
USER_AGENT = 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'


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
    total_received = 0.1
    total_sent = 0.1

    for i, address in enumerate(addresses):
        logging.info(f"*******Checking address {address} and {i}*******")
        if i % 3 == 0:
            # Use the Blockcypher API
            received, sent = get_address_transactions_24h_blockcypher(address)

        elif i % 3 == 1:
            # Use the Blockchain.info API
            received, sent = get_address_transactions_24h(address)

        else:
            # Use the Blockcypher API again
            received, sent = get_address_transactions_24h_blockcypher(address)

        total_received += received
        total_sent += sent

        logging.info(f"Total received: {total_received} BTC")
        logging.info(f"Total sent: {total_sent} BTC")
        time.sleep(3)

    return total_received, total_sent


def monitor_bitcoin_richest_addresses() -> Tuple[float, float]:
    """
    Monitor the richest Bitcoin addresses and calculate the total received and sent in the last 24 hours.
    Returns:
        total_received (float): Total Bitcoin received in the last 24 hours for the richest addresses.
        total_sent (float): Total Bitcoin sent in the last 24 hours for the richest addresses.
    """
    # Update if last update is older than 4 hours
    latest_info_saved = pd.read_csv(LATEST_INFO_FILE)
    last_update_time = latest_info_saved['latest_richest_addresses_update'][0]
    last_update_time = datetime.strptime(last_update_time, '%Y-%m-%d %H:%M:%S')

    if datetime.now() - last_update_time > timedelta(hours=UPDATE_INTERVAL_HOURS):
        # Save the update time to disk
        now = datetime.now()
        now_str = now.strftime('%Y-%m-%d %H:%M:%S')
        latest_info_saved['latest_richest_addresses_update'] = now_str
        latest_info_saved.to_csv('latest_info_saved.csv', index=False)
        logging.info(f'dataset been updated {now}')

        process = CrawlerProcess({'USER_AGENT': USER_AGENT})
        process.crawl(BitcoinRichListSpider)
        process.start()

    else:
        logging.info(f'list of richest addresses is already updated less than 8 hours ago at {last_update_time}')

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
    latest_info_saved_outer['total_received_coins_in_last_24'] = total_received1
    latest_info_saved_outer['total_sent_coins_in_last_24'] = total_sent1
