import requests
import time
import csv
import pandas as pd
from scrapy.crawler import CrawlerProcess
from spider import BitcoinRichListSpider


def check_address_transactions(address):
    invalid_addresses = []
    transactions = []

    response = requests.get(f"https://blockchain.info/rawaddr/{address}")

    if response.status_code == 200:
        data = response.json()
        if 'txs' not in data:
            print(f"Address {address} has no transaction history")
            invalid_addresses.append(address)
            return invalid_addresses, transactions

        transactions = data["txs"]
        for tx in transactions:
            # Get the time of the transaction in seconds
            tx_time = tx["time"]
            # Calculate the time difference in minutes
            time_diff = (time.time() - tx_time) / 60
            if time_diff <= 10:
                # The transaction took place in the last 10 minutes
                print(f"Transaction found for address {address}. {tx['out'][0]['value'] / 100000000} BTC moved.")

    elif response.status_code == 429:
        print(f"Rate limited for address {address}. Sleeping for a minute.")
        time.sleep(60)
        invalid_addresses, transactions = check_address_transactions(address)
    else:
        print(f"Failed to get transaction history for address {address}. Status code: {response.status_code}")
        invalid_addresses.append(address)

    return invalid_addresses, transactions


def read_addresses_from_csv(file_path):
    addresses = []
    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            addresses.append(row[0])
    return addresses


def check_multiple_addresses(addresses):
    invalid_addresses = []
    all_transactions = []
    for address in addresses:
        print(f"Checking transaction history for address {address}")
        invalid, transactions = check_address_transactions(address)
        invalid_addresses += invalid
        all_transactions += transactions
        time.sleep(6)
    return invalid_addresses, all_transactions


def run_bitcoin_transaction_checker():
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
    })
    process.crawl(BitcoinRichListSpider)
    process.start()

    # Read addresses from the CSV file
    addresses = read_addresses_from_csv('bitcoin_rich_list2000.csv')
    invalid_addresses, transactions = check_multiple_addresses(addresses)

    # Save transactions to a DataFrame and CSV file
    df = pd.DataFrame(transactions)
    df.to_csv('recent_transactions.csv', index=False)

    if len(invalid_addresses) > 0:
        print(f"{len(invalid_addresses)} addresses had invalid transaction history: {invalid_addresses}")


run_bitcoin_transaction_checker()
