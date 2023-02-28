import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup


def get_macro_expected_and_real_compare():
    events_list = ["CPI m/m", "CPI y/y", "Core CPI m/m", "Durable Goods Orders m/m"]
    url = "https://www.forexfactory.com/calendar"
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/87.0.4280.67 Safari/537.36")

    service = Service(executable_path=os.environ.get("CHROMEDRIVER_PATH", "C:\will\chromedriver.exe"))
    service.start()

    with webdriver.Remote(service.service_url, options=options) as browser:
        browser.get(url)
        browser.implicitly_wait(10)

        html = browser.page_source
        soup = BeautifulSoup(html, "html.parser")

        table = soup.find("table", class_="calendar__table")
        if not table:
            print("Table not found")
            service.stop()
            return

        forecast_values_in_function = {}
        actual_values_in_function = {}
        events_not_found = []
        for event in events_list:
            for row in table.find_all("tr"):
                event_cell = row.find("td", class_="calendar__cell calendar__event event")
                if event_cell and event_cell.find("span", class_="calendar__event-title").text == event:
                    currency_cell = row.find("td", class_="calendar__cell calendar__currency currency")
                    if currency_cell and currency_cell.string.strip() == "USD":
                        interest_cell = event_cell.find_next_sibling("td",
                                                                     class_="calendar__cell calendar__forecast forecast")
                        forecast_value = interest_cell.string if interest_cell else None
                        forecast_values_in_function[event] = forecast_value

                        actual_cell = row.find("td", class_="calendar__cell calendar__actual actual")
                        actual_value = actual_cell.text.strip() if actual_cell else None
                        actual_values_in_function[event] = actual_value
                    else:
                        events_not_found.append(event)
                    break
            else:
                events_not_found.append(event)

    service.stop()
    print("Forecast values:", forecast_values_in_function)
    print("Actual values:", actual_values_in_function)
    print("Events not found or not in USD currency:", events_not_found)


get_macro_expected_and_real_compare()
