# Standard library
import time
import logging

# Third-party libraries
from requests.sessions import Session
from dateutil.parser import parse
import configparser


# Initialize a session object
session = Session()

SATOSHI_TO_BITCOIN = 100000000
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load the config file
config = configparser.ConfigParser()
config.read('config.ini')
API_KEY_BLOCKCYPHER = config.get('API', 'Blockcypher')


def check_address_transactions_blockcypher(address):
    """
    Check the total Bitcoin received and sent in the last 24 hours for an address using the Blockcypher API.
    Args:
        address (str): The Bitcoin address to check.
    Returns:
        total_received (float): Total Bitcoin received in the last 24 hours.
        total_sent (float): Total Bitcoin sent in the last 24 hours.
    """

    # API requests limit is 20 requests per second and 200 per hour
    # consider if there is more than 20 more recipient in one transaction than this api do not load more than 2o

    logging.info('check_blockcypher')
    # Get the current time and time 24 hours ago
    current_time = int(time.time())
    time_24_hours_ago = current_time - 86400

    # Construct the API URL to get all transactions for the address
    api_key = API_KEY_BLOCKCYPHER
    # api_key = '8e20b70ce07248dd90e02aa19d611edf'
    api_url = f"https://api.blockcypher.com/v1/btc/main/addrs/{address}/full?token={api_key}"

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
                if input_inner["addresses"] == [address]:
                    total_sent += input_inner["output_value"]

        # Convert from Satoshi to BTC
        return (total_received / SATOSHI_TO_BITCOIN), (total_sent / SATOSHI_TO_BITCOIN)

    elif response.status_code == 429:

        logging.info(f"Rate limited for address {address}. Sleeping for a minute.")

        time.sleep(60)

        return check_address_transactions_blockcypher(address)

    else:

        logging.info(f"Failed to get transaction history for address {address}. Status code: {response.status_code}")

        return 0, 0