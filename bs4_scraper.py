import requests
from bs4 import BeautifulSoup
import pandas as pd
import logging
from handy_modules import save_update_time, retry_on_error_with_fallback

LATEST_INFO_FILE = 'data/latest_info_saved.csv'
BASE_URL = "https://bitinfocharts.com/top-100-richest-bitcoin-addresses"
OUTPUT_FILE = "data/bitcoin_rich_list2000.csv"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                  " (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
}
logging.basicConfig(level=logging.INFO)


@retry_on_error_with_fallback(max_retries=3, delay=5,
                              allowed_exceptions=(requests.exceptions.RequestException,),
                              fallback_values='pass')
def scrape_bitcoin_rich_list():
    df = pd.DataFrame(columns=["address"])

    for i in range(1, 4):
        url = f"{BASE_URL}-{i}.html"
        try:
            response = requests.get(url, headers=HEADERS)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Error while fetching data: {e}")
            raise

        try:
            soup = BeautifulSoup(response.text, "html.parser")
            tables = soup.find_all("table")

            for table in tables:
                data = []
                for row in table.find_all("tr")[1:]:
                    cells = row.find_all("td")
                    address_link = cells[1].find("a")
                    if address_link:
                        data.append({
                            "address": address_link.get_text()
                        })

                df2 = pd.DataFrame(data)
                df = pd.concat([df, df2], ignore_index=True)
        except Exception as e:
            print(f"Error while parsing data: {e}")
            continue

    df.dropna(subset=["address"], inplace=True)
    df.to_csv(OUTPUT_FILE, index=False)

    # Save update time
    save_update_time('richest_addresses_scrap')


if __name__ == "__main__":
    scrape_bitcoin_rich_list()