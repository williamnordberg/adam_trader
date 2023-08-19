import os
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from datetime import datetime
from typing import Tuple, Optional, Dict
from datetime import timedelta
import platform

from z_compares import compare_macro_m_to_m
from z_read_write_csv import read_latest_data, write_latest_data, save_value_to_database, \
    should_update, save_update_time, retrieve_latest_factor_values_database
from z_handy_modules import retry_on_error


def format_time(time_until: timedelta) -> str:
    days = time_until.days
    hours, remainder = divmod(time_until.seconds, 3600)
    minutes, _ = divmod(remainder, 60)

    if days > 1:
        return f"{days}d, {hours}h"
    elif days == 1:
        return f"{days}d, {hours}h"
    elif hours > 0:
        return f"{hours}h, {minutes}m"
    else:
        return f"{minutes}m"


def calculate_upcoming_events() -> Tuple[str, str, str]:
    fed = datetime.strptime(read_latest_data('interest_rate_announcement_date', str), "%Y-%m-%d %H:%M:%S")
    cpi = datetime.strptime(read_latest_data('cpi_announcement_date', str), "%Y-%m-%d %H:%M:%S")
    ppi = datetime.strptime(read_latest_data('ppi_announcement_date', str), "%Y-%m-%d %H:%M:%S")

    now = datetime.utcnow()

    time_until_fed = fed - now
    time_until_cpi = cpi - now
    time_until_ppi = ppi - now

    fed_announcement = ''
    cpi_fed_announcement = ''
    ppi_fed_announcement = ''

    if time_until_fed.days >= 0:
        fed_announcement = f"Nxt FED:{format_time(time_until_fed)}"

    if time_until_cpi.days >= 0:
        cpi_fed_announcement = f"Nxt CPI:{format_time(time_until_cpi)}"

    if time_until_ppi.days >= 0:
        ppi_fed_announcement = f"Nxt PPI:{format_time(time_until_ppi)}"

    return fed_announcement if time_until_fed.days <= 2 else '', \
        cpi_fed_announcement if time_until_cpi.days <= 2 else '', \
        ppi_fed_announcement if time_until_ppi.days <= 2 else ''


def handle_macro_data(metric_value: Optional[float], metric_name: str) -> Tuple[float, float]:
    if metric_value is None:
        bullish_value = read_latest_data(f'{metric_name}_bullish', float)
        bearish_value = read_latest_data(f'{metric_name}_bearish', float)
    else:
        bullish_value, bearish_value = compare_macro_m_to_m(metric_value)
        write_latest_data(f'{metric_name}_bullish', bullish_value)
        write_latest_data(f'{metric_name}_bearish', bearish_value)
        write_latest_data(f'{metric_name}_m_to_m', bullish_value)
    return bullish_value, bearish_value


def calculate_macro_sentiment(rate_this_month: Optional[float], rate_month_before: Optional[float],
                              cpi_m_to_m: Optional[float], ppi_m_to_m: Optional[float]) -> float:

    weights: Dict[str, float] = {"interest_rate": 0.5, "cpi": 0.25, "ppi": 0.25}

    rate_m_to_m = rate_this_month - rate_month_before if rate_this_month and rate_month_before else None
    rate_bullish, rate_bearish = handle_macro_data(rate_m_to_m, 'rate')
    cpi_bullish, cpi_bearish = handle_macro_data(cpi_m_to_m, 'cpi')
    ppi_bullish, ppi_bearish = handle_macro_data(ppi_m_to_m, 'ppi')

    # Calculate the weighted score for each alternative:
    weighted_score_up = (
            weights["interest_rate"] * rate_bullish +
            weights["cpi"] * cpi_bullish +
            weights["ppi"] * ppi_bullish
    )

    weighted_score_down = (
            weights["interest_rate"] * rate_bearish +
            weights["cpi"] * cpi_bearish +
            weights["ppi"] * ppi_bearish
    )

    total_score = weighted_score_up + weighted_score_down

    # Normalize the scores
    if total_score == 0:
        normalized_score_up, normalized_score_down = 0.0, 0.0
    else:
        normalized_score_up = weighted_score_up / total_score
    return round(normalized_score_up, 2)


def print_upcoming_events(events_date_dict: dict):
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


def get_chrome_options() -> Options:
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
                         " Chrome/87.0.4280.67 Safari/537.36")
    return options


def get_service() -> Service:
    os_name = platform.system()
    if os_name == "Windows":
        return Service(executable_path=os.environ.get("CHROMEDRIVER_PATH", "chromedriver.exe"))
    elif os_name == "Linux":
        return Service(executable_path=os.environ.get("CHROMEDRIVER_PATH", "chromedriver"))
    else:
        raise ValueError(f"Unsupported operating system: {os_name}")


@retry_on_error(max_retries=3, delay=5, allowed_exceptions=(
        Exception, TimeoutException), fallback_values=(None, {}))
def macro_sentiment_wrapper() -> Tuple[float, Dict[str, datetime]]:

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
            return 0.5, {}

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
                        if event == 'Federal Funds Rate':
                            write_latest_data('interest_rate_announcement_date', events_date_dict[event])
                        elif event == 'CPI m/m':
                            write_latest_data('cpi_announcement_date', events_date_dict[event])

                        elif event == 'PPI m/m':
                            write_latest_data('ppi_announcement_date', events_date_dict[event])

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
                                rate_month_before = float(previous_value.rstrip('%'))
                            elif event == "CPI m/m":
                                cpi_m_to_m = value
                            elif event == "PPI m/m":
                                ppi_m_to_m = value

    service.stop()

    if rate_this_month or cpi_m_to_m or ppi_m_to_m:
        macro_bullish = calculate_macro_sentiment(
            rate_this_month, rate_month_before, cpi_m_to_m, ppi_m_to_m)

        # Save in database
        if rate_this_month and rate_month_before:
            save_value_to_database('fed_rate_m_to_m', (rate_this_month-rate_month_before))
            save_value_to_database('interest_rate', rate_this_month)

        if cpi_m_to_m:
            save_value_to_database('cpi_m_to_m', cpi_m_to_m)
        if ppi_m_to_m:
            save_value_to_database('ppi_m_to_m', ppi_m_to_m)

        # Save the next event date
        if rate_this_month:
            write_latest_data('next-fed-announcement', events_date_dict['Federal Funds Rate'])

        return macro_bullish, events_date_dict

    else:
        macro_bullish = retrieve_latest_factor_values_database('macro')
        return macro_bullish, {}


def macro_sentiment() -> Tuple[float, Dict[str, datetime]]:
    if should_update('macro'):
        macro_bullish, events_date_dict = macro_sentiment_wrapper()

        # Check if function is not fail and nor return fallback value
        if macro_bullish is not None:
            save_value_to_database('macro_bullish', round(macro_bullish, 2))
            save_update_time('macro')
            return macro_bullish, events_date_dict
    else:
        macro_bullish = retrieve_latest_factor_values_database('macro')
        return macro_bullish, {}


if __name__ == "__main__":
    macro_bullish_outer, events_date_dict_outer = macro_sentiment_wrapper()
    print(macro_bullish_outer, events_date_dict_outer)
