from selenium.common import TimeoutException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
import os
import pandas as pd
import logging
import time


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def update_internal_factors():
    # Read the main dataset from disk
    main_dataset = pd.read_csv('main_dataset.csv', dtype={146: str})

    # Get the latest date in the main dataset
    latest_date = main_dataset.loc[main_dataset['DiffLast'].last_valid_index(), 'Date']

    # Set up ChromeDriver options
    options = Options()
    options.add_argument('--headless')  # Run ChromeDriver in headless mode

    # Set up ChromeDriver service
    service = Service('chromedriver.exe')  # Replace with the path to your chromedriver executable

    # Create a new instance of the Chrome driver
    driver = webdriver.Chrome(service=service, options=options)

    # Open the webpage
    driver.get("https://coinmetrics.io/community-network-data/")

    # Check if the accept button for cookies is present
    try:
        accept_button = WebDriverWait(driver, 7).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a.fusion-privacy-bar-acceptance")))
        accept_button.click()
    except TimeoutException:
        pass

    # Find and select Bitcoin from the dropdown menu
    time.sleep(4)
    selector = Select(WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#downloadSelect"))))
    selector.select_by_value("https://raw.githubusercontent.com/coinmetrics/data/master/csv/btc.csv")

    # Click the Download button
    download_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.cm-button")))
    download_button.click()
    time.sleep(2)

    # Wait for the download to finish
    wait_for_download = True
    new_data = None  # Initialize new_data as None
    while wait_for_download:
        # Get a list of all files in the Downloads folder, sorted by creation time (new first)
        files = sorted(os.listdir(os.path.join(os.path.expanduser("~"), "Downloads")),
                       key=lambda x: os.path.getctime(os.path.join(os.path.expanduser("~"), "Downloads", x)),
                       reverse=True)
        for file in files:
            if file.endswith(".csv"):
                new_data = pd.read_csv(os.path.join(os.path.expanduser("~"), "Downloads", file), dtype={146: str})
                wait_for_download = False
                break

    # Close the Chrome window
    driver.quit()

    if new_data is not None:
        # Rename the 'time' column to 'Date'
        new_data = new_data.rename(columns={'time': 'Date'})
        print(new_data)
        # Filter the new data to only include rows with a date after the latest date in the main dataset
        new_data = new_data[new_data['Date'] > latest_date]
        new_data = new_data[['Date', 'DiffLast', 'DiffMean', 'CapAct1yrUSD', 'HashRate']]
        if len(new_data) > 0:

            # check if new data have a same date row with main_dataset
            if main_dataset['Date'].iloc[-1] == new_data['Date'].iloc[0]:
                # drop the last row in main datasett
                main_dataset = main_dataset.drop(main_dataset.index[-1])

            # Append the new rows to the main dataset
            main_dataset = pd.concat([main_dataset, new_data])

            # Write the updated dataset to disk
            main_dataset.to_csv('main_dataset.csv', index=False)

            logging.info(f"{len(new_data)} new rows of internal factors added.")
        else:
            logging.info("internal factors is already up to date.")
    else:
        logging.error("Failed to download internal factors.")

    return None


if __name__ == "__main__":
    update_internal_factors()
