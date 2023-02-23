from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
import pandas as pd
import os

# Create a new instance of the Firefox driver
driver = webdriver.Firefox()

# Open the webpage
driver.get("https://coinmetrics.io/community-network-data/")

# Accept cookies
accept_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.fusion-privacy-bar-acceptance")))
accept_button.click()

# Find and select Bitcoin from the dropdown menu
selector = Select(WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#downloadSelect"))))
selector.select_by_value("https://raw.githubusercontent.com/coinmetrics/data/master/csv/btc.csv")

# Click the Download button
download_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.cm-button")))
download_button.click()

# Wait for the download to finish and print the CSV data
wait_for_download = True
while wait_for_download:
    for file in os.listdir(os.path.join(os.path.expanduser("~"), "Downloads")):
        if file.endswith(".csv"):
            data = pd.read_csv(os.path.join(os.path.expanduser("~"), "Downloads", file), dtype={146: str})
            print(data)
            wait_for_download = False

# Close the Firefox window
driver.quit()
