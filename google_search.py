from pytrends.request import TrendReq
import numpy as np
pytrends = TrendReq(hl='en-US', tz=360)

kw_list = ["Bitcoin"]

pytrends.build_payload(kw_list, cat=0, timeframe='now 7-d', geo='', gprop='')

trend = pytrends.interest_over_time()

# Calculate the average increase in search volume
search_volume = trend['Bitcoin'].values
increase = np.diff(search_volume)
#print(increase)
average_increase = np.mean(increase)
#print(average_increase)

# Check if the last hour's search volume is significantly higher
last_hour = trend.iloc[-1]['Bitcoin']
if last_hour > ((search_volume[-2] + average_increase)*1.2):
    print("There is an unusual increase in search in the last hour")
else:
    print("The search trend in the last hour is normal")