import time
import logging
import os
import configparser
from requests.sessions import Session
from dateutil.parser import parse
from typing import Tuple
from requests.exceptions import RequestException, Timeout, TooManyRedirects, HTTPError

from z_handy_modules import retry_on_error
import itertools

# Initialize a session object
session = Session()

SATOSHI_TO_BITCOIN = 100000000
API_BASE_URL = "https://api.blockcypher.com/v1/btc/main/addrs/"
SLEEP_TIME = 60

# Load the config file
config = configparser.ConfigParser()
config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config/config.ini')

with open(config_path, 'r') as f:
    config_string = f.read()

config.read_string(config_string)
# API_KEY_BLOCKCYPHER = config.get('API', 'Blockcypher')


@retry_on_error(max_retries=3, delay=5,
                allowed_exceptions=(RequestException, Timeout, TooManyRedirects, HTTPError,),
                fallback_values=(0.0, 0.0))
def get_address_transactions_24h_blockcypher(address: str, api_keys_cycle=itertools.cycle([
    'Blockcypher1', 'Blockcypher2', 'Blockcypher3', 'Blockcypher4', 'Blockcypher5'])) \
        -> Tuple[float, float]:
    """
    Check the total Bitcoin received and sent in the last 24 hours for an address using the Blockcypher API.

    Args:
        address (str): The Bitcoin address to check.
        api_keys_cycle: api key

    Returns:
        total_received (float): Total Bitcoin received in the last 24 hours.
        total_sent (float): Total Bitcoin sent in the last 24 hours.
    """

    # Get the current time and time 24 hours ago
    current_time = int(time.time())
    time_24_hours_ago = current_time - 86400

    # Get the next API key from the cycle
    api_key = next(api_keys_cycle)
    api_key = config.get('API', api_key)

    api_url = f"{API_BASE_URL}{address}/full?token={api_key}"

    # Send the API request and get the response
    response = session.get(api_url)

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
            for input_inner in tx["inputs"]:
                if "addresses" in input_inner and input_inner["addresses"] == [address]:
                    total_sent += input_inner["output_value"]

        # Convert from Satoshi to BTC
        return (total_received / SATOSHI_TO_BITCOIN), (total_sent / SATOSHI_TO_BITCOIN)

    elif response.status_code == 429:
        logging.info(f"Blockcypher Rate limited for address {address}. Sleeping for a minute.")
        time.sleep(SLEEP_TIME)
        return get_address_transactions_24h_blockcypher(address)

    else:
        # logging.info(f"Failed to get transaction history for address {address}. Status code: {response.status_code}")
        return 0, 0


if __name__ == "__main__":
    received, sent = get_address_transactions_24h_blockcypher('bc1q4c8n5t00jmj8temxdgcc3t32nkg2wjwz24lywv')
    print('received', received)
    print('sent', sent)
