# Standard library
import csv
import logging

from typing import Tuple, List
from bs4_scraper import scrape_bitcoin_rich_list
import configparser

BITCOIN_RICH_LIST_FILE = 'bitcoin_rich_list2000.csv'

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load the config file
config = configparser.ConfigParser()
config.read('config/config.ini')
USER_AGENT = 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'


def read_addresses_from_csv(file_path: str) -> List[str]:

    addresses = []
    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            addresses.append(row[0])
    return addresses



def monitor_bitcoin_richest_addresses() -> Tuple[float, float]:
    scrape_bitcoin_rich_list()

    # Read addresses from the CSV file
    addresses = read_addresses_from_csv(BITCOIN_RICH_LIST_FILE)
    print(addresses)
    return 0, 0



if __name__ == "__main__":
    # call function to get total send and total receive in last 24 hours
    total_received1, total_sent1 = monitor_bitcoin_richest_addresses()
