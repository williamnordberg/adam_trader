import bisect
import pandas as pd
from typing import Tuple
from handy_modules import save_update_time, read_float_from_latest_saved
from news_aggregate import aggregate_news

LATEST_INFO_PATH = 'data/latest_info_saved.csv'

# constants
INF = float('inf')

# 1. Macro
RANGES_MACRO_MTM = [(-INF, -0.75), (-0.75, -0.5), (-0.5, -0.25),
                    (-0.25, 0), (0, 0.25), (0.25, 0.5), (0.5, 0.75), (0.75, INF)]
VALUES_MACRO_MTM = [(1.0, 0.0), (0.85, 0.15), (0.7, 0.3), (0.6, 0.4), (0.4, 0.6), (0.3, 0.7), (0.15, 0.85), (0.0, 1.0)]

# 2. Order book
RANGES_ORDER_VOL = [(0.53, 0.56), (0.56, 0.59), (0.59, 0.62), (0.62, 0.65), (0.65, INF)]
VALUES_ORDER_VOL = [(0.6, 0.4), (0.7, 0.3), (0.8, 0.2), (0.9, 0.1), (1.0, 0.0)]

# 3. Prediction
RANGES_PREDICTION = [(0, 5), (5, 10), (10, 20), (20, float('inf'))]
VALUES_PREDICTION = [(0.1, 0.9), (0.2, 0.8), (0.5, 0.5), (1, 0)]

# 4. Technical in function

# 5.Richest
RANGES_RICH = [(-INF, -50), (-50, -40), (-40, -30), (-30, -20),
               (-20, -10), (-10, 0), (0, 10), (10, 20), (20, 30), (30, 40), (40, 50), (50, INF)]
VALUES_RICH = [(0.0, 1.0), (0.1, 0.9), (0.2, 0.8), (0.3, 0.7),
               (0.4, 0.6), (0.0, 0.0), (0.6, 0.4), (0.7, 0.3), (0.8, 0.2), (0.9, 0.1), (1.0, 0.0)]

# 6,7,8. Google, Reddit, Youtube
RANGES_GOOGLE = [(1.1, 1.15), (1.15, 1.2), (1.2, 1.25), (1.25, float('inf'))]
VALUES__GOOGLE = [(0.6, 0.4), (0.75, 0.25), (0.85, 0.15), (1, 0)]
RANGES_GOOGLE_DOWN = [(1.1, 1.15), (1.15, 1.2), (1.2, 1.25), (1.25, float('inf'))]
VALUES_GOOGLE_DOWN = [(0.4, 0.6), (0.25, 0.75), (0.15, 0.85), (0, 1)]

# 9.News in function


def compare(data, ranges, values):
    # Extract the right side of each range for comparison
    right_ranges = [r[1] for r in ranges]
    index = bisect.bisect_right(right_ranges, data)
    return values[index]


def compare_macro_m_to_m(cpi_m_to_m: float) -> Tuple[float, float]:
    return compare(cpi_m_to_m, RANGES_MACRO_MTM, VALUES_MACRO_MTM)


def compare_order_volume(probability_up: float, probability_down: float) -> Tuple[float, float]:
    if probability_up >= probability_down:
        return compare(probability_up, RANGES_ORDER_VOL, VALUES_ORDER_VOL)
    else:
        return compare(probability_down, RANGES_ORDER_VOL, [val[::-1] for val in VALUES_ORDER_VOL[::-1]])


def compare_predicted_price(predicted_price: int, current_price: int) -> Tuple[float, float]:
    price_difference_percentage = (predicted_price - current_price) / current_price * 100
    return compare(price_difference_percentage, RANGES_PREDICTION, VALUES_PREDICTION)


def compare_technical(reversal: str, potential_up_trend: bool, over_ema200: bool) -> Tuple[float, float]:
    # Define a dictionary for all possibilities
    technical_mapping = {
        # Reversal, Trend, EMA200
        ('up', True, True): (1, 0),
        ('up', True, False): (0.9, 0.1),
        ('up', False, True): (0.9, 0.1),
        ('up', False, False): (0.8, 0.2),

        ('down', False, False): (0, 1),
        ('down', True, False): (0.1, 0.9),
        ('down', False, True): (0.1, 0.9),
        ('down', True, True): (0.2, 0.8),

        ('neither', True, False): (0, 0),
        ('neither', False, True): (0, 0),
        ('neither', True, True): (0.7, 0.3),
        ('neither', False, False): (0.3, 0.7)
    }
    return technical_mapping[(reversal, potential_up_trend, over_ema200)]


def compare_richest_addresses() -> Tuple[float, float]:
    latest_info_saved = pd.read_csv(LATEST_INFO_PATH)
    total_received = latest_info_saved['total_received_coins_in_last_24'][0]
    total_sent = latest_info_saved['total_sent_coins_in_last_24'][0]

    # Save latest update time
    save_update_time('richest_addresses')

    activity_percentage = (total_received - total_sent) / total_sent * 100
    return compare(activity_percentage, RANGES_RICH, VALUES_RICH)


def compare_google_reddit_youtube(last_hour: int, two_hours_before: int) -> Tuple[float, float]:
    if last_hour >= two_hours_before:
        ratio = last_hour / two_hours_before
        return compare(ratio, RANGES_GOOGLE, VALUES__GOOGLE)
    else:
        ratio = two_hours_before / last_hour
        return compare(ratio, RANGES_GOOGLE_DOWN, VALUES_GOOGLE_DOWN)


def compare_news() -> (float, float):
    positive_polarity_24h, negative_polarity_24h, \
     positive_count_24h, negative_count_24h = aggregate_news()

    positive_polarity_48h = round(read_float_from_latest_saved('positive_polarity_score'), 2)
    positive_count_48h = read_float_from_latest_saved('positive_news_count')
    negative_polarity_48h = round(read_float_from_latest_saved('negative_polarity_score'), 2)
    negative_count_48h = read_float_from_latest_saved('negative_news_count')

    positive_pol_change = positive_polarity_24h - positive_polarity_48h
    positive_count_change = positive_count_24h - positive_count_48h
    negative_pol_change = negative_polarity_24h - negative_polarity_48h
    negative_count_change = negative_count_24h - negative_count_48h

    changes = [positive_pol_change, positive_count_change, -negative_pol_change, -negative_count_change]
    weights = [0.1, 0.1, 0.2, 0.1]
    score = sum(c*w for c, w in zip(changes, weights) if c > 0)
    return max(0.5+score, 1), max(0.5-score, 1)  # Restrict between 0 and 1

