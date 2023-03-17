import pandas as pd
from datetime import datetime

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

latest_info_saved = pd.read_csv('latest_info_saved.csv')

# Save the update time to disk
now = datetime.now()
now_str = now.strftime('%Y-%m-%d %H:%M:%S')
latest_info_saved['last_reddit_update_time'] = now_str

latest_info_saved.to_csv('latest_info_saved.csv', index=False)
