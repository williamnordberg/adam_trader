from datetime import datetime, timedelta
import requests
import time

def check_address_transactions(address):
    # Get the current time and time 10 days ago
    current_time = int(time.time())
    time_10_days_ago = current_time - 864000

    # Construct the API URL to get all transactions for the address
    api_url = f"https://blockchain.info/rawaddr/{address}"

    # Send the API request and get the response
    response = requests.get(api_url)
    response_json = response.json()

    # Get the list of transactions for the address in the last 10 days
    transactions = [tx for tx in response_json["txs"] if tx["time"] > time_10_days_ago]

    # Initialize variables for tracking total sent and received
    total_received = 0
    total_sent = 0

    # Print the list of transactions for the address in the last 10 days
    print(f"List of transactions for address {address} in the last 10 days:")
    for tx in transactions:
        for input in tx["inputs"]:
            if "prev_out" in input and input["prev_out"]["addr"] == address:
                total_sent += input["prev_out"]["value"]
                print(f"{datetime.fromtimestamp(tx['time']).strftime('%Y-%m-%d %H:%M:%S')} - Sent {input['prev_out']['value'] / -100000000} BTC to transaction {tx['hash']}")
            else:
                for output in tx["out"]:
                    if output["addr"] == address:
                        total_received += output["value"]
                        print(f"{datetime.fromtimestamp(tx['time']).strftime('%Y-%m-%d %H:%M:%S')} - Received {output['value'] / 100000000} BTC from transaction {tx['hash']}")

    # Print the total received and sent for the address in the last 10 days
    print(f"Total Bitcoin received in the last 10 days: {total_received / 100000000} BTC")
    print(f"Total Bitcoin sent in the last 10 days: {total_sent / -100000000} BTC")


check_address_transactions('3L3bXoTzjZiisyuRMkTrkx5GiDNT4XXpGs')

