def update_internal_factors():

    # Read the main dataset from disk
    main_dataset = pd.read_csv('main_dataset.csv', dtype={146: str})

    # Create a new instance of the Firefox driver
    driver = webdriver.Firefox()

    # Open the webpage
    driver.get("https://coinmetrics.io/community-network-data/")

    # Accept cookies
    accept_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "a.fusion-privacy-bar-acceptance")))
    accept_button.click()

    # Find and select Bitcoin from the dropdown menu
    selector = Select(WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#downloadSelect"))))
    selector.select_by_value("https://raw.githubusercontent.com/coinmetrics/data/master/csv/btc.csv")

    # Click the Download button
    download_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.cm-button")))
    download_button.click()

    # Wait for the download to finish and read the new data
    wait_for_download = True
    while wait_for_download:
        for file in os.listdir(os.path.join(os.path.expanduser("~"), "Downloads")):
            if file.endswith(".csv"):
                new_data = pd.read_csv(os.path.join(os.path.expanduser("~"), "Downloads", file), dtype={146: str})
                wait_for_download = False

    # Close the Firefox window
    driver.quit()

    # Find any new rows in the new data that are not in the main dataset
    new_rows = new_data.loc[~new_data['date'].isin(main_dataset['date'])]

    if len(new_rows) > 0:
        # Append the new rows to the main dataset
        main_dataset = pd.concat([main_dataset, new_rows])

        # Write the updated dataset to disk
        main_dataset.to_csv('main_dataset.csv', index=False)

        print(f"{len(new_rows)} new rows added to the main dataset.")
    else:
        print("The main dataset is already up to date.")

    return None
