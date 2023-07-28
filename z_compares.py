import bisect
from typing import Tuple
from z_read_write_csv import read_database

LATEST_INFO_PATH = 'data/latest_info_saved.csv'

# constants
INF = float('inf')

# 1. Macro
RANGES_MACRO_MTM = [(-INF, -0.75), (-0.75, -0.5), (-0.5, -0.25),
                    (-0.25, 0.1), (0.1, 0.26), (0.26, 0.51), (0.51, 0.76), (0.76, INF)]
VALUES_MACRO_MTM = [(1.0, 0.0), (0.85, 0.15), (0.7, 0.3), (0.6, 0.4), (0.4, 0.6),
                    (0.3, 0.7), (0.15, 0.85), (0.0, 1.0)]

# 2. Order book
RANGES_ORDER_VOL = [(0.5, 0.53), (0.53, 0.56), (0.56, 0.59), (0.59, 0.62), (0.62, 0.65), (0.65, INF)]
VALUES_ORDER_VOL = [(0.0, 0.0), (0.6, 0.4), (0.7, 0.3), (0.8, 0.2), (0.9, 0.1), (1.0, 0.0)]

# 3. Prediction
RANGES_PREDICTION = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, float('inf'))]
VALUES_PREDICTION_GREATER = [(0.0, 0.0), (0.6, 0.4), (0.7, 0.3), (0.8, 0.2), (0.9, 0.1), (1.0, 0.0)]
VALUES_PREDICTION_LESSER = [(0.0, 0.0), (0.4, 0.6), (0.3, 0.7), (0.2, 0.8), (0.1, 0.9), (0.0, 1.0)]


# 4. Technical in function

# 5.Richest
RANGES_RICH = [
    (float('-inf'), -5),
    (-5, -4),
    (-4, -3),
    (-3, -2),
    (-2, -1),
    (-1, 1),
    (1, 2),
    (2, 3),
    (3, 4),
    (4, 5),
    (5, float('inf')),
]
VALUES_RICH = [
    (0.0, 1.0),  # <-5
    (0.1, 0.9),  # -5 to -4
    (0.2, 0.8),  # -4 to -3
    (0.3, 0.7),  # -3 to -2
    (0.4, 0.6),  # -2 to -1
    (0.0, 0.0),  # -1 to 1
    (0.6, 0.4),  # 1 to 2
    (0.7, 0.3),  # 2 to 3
    (0.8, 0.2),  # 3 to 4
    (0.9, 0.1),  # 4 to 5
    (1.0, 0.0),  # >5
]


# 6,7,8. Google, Reddit, You tube
RANGES_GOOGLE = [(1.0, 1.1), (1.1, 1.15), (1.15, 1.2), (1.2, 1.25), (1.25, float('inf'))]
VALUES__GOOGLE = [(0.0, 0.0), (0.6, 0.4), (0.75, 0.25), (0.85, 0.15), (1.0, 0.0)]
RANGES_GOOGLE_DOWN = [(1.0, 1.1), (1.1, 1.15), (1.15, 1.2), (1.2, 1.25), (1.25, float('inf'))]
VALUES_GOOGLE_DOWN = [(0.0, 0.0), (0.4, 0.6), (0.25, 0.75), (0.15, 0.85), (0.0, 1.0)]

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
        return compare(probability_down, RANGES_ORDER_VOL, [val[::-1] for val in VALUES_ORDER_VOL])


def compare_predicted_price(predicted_price: int, current_price: int) -> Tuple[float, float]:
    if predicted_price > current_price:
        price_difference_percentage = (predicted_price - current_price) / current_price * 100
        return compare(price_difference_percentage, RANGES_PREDICTION, VALUES_PREDICTION_GREATER)
    elif current_price > predicted_price:
        price_difference_percentage = (current_price - predicted_price) / predicted_price * 100
        return compare(price_difference_percentage, RANGES_PREDICTION, VALUES_PREDICTION_LESSER)
    else:
        return 0.0, 0.0


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

    df = read_database()
    total_received = df['richest_addresses_total_received'][-1]
    total_sent = df['richest_addresses_total_sent'][-1]

    if total_received > total_sent:
        activity_percentage = ((total_received - total_sent) / total_sent) * 100
    elif total_sent > total_received:
        activity_percentage = -((total_sent - total_received) / total_received) * 100
    else:
        activity_percentage = 0

    return compare(activity_percentage, RANGES_RICH, VALUES_RICH)


def compare_google_reddit_youtube(last_hour: int, two_hours_before: int) -> Tuple[float, float]:
    # prevent division by zero
    if last_hour == 0 or two_hours_before == 0:
        last_hour += 1
        two_hours_before += 1

    if last_hour >= two_hours_before:
        ratio = last_hour / two_hours_before
        return compare(ratio, RANGES_GOOGLE, VALUES__GOOGLE)
    else:
        ratio = two_hours_before / last_hour
        return compare(ratio, RANGES_GOOGLE_DOWN, VALUES_GOOGLE_DOWN)
