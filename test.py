import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
from datetime import datetime
import logging

from macro_compare import calculate_macro_sentiment

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def print_upcoming_events(events_date_dict):
    """
       Print upcoming events within a specified time range.

       This function takes a dictionary containing events and their corresponding dates,
       and logs information about events that are happening within the specified number of days.

       :param events_date_dict: A dictionary containing events as keys and their corresponding
                                datetime objects as values.
       """
    now = datetime.utcnow()
    days_to_check = 2
    for event, event_date in events_date_dict.items():
        if event_date is None:
            continue
        days_until_event = (event_date - now).days
        if 0 <= days_until_event <= days_to_check:
            time_until_event = event_date - now
            hours, remainder = divmod(time_until_event.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            time_str = f"{days_until_event} day(s), {hours} hour(s), {minutes} min(s)"
            logging.info(f"Upcoming event: {event} x, {time_str} remaining")


def get_macro_expected_and_real_compare():

    events_list = ["Final Manufacturing PMI", "CPI m/m", "PPI m/m"]
    url = "https://www.forexfactory.com/calendar"
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/87.0.4280.67 Safari/537.36")

    service = Service(executable_path=os.environ.get("CHROMEDRIVER_PATH", "C:\will\chromedriver.exe"))
    service.start()

    events_date_dict = {}

    with webdriver.Remote(service.service_url, options=options) as browser:
        browser.get(url)
        browser.implicitly_wait(10)

        html = browser.page_source
        soup = BeautifulSoup(html, "html.parser")

        table = soup.find("table", class_="calendar__table")
        if not table:
            logging.warning("Table not found")
            service.stop()
            return 0, 0

        rate_this_month = None
        rate_month_before = None
        cpi_m_to_m = None
        ppi_m_to_m = None
        for event in events_list:
            for row in table.find_all("tr"):
                event_cell = row.find("td", class_="calendar__cell calendar__event event")
                if event_cell and event_cell.find("span", class_="calendar__event-title").text == event:
                    currency_cell = row.find("td", class_="calendar__cell calendar__currency currency")
                    if currency_cell and (currency_cell.string.strip() == "USD"):
                        events_date_dict[event] = datetime.utcfromtimestamp(int(row['data-timestamp']))
                        interest_cell = event_cell.find_next_sibling(
                            "td", class_="calendar__cell calendar__forecast forecast")
                        forecast_value = interest_cell.string if interest_cell else None

                        actual_cell = row.find("td", class_="calendar__cell calendar__actual actual")
                        actual_value = actual_cell.text.strip() if actual_cell else None

                        previous_value_cell = row.find("td", class_="calendar__cell calendar__previous previous")
                        previous_value = previous_value_cell.text.strip() if previous_value_cell else None

                        if actual_value or forecast_value:
                            value = float(actual_value if actual_value else forecast_value)
                            events_date_dict[event] = datetime.utcfromtimestamp(int(row['data-timestamp']))

                            if event == "Final Manufacturing PMI":
                                rate_this_month = value
                                rate_month_before = float(previous_value)
                            elif event == "CPI m/m":
                                cpi_m_to_m = value
                            elif event == "PPI m/m":
                                ppi_m_to_m = value

    service.stop()

    if rate_this_month or cpi_m_to_m or ppi_m_to_m:
        macro_bullish, macro_bearish = calculate_macro_sentiment(
            rate_this_month, rate_month_before, cpi_m_to_m, ppi_m_to_m)
        return macro_bullish, macro_bearish, events_date_dict

    else:
        return 0, 0


if __name__ == "__main__":
    macro_bullish_outer, macro_bearish_outer, events_date_dict_outer = get_macro_expected_and_real_compare()
    logging.info(f"{macro_bullish_outer},{macro_bearish_outer}, event: {events_date_dict_outer}")
    print_upcoming_events(events_date_dict_outer)
