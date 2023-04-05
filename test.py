import logging
import pandas as pd
from reddit import compare

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

latest_info_saved = pd.read_csv('latest_info_saved.csv')
total_received = latest_info_saved['total_received_coins_in_last_24'][0]
total_sent = latest_info_saved['total_sent_coins_in_last_24'][0]

richest_addresses_bullish, richest_addresses_bearish = compare(
    total_received, total_sent)

print(richest_addresses_bullish, richest_addresses_bearish)
