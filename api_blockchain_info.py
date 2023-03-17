import time
import logging
from requests.sessions import Session

# Initialize a session object
session = Session()

SATOSHI_TO_BITCOIN = 100000000
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def check_address_transactions_blockchain_info(address):
    """
        Check the total Bitcoin received and sent in the last 24 hours for an address using the Blockchain.info API.
        Args:
            address (str): The Bitcoin address to check.
        Returns:
            total_received (float): Total Bitcoin received in the last 24 hours.
            total_sent (float): Total Bitcoin sent in the last 24 hours.
        """
    logging.info('check_blockchain_info')
    # Get the current time and time 24 hours ago
    current_time = int(time.time())
    time_24_hours_ago = current_time - 86400

    # Construct the API URL to get all transactions for the address
    api_url = f"https://blockchain.info/rawaddr/{address}"

    # Send the API request and get the response
    response = session.get(api_url)

    # Check the response status code
    if response.status_code == 200:
        response_json = response.json()

        # Get the list of transactions for the address in the last 24 hours
        transactions = [tx for tx in response_json["txs"] if tx["time"] > time_24_hours_ago]

        # Initialize variables for tracking total sent and received
        total_received = 0
        total_sent = 0
        processed_txids = []

        # Loop through the list of transactions and calculate total sent and received
        for tx in transactions:
            for input_inner in tx["inputs"]:
                if "prev_out" in input_inner and input_inner["prev_out"]["addr"] == address:
                    total_sent += input_inner["prev_out"]["value"]
                else:
                    for output in tx["out"]:
                        if output["addr"] == address:
                            if tx["hash"] not in processed_txids:
                                processed_txids.append(tx["hash"])
                                total_received += output["value"]

        # Convert from Satoshi to BTC
        return abs(total_received / SATOSHI_TO_BITCOIN), abs(total_sent / -SATOSHI_TO_BITCOIN)

    elif response.status_code == 429:
        logging.info(f"Rate limited for address {address}. Sleeping for a minute.")
        time.sleep(60)
        return check_address_transactions_blockchain_info(address)
    else:
        logging.info(f"Failed to get transaction history for address {address}. Status code: {response.status_code}")
        return 0, 0
