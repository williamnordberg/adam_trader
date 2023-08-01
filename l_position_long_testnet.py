from binance.client import Client
import logging
import configparser
import os
from datetime import datetime
from z_handy_modules import retry_on_error


CONFIG_PATH = 'config/config.ini'
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
SYMBOL = 'BTCUSDT'


def initialized_client():
    config = configparser.ConfigParser()
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), CONFIG_PATH)

    with open(config_path, 'r') as f:
        config_string = f.read()

    config.read_string(config_string)
    api_key = config.get('binance_testnet', 'api_key')
    api_secret = config.get('binance_testnet', 'api_secret')

    # Initialize the Binance client with your API key and secret key
    client = Client(api_key, api_secret, tld='us', testnet=True)

    # Enable automatic timestamp synchronization
    client.adjust_timestamp = True

    return client


def get_trade_history(symbol: str):
    # Fetch and display the trade history for a given symbol
    # Params: symbol - trading pair symbol (e.g. 'BTCUSDT')
    client = initialized_client()
    trades = client.get_my_trades(symbol=symbol)
    logging.info(f"Trade history for {symbol}:")
    for trade in trades:
        timestamp = trade['time'] / 1000.0
        dt_object = datetime.fromtimestamp(timestamp)
        logging.info(f"Trade ID: {trade['id']} - Timestamp: {dt_object} - Side: {trade['isBuyer']} "
                     f"- Quantity: {trade['qty']} - Price: {trade['price']}")


def get_account_assets():
    # Fetch and display the asset balances in the account
    client = initialized_client()
    account_info = client.get_account()
    balances = account_info['balances']
    logging.info("Account Assets:")
    for balance in balances:
        asset = balance['asset']
        free = balance['free']
        locked = balance['locked']
        logging.info(f"Asset: {asset} - Free: {free} - Locked: {locked}")


def get_open_orders(symbol: str):
    # Fetch and display the open orders for a given symbol
    # Params: symbol - trading pair symbol (e.g. 'BTCUSDT')

    client = initialized_client()
    open_orders = client.get_open_orders(symbol=symbol)
    logging.info(f"Open orders for {symbol}:")
    if not open_orders:
        logging.info("No open orders.")
    else:
        for order in open_orders:
            logging.info(f"Order ID: {order['orderId']} - Side: {order['side']} -"
                         f" Type: {order['type']} - Quantity: {order['origQty']} -"
                         f" Price: {order['price']} - Time: {order['time']}")


def get_asset_pnl():
    # Calculate and display the PnL for each asset and the total PnL
    client = initialized_client()
    balances = client.get_account()['balances']
    total_pnl = 0

    logging.info("Asset PnL:")
    for balance in balances:
        asset = balance['asset']
        free_balance = float(balance['free'])
        locked_balance = float(balance['locked'])
        total_balance = free_balance + locked_balance

        if total_balance > 0:
            # Get the latest ticker price for the asset
            try:
                ticker = client.get_symbol_ticker(symbol=f'{asset}USDT')
                latest_price = float(ticker['price'])

                # Calculate the asset value in USD
                asset_value = total_balance * latest_price
                logging.info(f"{asset}: ${asset_value:.2f}")

                # Accumulate the asset values to calculate the total PnL
                total_pnl += asset_value
            except Exception as e:
                logging.info(f"Error fetching ticker price for {asset}: {e}")

    logging.info(f"Total PnL: ${total_pnl:.2f}")


def calculate_total_profit_loss(symbol):
    # Calculate and display the total profit, total loss, and net PnL for a given symbol
    # Params: symbol - trading pair symbol (e.g. 'BTCUSDT'
    client = initialized_client()
    trades = client.get_my_trades(symbol=symbol)
    total_profit = 0
    total_loss = 0

    for trade in trades:
        price = float(trade['price'])
        quantity = float(trade['qty'])
        is_buyer = trade['isBuyer']
        cost = price * quantity

        if is_buyer:
            total_loss += cost
        else:
            total_profit += cost

    logging.info(f"Total Profit: ${total_profit:.2f}")
    logging.info(f"Total Loss: ${total_loss:.2f}")
    net_pnl = total_profit - total_loss
    logging.info(f"Net PnL: ${net_pnl:.2f}")


def cancel_all_open_orders(symbol: str):
    """
    Cancel all open orders for a given symbol
    Params: symbol - trading pair symbol (e.g. 'BTCUSDT')
    """
    client = initialized_client()
    open_orders = client.get_open_orders(symbol=symbol)

    if not open_orders:
        logging.info(f"No open orders for {symbol}.")
    else:
        for order in open_orders:
            order_id = order['orderId']
            try:
                client.cancel_order(symbol=symbol, orderId=order_id)
                logging.info(f"Cancelled order ID: {order_id}")
            except Exception as e:
                logging.error(f"Error cancelling order ID: {order_id}, Error: {e}")


def get_all_orders(symbol: str):
    client = initialized_client()
    all_orders = client.get_all_orders(symbol=symbol)
    logging.info(f"All orders for {symbol}:")
    if not all_orders:
        logging.info("No orders.")
    else:
        for order in all_orders:
            logging.info(f"Order ID: {order['orderId']} - Side: {order['side']} -"
                         f" Type: {order['type']} - Quantity: {order['origQty']} -"
                         f" Price: {order['price']} - Time: {order['time']} - Status: {order['status']}")


@retry_on_error(3, 5, (Exception,))
def close_position_at_market(btc_amount: float):
    client = initialized_client()

    # Place a market sell order for the desired amount of BTC
    client.create_order(
        symbol='BTCUSDT',
        side='SELL',
        type='MARKET',
        quantity=btc_amount
    )

    logging.info('Sell order placed successfully at market price')


@retry_on_error(3, 5, (Exception,))
def get_open_positions():
    client = initialized_client()
    account_info = client.get_account()

    # Filter out assets with zero balance
    open_positions = [balance for balance in account_info['balances'] if float(balance['free']) > 0]

    if not open_positions:
        logging.info("No open positions.")
    else:
        for position in open_positions:
            logging.info(f"Asset: {position['asset']} - Free: {position['free']} - Locked: {position['locked']}")


def place_market_buy_order(btc_amount: float):
    # Place a market buy order for a given amount of BTC
    # Params: btc_amount - the quantity to buy
    client = initialized_client()

    # Place a market buy order for the desired amount of BTC
    client.create_order(
        symbol='BTCUSDT',
        side='BUY',
        type='MARKET',
        quantity=btc_amount
    )

    logging.info('Buy order placed successfully at market price')


@retry_on_error(3, 5, (Exception,), fallback_values='could not retrieve')
def get_btc_open_positions():
    client = initialized_client()
    account_info = client.get_account()

    # Filter out assets with zero balance and only keep BTC
    btc_position = [balance for balance in account_info['balances'] if balance['asset']
                    == 'BTC' and float(balance['free']) > 0]

    if not btc_position:
        logging.info("No open BTC position.")
    else:
        for position in btc_position:
            logging.info(f"Asset: {position['asset']} - position size: {position['free']}")


if __name__ == '__main__':
    # get_open_positions()
    # close_position_at_market(0.3)
    # get_open_positions()
    # get_trade_history(SYMBOL)
    # get_account_assets()
    # get_asset_pnl()
    # calculate_total_profit_loss(SYMBOL)
    # cancel_all_open_orders(SYMBOL)
    # place_market_buy_order(1)
    # get_open_orders(SYMBOL)
    # close_position_at_market(0.4)
    get_btc_open_positions()
    # get_trade_history(SYMBOL)
