import fredapi

# Initialize the API
fred = fredapi.Fred(api_key='8f7cbcbc1210c7efa87ee9484e159c21')

# Get the latest value for the federal funds rate
fed_funds_rate = fred.get_series("FEDFUNDS")

# Get the latest value (i.e., the most recent observation)
latest_value = fed_funds_rate.iloc[-1]

# Print the result
print("The current federal funds rate is {:.2f}%".format(latest_value))


