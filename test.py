import pandas as pd
from datetime import datetime, timezone, timedelta
from pytz import UTC

current_hour = pd.Timestamp.now(tz='utc').floor("H").strftime('%Y-%m-%d %H:%M:%S')
test3 = datetime.now(timezone.utc).replace(tzinfo=None, microsecond=0)
last_update_time21 = datetime.strptime('2023-06-14 18:00:00', '%Y-%m-%d %H:%M:%S')
bool = datetime.now(timezone.utc).replace(tzinfo=None, microsecond=0) - last_update_time21 < timedelta(hours=1)

current_hour_pandas = pd.Timestamp.now(tz='UTC').floor("H")
print(current_hour_pandas)
print(type(current_hour_pandas))

current_hour3 = pd.Timestamp.now(tz='UTC').floor("H").tz_localize(None)
print(type(current_hour3))
print(current_hour3)