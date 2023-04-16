from handy_modules import compare_predicted_price, get_bitcoin_price, should_update, save_update_time
from typing import Tuple
from database import read_database


# Save latest update time
save_update_time('predicted_price')


def decision_tree_predictor() -> Tuple[float, float]:
    if should_update('predicted_price'):
        return '_wrapper'
    else:
        database = read_database()
        prediction_bullish = database['prediction_bullish'][-1]
        prediction_bearish = database['prediction_bearish'][-1]
        return prediction_bullish, prediction_bearish

