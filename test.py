import time
from pytrends.request import TrendReq



pytrends = TrendReq(hl='en-US', tz=360)

def get_average_trend(keywords):
    pytrends.build_payload(kw_list=keywords, cat=0, timeframe='today 12-m', geo='', gprop='')
    trend_data = pytrends.interest_over_time()
    trend_data['mean'] = trend_data[keywords].mean(axis=0)
    return trend_data['mean']

def get_current_trend(keywords):
    pytrends.build_payload(kw_list=keywords, cat=0, timeframe='now 1-m', geo='', gprop='')
    trend_data = pytrends.interest_over_time()
    return trend_data[keywords].iloc[-1]

def check_trends(keywords, average_trend):
    current_trend = get_current_trend(keywords)
    if (current_trend < 0.8 * average_trend).any() or (current_trend > 1.2 * average_trend).any():
        print("Warning: Unusual search trend detected for keywords", keywords)
        print("Current trend:", current_trend)
        print("Average trend:", average_trend)

keywords = ["Bitcoin", "crypto", "cryptocurrency", "ethereum"]
average_trend = get_average_trend(keywords)

while True:
    check_trends(keywords, average_trend)
    time.sleep(60)
