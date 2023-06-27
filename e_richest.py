import logging
import time
import csv

from typing import Tuple, List
import configparser

from e_bs4_scraper import scrape_bitcoin_rich_list
from e_api_blockcypher import get_address_transactions_24h_blockcypher
from handy_modules import retry_on_error
from read_write_csv import save_value_to_database, should_update, save_update_time

SATOSHI_TO_BITCOIN = 100000000
BITCOIN_RICH_LIST_FILE = 'data/bitcoin_rich_list2000.csv'
config = configparser.ConfigParser()
config.read('config/config.ini')


@retry_on_error(max_retries=3, delay=5, allowed_exceptions=(
        FileNotFoundError,), fallback_values=[])
def read_addresses_from_csv() -> List[str]:
    """
        Read Bitcoin addresses from a CSV file.

        Returns:
            addresses (list): A list of Bitcoin addresses.
        """
    addresses = []
    with open(BITCOIN_RICH_LIST_FILE, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            addresses.append(row[0])
    return addresses


def check_multiple_addresses(addresses: List[str]) -> Tuple[int, int]:
    """
    Check the total Bitcoin received and sent in the last 24 hours for a list of addresses.
    Args:
        addresses (list): A list of Bitcoin addresses.
    Returns:
        total_received (int): Total Bitcoin received in the last 24 hours for all addresses.
        total_sent (int): Total Bitcoin sent in the last 24 hours for all addresses.
    """
    total_received = 0
    total_sent = 0

    for i, address in enumerate(addresses):
        received, sent = get_address_transactions_24h_blockcypher(address)
        total_received += received
        total_sent += sent
        time.sleep(0.5)

    return int(total_received), int(total_sent)


def monitor_bitcoin_richest_addresses() -> Tuple[float, float]:
    """
    Monitor the richest Bitcoin addresses and calculate the total received and sent in the last 24 hours.
    Returns:
        total_received (float): Total Bitcoin received in the last 24 hours for the richest addresses.
        total_sent (float): Total Bitcoin sent in the last 24 hours for the richest addresses.
    """
    if should_update('richest_addresses_scrap'):
        scrape_bitcoin_rich_list()

    if should_update('richest_addresses'):

        # Read addresses from the CSV file
        addresses = read_addresses_from_csv()

        if not addresses:
            logging.info('list of reach addresses not found')
            return 0.0, 0.0

        # Check the total Bitcoin received and sent in the last 24 hours for all addresses
        total_received, total_sent = check_multiple_addresses(addresses)

        save_update_time('richest_addresses')

        # Save to database
        save_value_to_database('richest_addresses_total_received', total_received)
        save_value_to_database('richest_addresses_total_sent', total_sent)

        return total_received, total_sent
    else:
        return 0.0, 0.0


if __name__ == "__main__":
    # call function to get total send and total receive in last 24 hours
    total_received1, total_sent1 = monitor_bitcoin_richest_addresses()
