import requests
from bs4 import BeautifulSoup
import pandas as pd
from handy_modules import save_update_time

LATEST_INFO_FILE = 'data/latest_info_saved.csv'


def scrape_bitcoin_rich_list():
    base_url = "https://bitinfocharts.com/top-100-richest-bitcoin-addresses"
    df = pd.DataFrame(columns=["address"])

    for i in range(1, 4):
        url = f"{base_url}-{i}.html"
        response = requests.get(url)
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

    df.dropna(subset=["address"], inplace=True)
    df.to_csv("data/bitcoin_rich_list2000.csv", index=False)

    # Save update time
    save_update_time('richest_addresses_scrap')


if __name__ == "__main__":
    scrape_bitcoin_rich_list()
