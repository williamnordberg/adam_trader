from datetime import datetime, timedelta
import requests
import time
import csv
import pandas as pd
from scrapy.crawler import CrawlerProcess
from spider import BitcoinRichListSpider


def read_addresses_from_csv(file_path):
    addresses = []
    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            addresses.append(row[0])
    return addresses


def check_address_transactions(address):
    # Get the current time and time 24 hours ago
    current_time = int(time.time())
    time_24_hours_ago = current_time - 864000

    # Construct the API URL to get all transactions for the address
    api_url = f"https://blockchain.info/rawaddr/{address}"

    # Send the API request and get the response
    response = requests.get(api_url)

    # Check the response status code
    if response.status_code == 200:
        response_json = response.json()

        # Get the list of transactions for the address in the last 24 hours
        transactions = [tx for tx in response_json["txs"] if tx["time"] > time_24_hours_ago]

        # Initialize variables for tracking total sent and received
        total_received = 0
        total_sent = 0

        # Loop through the list of transactions and calculate total sent and received
        for tx in transactions:
            for input in tx["inputs"]:
                if "prev_out" in input and input["prev_out"]["addr"] == address:
                    total_sent += input["prev_out"]["value"]
                else:
                    for output in tx["out"]:
                        if output["addr"] == address:
                            total_received += output["value"]

        # Convert from Satoshi to BTC
        return total_received / 100000000, total_sent / -100000000

    elif response.status_code == 429:
        print(f"Rate limited for address {address}. Sleeping for a minute.")
        time.sleep(60)
        return check_address_transactions(address)
    else:
        print(f"Failed to get transaction history for address {address}. Status code: {response.status_code}")
        return 0, 0


def check_multiple_addresses(addresses):
    total_received = 0
    total_sent = 0

    for address in addresses:
        print(f"Checking transaction history for address {address}")
        received, sent = check_address_transactions(address)
        total_received += received
        total_sent += sent
        print(f"Total Bitcoin received in the last 24 hours: {total_received} BTC")
        print(f"Total Bitcoin sent in the last 24 hours: {total_sent} BTC")
        time.sleep(6)

    print(f"Total Bitcoin received in the last 24 hours: {total_received / 100000000} BTC")
    print(f"Total Bitcoin sent in the last 24 hours: {total_sent / 100000000} BTC")

    return total_received, total_sent


def monitor_bitcoin_richest_addresses():
    # Update if last update is older than 4 hours
    # Read the last update time from disk
    last_update_time = pd.read_csv('last_update_time_richest_addresses.csv', header=None, names=['time'])['time'][0]
    last_update_time = datetime.strptime(last_update_time, '%Y-%m-%d %H:%M:%S')

    if datetime.now() - last_update_time > timedelta(hours=4):
        process = CrawlerProcess({'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'})
        process.crawl(BitcoinRichListSpider)
        process.start()

        # Save the update time to disk
        now = datetime.now()
        now_str = now.strftime('%Y-%m-%d %H:%M:%S')
        pd.DataFrame({'time': [now_str]}).to_csv('last_update_time_richest_addresses.csv', index=False, header=False)
        print(f'Richest addresses been updated at {now}')
    else:
        last_update_time = pd.read_csv('last_update_time_richest_addresses.csv', header=None, names=['time'])['time'][0]
        last_update_time = datetime.strptime(last_update_time, '%Y-%m-%d %H:%M:%S')
        print(f'The dataset was already updated less than 4 hours ago at {last_update_time}')

    # Read addresses from the CSV file
    addresses = read_addresses_from_csv('bitcoin_rich_list2000.csv')

    # Check the total Bitcoin received and sent in the last 24 hours for all addresses
    total_received, total_sent = check_multiple_addresses(addresses)

    # Print the total Bitcoin received and sent
    print(f"Total Bitcoin received in the last 24 hours: {total_received / 100000000} BTC")
    print(f"Total Bitcoin sent in the last 24 hours: {total_sent / 100000000} BTC")


monitor_bitcoin_richest_addresses()
