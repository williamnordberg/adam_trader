import requests

def get_current_block_height():
    try:
        api_url = 'https://api.blockchair.com/bitcoin/stats'
        response = requests.get(api_url)

        if response.status_code == 200:
            data = response.json()
            block_height_hex = data['data']['blocks']
            return block_height_hex
        else:
            print(f"Error: {response.status_code} - {response.reason}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

print(get_current_block_height())