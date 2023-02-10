import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup

def get_forecast_values(events, url):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36")

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

        rows = table.find_all("tr")
        forecast_values = {}
        for event in events:
            for r in rows:
                event_cell = r.find("td", class_="calendar__cell calendar__event event")
                if event_cell and event_cell.find("span", class_="calendar__event-title").text == event:
                    interest_cell = event_cell.find_next_sibling("td", class_="calendar__cell calendar__forecast forecast")
                    forecast_value = interest_cell.string if interest_cell else None
                    forecast_values[event] = forecast_value
                    break
            if event not in forecast_values:
                print(f"Forecast value for {event} not found")
                break
        else:
            print("Next expected forecast values:", forecast_values)

    service.stop()
    return forecast_values

# Search criteria
events = ["Unemployment Claims", "Construction PMI", "Retail Sales m/m"]
url = "https://www.forexfactory.com/calendar"

forecast_values = get_forecast_values(events, url)
