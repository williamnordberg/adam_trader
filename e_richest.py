import logging
import time
from typing import Tuple, List

from e_richest_scraper import scrape_bitcoin_rich_list
from z_read_write_csv import save_value_to_database, should_update, save_update_time, \
    read_rich_addresses
from e_api_blockchain_info import get_address_transactions_24h

SATOSHI_TO_BITCOIN = 100000000


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
        received, sent = get_address_transactions_24h(address)

        total_received += received
        total_sent += sent

        time.sleep(5)

    return int(total_received), int(total_sent)


def monitor_bitcoin_richest_addresses() -> Tuple[int, int]:
    """
    Monitor the richest Bitcoin addresses and calculate the total received and sent in the last 24 hours.
    Returns:
        total_received (float): Total Bitcoin received in the last 24 hours for the richest addresses.
        total_sent (float): Total Bitcoin sent in the last 24 hours for the richest addresses.
    """
    if should_update('richest_addresses_scrap'):
        scrape_bitcoin_rich_list()

    # Read addresses from the CSV file
    addresses = read_rich_addresses()

    if not addresses:
        logging.info('list of reach addresses not found')
        return 0, 0

    # Check the total Bitcoin received and sent in the last 24 hours for all addresses
    total_received, total_sent = check_multiple_addresses(addresses)

    save_update_time('richest_addresses')
    save_value_to_database('richest_addresses_total_received', total_received)
    save_value_to_database('richest_addresses_total_sent', total_sent)

    return total_received, total_sent


if __name__ == "__main__":
    # call function to get total send and total receive in last 24 hours
    total_received1, total_sent1 = monitor_bitcoin_richest_addresses()
