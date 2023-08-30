from binance.client import Client
from datetime import datetime
import pandas as pd

client = Client()
# Fetch 1 hour klines (candlestick data) for the last 500 hours
candlesticks = client.futures_klines(symbol="BTCUSDT", interval=Client.KLINE_INTERVAL_1HOUR, limit=500)

# Initialize an empty list to store the rows
data = []

# Loop through the candlesticks to convert and save the data
for candlestick in candlesticks:
    time_open = candlestick[0]
    open_price = candlestick[1]
    high = candlestick[2]
    low = candlestick[3]
    close = candlestick[4]

    # Convert the timestamp to a readable date-time format
    timestamp = time_open / 1000
    readable_date = datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

    # Add the data to the list
    data.append({"date": readable_date, "Open": open_price, "High": high, "Low": low, "Close": close})

# Create a DataFrame to save the data
df = pd.DataFrame(data)

print(df)

# Save to csv
csv_path = 'data_predictor/btc_h.csv'
df.to_csv(csv_path, index=False)

