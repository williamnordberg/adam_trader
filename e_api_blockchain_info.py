import time
import logging
import requests
from typing import Tuple, Optional
from z_handy_modules import retry_on_error
from requests.exceptions import RequestException, Timeout, HTTPError, ChunkedEncodingError
from ssl import SSLEOFError

SATOSHI_TO_BITCOIN = 100000000
API_URL = "https://blockchain.info/rawaddr/"
SLEEP_TIME = 60
MAX_RETRIES = 3


@retry_on_error(MAX_RETRIES, 5, allowed_exceptions=(
        Exception, SSLEOFError, RequestException, Timeout, HTTPError,
        ConnectionError, ChunkedEncodingError),
                fallback_values=(None, None))
def get_address_transactions_24h(address: str) -> Tuple[Optional[float], Optional[float]]:
    """
    Check the total Bitcoin received and sent in the last 24 hours for an address using the Blockchain.info API.

    Args:
        address (str): The Bitcoin address to check.

    Returns:
        total_received (float): Total Bitcoin received in the last 24 hours.
        total_sent (float): Total Bitcoin sent in the last 24 hours.
    """
    # we use  fallback_values=(999.91, 999.91) as indicator to error
    current_time = int(time.time())
    time_24_hours_ago = current_time - 86400

    # Construct the API URL to get all transactions for the address
    api_url = f"{API_URL}{address}"

    # Send the API request and get the response
    response = requests.get(api_url, timeout=30)  # 30 seconds timeout

    # Check the response status code
    if response.status_code == 200:
        response_json = response.json()
        # Get the list of transactions for the address in the last 24 hours
        transactions = [tx for tx in response_json["txs"] if tx["time"] > time_24_hours_ago]

        total_received = 0
        total_sent = 0
        processed_txids = []

        # Loop through the list of transactions and calculate total sent and received
        for tx in transactions:
            for input_inner in tx["inputs"]:
                if "prev_out" in input_inner and "addr" in input_inner["prev_out"] and \
                        input_inner["prev_out"]["addr"] == address:
                    total_sent += input_inner["prev_out"]["value"]

            for output in tx["out"]:
                if "addr" in output and output["addr"] == address:
                    if tx["hash"] not in processed_txids:
                        processed_txids.append(tx["hash"])
                        total_received += output["value"]

        # Convert from Satoshi to BTC
        return abs(total_received / SATOSHI_TO_BITCOIN), abs(total_sent / SATOSHI_TO_BITCOIN)

    elif response.status_code == 429:
        logging.info(f"blockchain.info rate limited for address {address}. Sleeping for a minute.")
        time.sleep(SLEEP_TIME)
        return get_address_transactions_24h(address)

    elif response.status_code in {504, 524}:
        # Treat these as timeout errors
        raise Timeout(f"Timeout error with status code {response.status_code}")

    else:
        logging.info(f"Failed to get transaction history for address {address}. Status code: {response.status_code}")
        raise HTTPError(f"Received error status code {response.status_code}")


if __name__ == '__main__':
    received, sent = get_address_transactions_24h('bc1q4c8n5t00jmj8temxdgcc3t32nkg2wjwz24lywv')
    print(f'received: {received}, sent: {sent}')
