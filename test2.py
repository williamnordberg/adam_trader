from datetime import datetime, timedelta
import requests
import time
import csv
import pandas as pd
from scrapy.crawler import CrawlerProcess
from spider import BitcoinRichListSpider
from dateutil.parser import parse


def read_addresses_from_csv(file_path):
    addresses = []
    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            addresses.append(row[0])
    return addresses


def check_address_transactions_blockchain_info(address):
    print('check_address_transactions_blockchain_info')
    # Get the current time and time 24 hours ago
    current_time = int(time.time())
    time_24_hours_ago = current_time - 86400

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
        return (total_received / 100000000), (total_sent / -100000000)

    elif response.status_code == 429:
        print(f"Rate limited for address {address}. Sleeping for a minute.")
        time.sleep(60)
        return check_address_transactions_blockchain_info(address)
    else:
        print(f"Failed to get transaction history for address {address}. Status code: {response.status_code}")
        return 0, 0


def check_address_transactions_blockcypher(address):
    print('check_address_transactions_blockcypher')
    # Get the current time and time 24 hours ago
    current_time = int(time.time())
    time_24_hours_ago = current_time - 86400

    # Construct the API URL to get all transactions for the address
    api_key = '8e20b70ce07248dd90e02aa19d611edf'
    api_url = f"https://api.blockcypher.com/v1/btc/main/addrs/{address}/full?token={api_key}"

    # Send the API request and get the response
    response = requests.get(api_url)

    # Check the response status code
    if response.status_code == 200:
        response_json = response.json()

        # Get the list of transactions for the address in the last 24 hours
        transactions = [tx for tx in response_json["txs"] if parse(tx["received"]).timestamp() > time_24_hours_ago]

        # Initialize variables for tracking total sent and received
        total_received = 0
        total_sent = 0

        # Loop through the list of transactions and calculate total sent and received
        for tx in transactions:
            for output in tx["outputs"]:
                if output["addresses"] == [address]:
                    total_received += output["value"]
            for input in tx["inputs"]:
                if input["addresses"] == [address]:
                    total_sent += input["output_value"]

        # Convert from Satoshi to BTC
        return (total_received / 100000000), (total_sent / 100000000)

    else:
        # Handle the case where the API request fails
        return None, None


def check_address_transactions_bitcore(address):
    print('check_address_transactions_bitcore')
    # Get the current time and time 24 hours ago
    current_time = int(time.time())
    time_24_hours_ago = current_time - 86400

    # Construct the API URL to get all transactions for the address
    api_url = f"https://api.bitcore.io/api/BTC/mainnet/address/{address}/txs"

    # Send the API request and get the response
    response = requests.get(api_url)

    # Check the response status code
    if response.status_code == 200:
        transactions = response.json()
        outgoing_txids = []
        total_send, total_receive = 0, 0
        for tx in transactions:
            if tx['spentTxid'] != '':
                # This is an outgoing transaction
                outgoing_txids.append(tx['mintTxid'])
                total_send += tx['value']
            elif tx['mintTxid'] not in outgoing_txids:
                # This is an incoming transaction
                total_receive += tx['value']

        return total_receive / 100000000, total_send / 10000000

    elif response.status_code == 429:
        print(f"Rate limited for address {address}. Sleeping for a minute.")
        time.sleep(60)
        return check_address_transactions_bitcore(address)
    else:
        print(f"Failed to get transaction history for address {address}. Status code: {response.status_code}")
        return 0, 0


def check_multiple_addresses(addresses):
    total_received = 0
    total_sent = 0

    for i, address in enumerate(addresses):
        print(f"Checking transaction history for address {address}")
        if i % 3 == 0:
            # Use the Blockchain.info API
            received, sent = check_address_transactions_blockchain_info(address)

        elif i % 3 == 1:
            # Use the Blockcypher API
            received, sent = check_address_transactions_blockcypher(address)

        else:
            # Use the Blockchair API
            received, sent = check_address_transactions_bitcore(address)

        total_received += received
        total_sent += sent

        print(f"Total Bitcoin received in the last 24 hours: {total_received} BTC")
        print(f"Total Bitcoin sent in the last 24 hours: {total_sent} BTC")
        time.sleep(5)

    return total_received, total_sent


def monitor_bitcoin_richest_addresses():
    # Update if last update is older than 4 hours
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
    return total_received, total_sent


total_received1, total_sent1 = monitor_bitcoin_richest_addresses()
print(total_received1, total_sent1)
