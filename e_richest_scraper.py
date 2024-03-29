import requests
from bs4 import BeautifulSoup
import pandas as pd
import logging

from z_handy_modules import retry_on_error
from z_read_write_csv import save_update_time
from http.client import HTTPException


BASE_URL = "https://bitinfocharts.com/top-100-richest-bitcoin-addresses"
OUTPUT_FILE = "data/bitcoin_rich_list2000.csv"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                  " (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
}


@retry_on_error(max_retries=3, delay=5,
                allowed_exceptions=(requests.exceptions.RequestException,
                                    FileNotFoundError, IOError, AttributeError,
                                    TimeoutError, ConnectionError, HTTPException, Exception),
                fallback_values='pass')
def scrape_bitcoin_rich_list():
    logging.info('$$$start scrapping list of bitcoin richest addresses$$$')
    df = pd.DataFrame(columns=["address"])

    for i in range(1, 4):
        url = f"{BASE_URL}-{i}.html"
        try:
            response = requests.get(url, headers=HEADERS)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logging.error(f"Error while fetching data: {e}")
            raise

        try:
            soup = BeautifulSoup(response.text, "html.parser")
            tables = soup.find_all("table")

            # check if there are tables
            if not tables:
                logging.warning(f"No tables found on page {i}")
                continue

            for table in tables:
                data = []
                for row in table.find_all("tr")[1:]:
                    cells = row.find_all("td")
                    address_link = cells[1].find("a")
                    if address_link:
                        address = address_link.get_text()
                        clean_address = address.replace('.', '')  # this removes all "." from the address
                        data.append({
                            "address": clean_address
                        })
                df2 = pd.DataFrame(data)
                df = pd.concat([df, df2], ignore_index=True)
        except Exception as e:
            logging.error(f"Error while parsing data: {e}")
            continue

    df.dropna(subset=["address"], inplace=True)
    df.to_csv(OUTPUT_FILE, index=False)

    # Save update time
    logging.info('$$$finish scrapping list of bitcoin richest addresses$$$')
    save_update_time('richest_addresses_scrap')


if __name__ == "__main__":
    scrape_bitcoin_rich_list()
