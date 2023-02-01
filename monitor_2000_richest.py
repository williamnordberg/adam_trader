import requests
import time
import csv


def check_address_transactions(address):
    invalid_addresses = []

    response = requests.get(f"https://blockchain.info/rawaddr/{address}")

    if response.status_code == 200:
        data = response.json()
        transactions = data["txs"]
        for tx in transactions:
            # Get the time of the transaction in seconds
            tx_time = tx["time"]
            # Calculate the time difference in minutes
            time_diff = (time.time() - tx_time) / 60
            if time_diff <= 10000:
                # The transaction took place in the last 10 minutes
                print(f"Transaction found for address {address}. {tx['out'][0]['value'] / 100000000} BTC moved.")
                break
    elif response.status_code == 429:
        print(f"Rate limited for address {address}. Sleeping for a minute.")
        time.sleep(60)
        check_address_transactions(address)
    else:
        print(f"Failed to get transaction history for address {address}. Status code: {response.status_code}")
        invalid_addresses.append(address)


def read_addresses_from_csv(file_path):
    addresses = []
    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            addresses.append(row[0])
    return addresses


def main():
    # Read addresses from the CSV file
    addresses = read_addresses_from_csv('bitcoin_rich_list2000.csv')
    x = 0
    for address in addresses:
        check_address_transactions(address)
        x = x + 1
        print(++x)
        time.sleep(5)


if __name__ == "__main__":
    main()
