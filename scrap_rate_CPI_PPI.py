from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup

# there is a line that you can change to  what you want to scrap
url = "https://www.forexfactory.com/calendar"

options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36")

service = Service(executable_path='C:\will\chromedriver.exe')
service.start()

browser = webdriver.Remote(service.service_url, options=options)
browser.get(url)
browser.implicitly_wait(10)

html = browser.page_source
soup = BeautifulSoup(html, "html.parser")

table = soup.find("table", class_="calendar__table")
rows = table.find_all("tr")
forecast_value, forecast_value1, forecast_value1 = None, None, None
for r in rows:
    event_cell = r.find("td", class_="calendar__cell calendar__event event")
    # just change here to what you want to search for
    if event_cell and event_cell.find("span", class_="calendar__event-title").text == "Unemployment Claims":
        interest_cell = event_cell.find_next_sibling("td", class_="calendar__cell calendar__forecast forecast")
        forecast_value = interest_cell.string
    if event_cell and event_cell.find("span", class_="calendar__event-title").text == "Construction PMI":
        interest_cell = event_cell.find_next_sibling("td", class_="calendar__cell calendar__forecast forecast")
        forecast_value1 = interest_cell.string
    if event_cell and event_cell.find("span", class_="calendar__event-title").text == "Retail Sales m/m":
        interest_cell = event_cell.find_next_sibling("td", class_="calendar__cell calendar__forecast forecast")
        forecast_value2 = interest_cell.string
    if forecast_value and forecast_value1 and forecast_value2:
        break

if forecast_value and forecast_value1 and forecast_value2:
    print("Next expected forecast value:", forecast_value, forecast_value1, forecast_value2)
else:
    print("Forecast value not found")

browser.quit()
service.stop()



