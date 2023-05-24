import pandas as pd
import matplotlib.pyplot as plt
from pycoingecko import CoinGeckoAPI

DATABASE_PATH = 'data/database.csv'
DAYS_TO_COMPARE = 7

# Load data and convert 'date' column to datetime format
df = pd.read_csv(DATABASE_PATH, parse_dates=['date'])
df.set_index('date', inplace=True)

# Extract predicted_price series
predicted_prices = df["predicted_price"]

# Initialize CoinGecko API client
cg = CoinGeckoAPI()

# Get hourly Bitcoin price data from CoinGecko for the last days
bitcoin_price_data = cg.get_coin_market_chart_by_id(id='bitcoin', vs_currency='usd', days=DAYS_TO_COMPARE, interval='hourly')

# Convert the price data to a DataFrame and process the timestamps
bitcoin_price_df = pd.DataFrame(bitcoin_price_data['prices'], columns=['datetime', 'price'])
bitcoin_price_df['datetime'] = pd.to_datetime(bitcoin_price_df['datetime'], unit='ms')

# Set the datetime as the index for easier comparison later
bitcoin_price_df.set_index('datetime', inplace=True)

# Extract real_price series
real_prices = bitcoin_price_df['price']

# Get the timestamp for 10 days ago
ten_days_ago = pd.Timestamp.now() - pd.Timedelta(days=DAYS_TO_COMPARE)

# Filter predicted_prices and real_prices to the last 10 days
predicted_prices = predicted_prices[predicted_prices.index >= ten_days_ago]
real_prices = real_prices[real_prices.index >= ten_days_ago]

# Plot the data
plt.figure(figsize=(12, 6))
plt.plot(predicted_prices, label='Predicted Price')
plt.plot(real_prices, label='Real Price')
plt.title('Bitcoin Predicted Price vs Real Price (Last 10 Days)')
plt.xlabel('Date')
plt.ylabel('Price')
plt.legend(loc='best')
plt.grid(True)
plt.show()
