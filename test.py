import pandas as pd
from datetime import datetime, timezone

current_hour = pd.Timestamp.now(tz='utc').floor("H").strftime('%Y-%m-%d %H:%M:%S')
current_datet = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
print(current_hour)
print(current_datet)