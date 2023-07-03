import random
import pandas as pd
from selenium import webdriver
import time
import nltk
from concurrent.futures import ProcessPoolExecutor

nltk.download('words')
DATABASE_PATH = "discount_code.csv"
DISCOUNT_PRICE = 24000


def save_word(discount_word: str):

    latest_info_saved = pd.read_csv(DATABASE_PATH)
    latest_info_saved.loc[0, f'word'] = discount_word
    latest_info_saved.to_csv(DATABASE_PATH, index=False)


def generate_random_word(length):
    english_words = [word.upper() for word in nltk.corpus.words.words() if len(word) == length]
    return random.choice(english_words)


def find_discount_code():
    driver = webdriver.Chrome()

    try:
        driver.get("https://www.townscript.com/v2/e/diskoafrikamorabitojuly8th/booking/tickets")
        add_button_xpath = "/html/body/app-root/app-ticket-page/div/div/div[1]/ts-panel/div/div/div/app-ticket-details/div/div/div[2]/app-add-ticket/div/div/span"
        apply_discount_code_xpath = "/html/body/app-root/app-ticket-page/div/div/div[2]/app-discount-container/div/ts-panel/ts-panel-header/div"
        code_input_selector = "//input[@id='codeInput']"
        apply_button_selector = "#codeInputForm > div > button"
        total_amount_xpath = "/html/body/app-root/app-ticket-page/div/div/div[2]/app-ticket-summary/div/div/div[2]/div[1]/app-price/span/span"

        add_button = driver.find_element("xpath", add_button_xpath)
        add_button.click()
        time.sleep(2)

        apply_discount_code = driver.find_element("xpath", apply_discount_code_xpath)
        time.sleep(2)
        apply_discount_code.click()
        time.sleep(2)

        while True:
            random_word = generate_random_word(10)
            code_input = driver.find_element("xpath", code_input_selector)
            code_input.clear()
            code_input.send_keys(random_word)

            apply_button = None
            while apply_button is None:
                apply_button = driver.execute_script("return document.querySelector('#codeInputForm > div > button')")
                if apply_button is None:
                    time.sleep(1)  # Wait for 1 second before trying again

            apply_button.click()

            total_amount_element = driver.find_element("xpath", total_amount_xpath)
            total_amount = int(total_amount_element.text)

            if total_amount < DISCOUNT_PRICE:
                print(f"Discount code: {random_word}, Total amount: {total_amount}")
                save_word(random_word)
                break

    finally:
        driver.quit()


if __name__ == '__main__':
    num_processes = 3

    with ProcessPoolExecutor(max_workers=num_processes) as executor:
        for _ in range(num_processes):
            executor.submit(find_discount_code)
            time.sleep(60)
