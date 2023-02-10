import time
import requests

# Define the Google Trends API URL
url = 'https://trends.google.com/trends/api/widgetdata/comparedgeo/csv?hl=en-US&tz=-120&req=%7B%22geo%22:%7B%22country%22:%22US%22%7D,%22comparisonItem%22:%5B%7B%22geo%22:%7B%22country%22:%22US%22%7D,%22complexKeywordsRestriction%22:%7B%22keyword%22:%5B%7B%22type%22:%22BROAD%22,%22value%22:%22bitcoin%22%7D%5D%7D%7D%5D,%22resolution%22:%22WEEK%22,%22locale%22:%22en-US%22,%22requestOptions%22:%7B%22property%22:%22%22,%22backend%22:%22IZG%22,%22category%22:0%7D%7D&token=APP6_UEAAAAAXR2XQlKLZLXGfcBHU_6A8KiW_hfKdPcc&tz=-120'

# Define the function to get search volume
def get_search_volume():
    # Make a request to the Google Trends API
    response = requests.get(url)
    data = response.text.splitlines()
    print(data)
    # Extract the search volume from the API response
    search_volume = data[-2].split(',')[1]
    return int(search_volume)

# Define the function to check if search volume is unusual
def is_unusual_volume(volume, threshold=100):
    # You can adjust the threshold based on your needs
    return volume > threshold

# Main loop to monitor search volume
while True:
    search_volume = get_search_volume()
    if is_unusual_volume(search_volume):
        print(f'Warning: Unusual search volume for bitcoin ({search_volume})')
    time.sleep(60) # Wait for one minute before checking again
