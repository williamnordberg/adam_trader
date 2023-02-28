import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup


def get_macro_expected_and_real_compare():
    events_list = ["CPI m/m", "CPI y/y", "Core CPI m/m", "Core PPI m/m", "PPI m/m","Federal Funds Rate"]
    url = "https://www.forexfactory.com/calendar"
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/87.0.4280.67 Safari/537.36")

    service = Service(executable_path=os.environ.get("CHROMEDRIVER_PATH", "C:\will\chromedriver.exe"))
    service.start()

    CPI_better_than_expected = False
    PPI_better_than_expected = False
    interest_rate_better_than_expected = False

    with webdriver.Remote(service.service_url, options=options) as browser:
        browser.get(url)
        browser.implicitly_wait(10)

        html = browser.page_source
        soup = BeautifulSoup(html, "html.parser")

        table = soup.find("table", class_="calendar__table")
        if not table:
            print("Table not found")
            service.stop()
            return CPI_better_than_expected, PPI_better_than_expected, interest_rate_better_than_expected

        events_dict = {}
        for event in events_list:
            for row in table.find_all("tr"):
                event_cell = row.find("td", class_="calendar__cell calendar__event event")
                if event_cell and event_cell.find("span", class_="calendar__event-title").text == event:
                    currency_cell = row.find("td", class_="calendar__cell calendar__currency currency")
                    if currency_cell and currency_cell.string.strip() == "USD":
                        interest_cell = event_cell.find_next_sibling("td",
                                                                     class_="calendar__cell calendar__forecast forecast")
                        forecast_value = interest_cell.string if interest_cell else None

                        actual_cell = row.find("td", class_="calendar__cell calendar__actual actual")
                        actual_value = actual_cell.text.strip() if actual_cell else None

                        if actual_value and forecast_value and float(actual_value[:-1]) <= float(forecast_value[:-1]):
                            events_dict[event] = True
                            if event == "CPI m/m" or event == "CPI y/y":
                                CPI_better_than_expected = True
                            elif event == "Core PPI m/m" or event == "PPI m/m":
                                PPI_better_than_expected = True
                            elif event == "Federal Funds Rate":
                                interest_rate_better_than_expected = True
                        else:
                            events_dict[event] = False
                    else:
                        events_dict[event] = False
                    break
            else:
                events_dict[event] = False

    service.stop()
    return CPI_better_than_expected, PPI_better_than_expected, interest_rate_better_than_expected


CPI_better_than_expected, PPI_better_than_expected, interest_rate_better_than_expected \
    = get_macro_expected_and_real_compare()
print(CPI_better_than_expected, PPI_better_than_expected, interest_rate_better_than_expected)
