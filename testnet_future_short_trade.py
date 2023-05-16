from binance.client import Client
import logging
import configparser
import os

CONFIG_PATH = 'config/config.ini'
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
SYMBOL = 'BTCUSDT'


def get_margin_mode():
    client = initialized_future_client()
    positions = client.futures_position_information()

    for position in positions:
        if position['symbol'] == SYMBOL:
            return position['marginType']

    return None


def initialized_future_client():
    config = configparser.ConfigParser()
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), CONFIG_PATH)

    with open(config_path, 'r') as f:
        config_string = f.read()

    config.read_string(config_string)
    api_key = config.get('binance_future_testnet', 'api_key')
    api_secret = config.get('binance_future_testnet', 'api_secret')

    client = Client(api_key, api_secret, testnet=True)
    client.API_URL = 'https://testnet.binancefuture.com'  # Set the futures testnet URL
    return client


def short_market_on_specific_price(btc_amount: float, price: float, leverage: int, margin_mode: str):
    # Place a limit sell (short) order for a given symbol, amount, and price
    # Params: btc_amount - the quantity to sell (short)
    client = initialized_future_client()

    # Set the leverage
    client.futures_change_leverage(symbol=SYMBOL, leverage=leverage)
    logging.info(f'Leverage set to {leverage}x for {SYMBOL}')

    # Set the margin mode
    # Check if margin mode needs to be changed
    current_margin_mode = get_margin_mode()
    if current_margin_mode != margin_mode:
        client.futures_change_margin_type(symbol=SYMBOL, marginType=margin_mode.upper())
        logging.info(f'Margin mode set to {margin_mode} for {SYMBOL}')

    # Get the latest ticker price for BTC
    ticker = client.get_symbol_ticker(symbol=SYMBOL)
    latest_price = float(ticker['price'])
    logging.info(f'latest price: {latest_price}')

    # Check if the target price has been reached
    if latest_price >= price:
        # Place a limit sell (short) order for the desired amount of BTC at the target price
        client.futures_create_order(
            symbol=SYMBOL,
            side='SELL',
            type='LIMIT',
            timeInForce='GTC',
            quantity=btc_amount,
            price=price
        )

        logging.info('Short order placed successfully')
    else:
        logging.info('Target price has not been reached')


def get_open_futures_positions():
    client = initialized_future_client()
    open_positions = client.futures_position_information()
    logging.info("Open futures positions:")

    if not open_positions:
        logging.info("No open futures positions.")
    else:
        for position in open_positions:
            if float(position['positionAmt']) != 0:
                logging.info(f"Symbol: {position['symbol']} - Position Amount: {position['positionAmt']} -"
                             f" Entry Price: {position['entryPrice']} - Unrealized PnL: {position['unRealizedProfit']}")


def close_shorts_open_positions(symbol: str):
    client = initialized_future_client()
    open_positions = client.futures_position_information()

    for position in open_positions:
        if float(position['positionAmt']) != 0 and position['symbol'] == symbol:
            side = 'BUY' if float(position['positionAmt']) < 0 else 'SELL'
            order_type = 'MARKET'

            client.futures_create_order(
                symbol=symbol,
                side=side,
                type=order_type,
                quantity=abs(float(position['positionAmt'])),
            )

            logging.info(f"Closed position for symbol {symbol} with position amount {position['positionAmt']}.")


def short_market(btc_amount: float, leverage: int, margin_mode: str):
    # Place a market sell (short) order for a given symbol and amount
    # Params: btc_amount - the quantity to sell (short)
    client = initialized_future_client()

    # Set the leverage
    client.futures_change_leverage(symbol=SYMBOL, leverage=leverage)
    logging.info(f'Leverage set to {leverage}x for {SYMBOL}')

    # Set the margin mode
    # Check if margin mode needs to be changed
    current_margin_mode = get_margin_mode()
    if current_margin_mode != margin_mode:
        client.futures_change_margin_type(symbol=SYMBOL, marginType=margin_mode.upper())
        logging.info(f'Margin mode set to {margin_mode} for {SYMBOL}')

    # Get the latest ticker price for BTC
    ticker = client.get_symbol_ticker(symbol=SYMBOL)
    latest_price = float(ticker['price'])
    logging.info(f'latest price: {latest_price}')

    # Place a market sell (short) order for the desired amount of BTC
    client.futures_create_order(
        symbol=SYMBOL,
        side='SELL',
        type='MARKET',
        quantity=btc_amount,
    )

    logging.info('Short order placed successfully')


if __name__ == '__main__':
    # short_market(0.03, 28000, 10, 'isolated')  # 5x leverage and isolated margin mode
    # close_shorts_open_positions(SYMBOL)
    # get_open_futures_positions()
    # print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
    # close_shorts_open_positions(SYMBOL)
    # short_market(0.1, 3, 'isolated')
    # get_open_futures_positions()
    print('future', get_future_price(SYMBOL))
    get_future_price(SYMBOL)
    print('spot:', get_bitcoin_price())

