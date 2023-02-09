import fredapi
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup


url = "https://www.forexfactory.com/calendar?week=jan29.2023#closed"

# Initialize a headless browser and set the user agent
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36")

# Create the Chrome service
service = Service(executable_path='C:\will\chromedriver.exe')

# Start the Chrome service
service.start()

# Connect to the service and initialize a browser
browser = webdriver.Remote(service.service_url, options=options)

# Load the webpage
browser.get(url)

# Wait for the page to load
browser.implicitly_wait(10)

# Extract the page source
html = browser.page_source

# Create BeautifulSoup object from the source
soup = BeautifulSoup(html, "html.parser")
#print(soup)

table = soup.find("table", class_="calendar__table")
rows = table.find_all("tr")
interest_rate = None
for r in rows:
    interest_cell = r.find("td", class_="calendar__cell calendar__forecast forecast", string="4.75%")
    if interest_cell:
        interest_rate = interest_cell.string
        break

if interest_rate:
    print("Next expected interest rate hike:", interest_rate)
else:
    print("Interest rate information not found")

# Close the browser
browser.quit()

# Stop the Chrome service
service.stop()


# Getting current rate
# Initialize the API
fred = fredapi.Fred(api_key='8f7cbcbc1210c7efa87ee9484e159c21')

# Get the latest value for the federal funds rate
fed_funds_rate = fred.get_series("FEDFUNDS")

# Get the latest value (i.e., the most recent observation)
latest_value = fed_funds_rate.iloc[-1]

# Print the result
print("The current federal funds rate is {:.2f}%".format(latest_value))


