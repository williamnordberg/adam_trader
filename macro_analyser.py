import os
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
from datetime import datetime
from typing import Tuple, Dict

from database import save_value_to_database, read_database
from macro_compare import calculate_macro_sentiment
from handy_modules import save_update_time, should_update

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
    days_to_check = 5

    for event, event_date in events_date_dict.items():
        if event_date is None:
            continue

        days_until_event = (event_date - now).days

        if 0 <= days_until_event <= days_to_check:
            time_until_event = event_date - now
            hours, remainder = divmod(time_until_event.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            time_str = f"{days_until_event} day(s), {hours} hour(s), {minutes} min(s)"
            logging.info(f"Upcoming event: {event} , {time_str} remaining")


def get_chrome_options():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
                         " Chrome/87.0.4280.67 Safari/537.36")
    return options


def get_service():
    return Service(executable_path=os.environ.get("CHROMEDRIVER_PATH", "chromedriver.exe"))


def macro_sentiment_wrapper() -> Tuple[float, float, Dict[str, datetime]]:
    # Save latest update time
    save_update_time('macro')

    events_list = ["Federal Funds Rate", "CPI m/m", "PPI m/m"]
    url = "https://www.forexfactory.com/calendar"
    options = get_chrome_options()
    service = get_service()
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
            return 0, 0, {}

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
                        forecast_value = interest_cell.find("span", class_="calendar-forecast")\
                            .text if interest_cell else None

                        actual_cell = row.find("td", class_="calendar__cell calendar__actual actual")
                        actual_value = actual_cell.text.strip().rstrip('%') if actual_cell and actual_cell\
                            .text.strip() else None

                        previous_value_cell = row.find("td", class_="calendar__cell calendar__previous previous")
                        previous_value = previous_value_cell.text.strip() if previous_value_cell else None

                        if actual_value or forecast_value:
                            value = float(actual_value if actual_value else forecast_value.rstrip('%'))
                            events_date_dict[event] = datetime.utcfromtimestamp(int(row['data-timestamp']))

                            if event == "Federal Funds Rate":
                                rate_this_month = value
                                rate_month_before = float(previous_value)
                            elif event == "CPI m/m":
                                cpi_m_to_m = value
                            elif event == "PPI m/m":
                                ppi_m_to_m = value

    service.stop()
    print(rate_this_month, rate_month_before)
    if rate_this_month or cpi_m_to_m or ppi_m_to_m:
        macro_bullish, macro_bearish = calculate_macro_sentiment(
            rate_this_month, rate_month_before, cpi_m_to_m, ppi_m_to_m)

        # Save in database
        save_value_to_database('interest_rate', rate_this_month)
        save_value_to_database('cpi_m_to_m', cpi_m_to_m)
        save_value_to_database('ppi_m_to_m', ppi_m_to_m)
        save_value_to_database('macro_bullish', macro_bullish)
        save_value_to_database('macro_bearish', macro_bearish)

        return macro_bullish, macro_bearish, events_date_dict

    else:
        return 0, 0, {}


def macro_sentiment() -> Tuple[float, float, Dict[str, datetime]]:
    if should_update('macro'):
        return macro_sentiment_wrapper()
    else:
        database = read_database()
        macro_bullish = database['macro_bullish'][-1]
        macro_bearish = database['macro_bearish'][-1]
        return macro_bullish, macro_bearish, {}


if __name__ == "__main__":
    macro_bullish_outer, macro_bearish_outer, events_date_dict_outer = macro_sentiment()
    logging.info(f"{macro_bullish_outer}, {macro_bearish_outer}, event: {events_date_dict_outer}")
    print_upcoming_events(events_date_dict_outer)
    calculate_macro_sentiment(5, 4.75, 0.1, -0.5)
