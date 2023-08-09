# Constants
LONG_THRESHOLD = 0.68
SHORT_THRESHOLD = 0.3
RICHEST_ADDRESSES_SLEEP_TIME = 20 * 60
MAIN_TRADING_LOOP_SLEEP_TIME = 20 * 60
MIN_CONTRIBUTING_FACTORS_WEIGHT = 0.57


# Market scanner
WEIGHTS = {
    "macro": 0.2,
    "order": 0.2,
    "prediction": 0.15,
    "technical": 0.125,
    "richest": 0.125,
    "google": 0.05,
    "reddit": 0.05,
    "youtube": 0.05,
    "news": 0.05,
}

factor_values = {
    'macro': 0.5,
    'order': 0.5,
    'prediction': 0.5,
    'technical': 0.5,
    'richest': 0.5,
    'google': 0.5,
    'reddit': 0.5,
    'youtube': 0.5,
    'news': 0.5
}

position = {
    'opening_score': 0.0,
    'opening_time': '',
    'closing_time': '',
    'opening_price': 0,
    'closing_price': 0,
    'profit_target': 0,
    'stop_loss': 0,
    'PNL': 0,
    'closing_score': 0.5,
    'type': ''
}

# Position dictionaries and constants
LONG_POSITION = {
    'THRESHOLD_TO_CLOSE': 0.4,
    'PROFIT_MARGIN': 0.01,
    'SIZE': 0.1,
    'LOOP_SLEEP_TIME': 60 * 5
}

SHORT_POSITION = {
    'THRESHOLD_TO_CLOSE': 0.60,
    'PROFIT_MARGIN': 0.01,
    'SIZE': 0.1,
    'LEVERAGE': 10,
    'LOOP_SLEEP_TIME': 60 * 5
}

factor_values_position = {
    'macro': 0.5,
    'order': 0.5,
    'order_target': 0.5,
    'prediction': 0.5,
    'technical': 0.5,
    'richest': 0.5,
    'google': 0.5,
    'reddit': 0.5,
    'youtube': 0.5,
    'news': 0.5
}

WEIGHTS_POSITION = {
    "macro": 0.2,
    "order": 0.2,
    'order_target': 0.15,
    "prediction": 0.10,
    "technical": 0.125,
    "richest": 0.125,
    "google": 0.02,
    "reddit": 0.01,
    "youtube": 0.02,
    "news": 0.05,
}
