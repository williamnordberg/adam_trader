import os
from contextlib import contextmanager
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup


EVENTS_LIST = ["CPI m/m", "CPI y/y", "Core CPI m/m", "Core PPI m/m", "PPI m/m", "Federal Funds Rate"]
URL = "https://www.forexfactory.com/calendar"
CHROMEDRIVER_PATH = os.environ.get("CHROMEDRIVER_PATH", "C:\will\chromedriver.exe")
HEADLESS = True
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/87.0.4280.67 Safari/537.36"
)


@contextmanager
def get_browser():
    options = webdriver.ChromeOptions()
    if HEADLESS:
        options.add_argument("--headless")
    options.add_argument(f"user-agent={USER_AGENT}")
    with Service(executable_path=CHROMEDRIVER_PATH) as service:
        with webdriver.Chrome(service=service, options=options) as browser:
            yield browser


def get_macro_expected_and_real_compare():
    cpi_better_than_expected = False
    ppi_better_than_expected = False
    interest_rate_better_than_expected = False

    with get_browser() as browser:
        browser.get(URL)
        browser.implicitly_wait(10)

        html = browser.page_source
        soup = BeautifulSoup(html, "html.parser")

        table = soup.find("table", class_="calendar__table")
        if not table:
            print("Table not found")
            return cpi_better_than_expected, ppi_better_than_expected, interest_rate_better_than_expected

        events_dict = {}
        for event in EVENTS_LIST:
            for row in table.find_all("tr"):
                event_cell = row.find("td", class_="calendar__cell calendar__event event")
                if event_cell and event_cell.find("span", class_="calendar__event-title").text == event:
                    currency_cell = row.find("td", class_="calendar__cell calendar__currency currency")
                    if currency_cell and currency_cell.string.strip() == "USD":
                        interest_cell = event_cell.find_next_sibling("td", class_="calendar__cell calendar__forecast forecast")
                        forecast_value = interest_cell.string if interest_cell else None

                        actual_cell = row.find("td", class_="calendar__cell calendar__actual actual")
                        actual_value = actual_cell.text.strip() if actual_cell else None

                        if actual_value and forecast_value and float(actual_value[:-1]) <= float(forecast_value[:-1]):
                            events_dict[event] = True
                            if event in {"CPI m/m", "CPI y/y"}:
                                cpi_better_than_expected = True
                            elif event in {"Core PPI m/m", "PPI m/m"}:
                                ppi_better_than_expected = True
                            elif event == "Federal Funds Rate":
                                interest_rate_better_than_expected = True
                        else:
                            events_dict[event] = False
                    else:
                        events_dict[event] = False
                    break
            else:
                events_dict[event] = False

    return cpi_better_than_expected, ppi_better_than_expected, interest_rate_better_than_expected



cpi_better_than_expected, ppi_better_than_expected, interest_rate_better_than_expected = get_macro_expected_and_real_compare()
print(cpi_better_than_expected, ppi_better_than_expected, interest_rate_better_than_expected)
