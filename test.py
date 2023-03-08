import requests

# Your API key
api_key = "a91dd9fb-3f4f-441e-bcaf-6f4715f817b4"

# The address you want to get the balance for
address = "bc1q3yggt43l50mtruxahs5dyz9amyq83tjmqt4pyq"

# The API endpoint URL
url = f"https://api.zapper.fi/v1/balances?addresses%5B%5D={address}&api_key={api_key}"

# Make a GET request to the API
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    # Get the balance for the address
    balance = response.json()[0]['raw_balance']
    print(f"The balance for address {address} is {balance} BTC")
else:
    print(f"Error: {response.status_code} - {response.text}")
