import bisect
from typing import Tuple
from z_read_write_csv import read_database

LATEST_INFO_PATH = 'data/latest_info_saved.csv'

# constants
INF = float('inf')
SHORT_MOVING_AVERAGE_WINDOW_Rich = 5
LONG_MOVING_AVERAGE_WINDOW_Rich = 20

SHORT_MOVING_AVERAGE_WINDOW_ORDER = 5
LONG_MOVING_AVERAGE_WINDOW_ORDER = 20

SHORT_MOVING_AVERAGE_GOOGLE = 5
LONG_MOVING_AVERAGE_GOOGLE = 20

# 1. Macro
RANGES_MACRO_MTM = [(-INF, -0.75), (-0.75, -0.5), (-0.5, -0.25),
                    (-0.25, 0.1), (0.1, 0.26), (0.26, 0.51), (0.51, 0.76), (0.76, INF)]
VALUES_MACRO_MTM = [(1.0, 0.0), (0.85, 0.15), (0.7, 0.3), (0.6, 0.4), (0.4, 0.6),
                    (0.3, 0.7), (0.15, 0.85), (0.0, 1.0)]

# 2. Order book
RANGES_ORDER_VOL = [(0.5, 0.53), (0.53, 0.56), (0.56, 0.59), (0.59, 0.62), (0.62, 0.65), (0.65, INF)]
VALUES_ORDER_VOL = [0.5, 0.6, 0.7, 0.8, 0.9, 1.0]

# 3. Prediction
RANGES_PREDICTION = [(0, 0.5), (0.5, 1), (1, 1.5), (1.5, 3), (3, 4), (4, float('inf'))]
VALUES_PREDICTION_GREATER = [0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
VALUES_PREDICTION_LESSER = [0.5, 0.4, 0.3, 0.2, 0.1, 0.0]

# 5.Richest
RANGES_RICH = [
    (float('-inf'), -3),  # 0.0
    (-3, -2),      # 0.1
    (-2, -1.5),    # 0.2
    (-1.5, -1),    # 0.3
    (-1, -0.5),    # 0.4
    (-0.5, 0.5),   # 0.5
    (0.5, 1),  # 0.6
    (1, 1.5),  # 0.7
    (1.5, 2),  # 0.8
    (2, 3),    # 0.9
    (3, float('inf')),   # 1.0
]
VALUES_RICH = [
    0.0,  # <- < -3
    0.1,  # -2 to -3
    0.2,  # -1.5 to -2
    0.3,  # -1 to -1.5
    0.4,  # -0.5 to -1
    0.5,  # -0.5 to 0.5
    0.6,  # 0.5 to 1
    0.7,  # 1 to 1.5
    0.8,  # 1.5 to 2
    0.9,  # 2 to 3
    1.0,  # >3
]


RANGES_GOOGLE = [(1.0, 1.1), (1.1, 1.15), (1.15, 1.2), (1.2, 1.25), (1.25, float('inf'))]
VALUES__GOOGLE = [0.5, 0.6, 0.75, 0.85, 1.0]
RANGES_GOOGLE_DOWN = [(1.0, 1.1), (1.1, 1.15), (1.15, 1.2), (1.2, 1.25), (1.25, float('inf'))]
VALUES_GOOGLE_DOWN = [0.5, 0.4, 0.25, 0.15, 0.0]


def compare(data, ranges, values):
    # Extract the right side of each range for comparison
    right_ranges = [r[1] for r in ranges]
    index = bisect.bisect_right(right_ranges, data)
    return values[index]


def compare_macro_m_to_m(cpi_m_to_m: float) -> Tuple[float, float]:
    return compare(cpi_m_to_m, RANGES_MACRO_MTM, VALUES_MACRO_MTM)


def moving_averages_cross_order_book() -> float:
    df = read_database()

    # Calculate the short and long moving averages for total received
    short_mv_bid = (df['bid_volume'].
                    rolling(window=SHORT_MOVING_AVERAGE_WINDOW_ORDER).mean().tail(1).item())
    long_mv_bid = (df['bid_volume'].
                   rolling(window=LONG_MOVING_AVERAGE_WINDOW_ORDER).mean().tail(1).item())

    short_mv_ask = (df['ask_volume'].
                    rolling(window=SHORT_MOVING_AVERAGE_WINDOW_ORDER).mean().tail(1).item())
    long_mv_ask = (df['ask_volume'].
                   rolling(window=LONG_MOVING_AVERAGE_WINDOW_ORDER).mean().tail(1).item())

    if short_mv_bid > long_mv_bid and short_mv_ask < long_mv_ask:
        return 0.15
    elif short_mv_bid < long_mv_bid and short_mv_ask > long_mv_ask:
        return -0.15

    elif short_mv_bid > long_mv_bid and short_mv_ask > long_mv_ask:
        return 0.1
    elif short_mv_bid < long_mv_bid and short_mv_ask < long_mv_ask:
        return -0.1
    else:
        return 0.0


def compare_order_volume(probability_up: float, probability_down: float) -> float:
    if probability_up >= probability_down:
        order_bullish = compare(probability_up, RANGES_ORDER_VOL, VALUES_ORDER_VOL)
    else:
        order_bearish = compare(
            probability_down, RANGES_ORDER_VOL, VALUES_ORDER_VOL)
        order_bullish = round(1 - order_bearish, 2)

    mv_add_on_bullish = moving_averages_cross_order_book()
    order_bullish += mv_add_on_bullish
    order_bullish = round(order_bullish, 2)

    # Ensure values are within the range [0, 1]
    order_bullish = min(max(order_bullish, 0), 1)

    return order_bullish


def compare_predicted_price(predicted_price: int, current_price: int) -> float:
    if predicted_price > current_price:
        price_difference_percentage = (predicted_price - current_price) / current_price * 100
        prediction_bullish = compare(
            price_difference_percentage, RANGES_PREDICTION, VALUES_PREDICTION_GREATER)
        return prediction_bullish
    elif current_price > predicted_price:
        price_difference_percentage = (current_price - predicted_price) / predicted_price * 100
        prediction_bullish = compare(
            price_difference_percentage, RANGES_PREDICTION, VALUES_PREDICTION_LESSER)
        return prediction_bullish
    else:
        return 0.5


def compare_technical(reversal: str, potential_up_trend: bool, over_ema200: bool) -> float:
    # Define a dictionary for all possibilities
    technical_mapping = {
        # Reversal, Trend, EMA200
        ('up', True, True): 1,
        ('up', True, False): 0.9,
        ('up', False, True): 0.9,
        ('up', False, False): 0.8,

        ('down', False, False): 0,
        ('down', True, False): 0.1,
        ('down', False, True): 0.1,
        ('down', True, True): 0.2,

        ('neither', True, False): 0.5,
        ('neither', False, True): 0.5,
        ('neither', True, True): 0.7,
        ('neither', False, False): 0.3
    }
    return technical_mapping[(reversal, potential_up_trend, over_ema200)]


def moving_averages_cross_richest() -> float:
    df = read_database()

    # Calculate the short and long moving averages for total received
    short_mv_received = (df['richest_addresses_total_received'].
                         rolling(window=SHORT_MOVING_AVERAGE_WINDOW_Rich).mean().tail(1).item())
    long_mv_received = (df['richest_addresses_total_received'].
                        rolling(window=LONG_MOVING_AVERAGE_WINDOW_Rich).mean().tail(1).item())

    short_mv_sent = (df['richest_addresses_total_sent'].
                     rolling(window=SHORT_MOVING_AVERAGE_WINDOW_Rich).mean().tail(1).item())
    long_mv_sent = (df['richest_addresses_total_sent'].
                    rolling(window=LONG_MOVING_AVERAGE_WINDOW_Rich).mean().tail(1).item())

    if short_mv_received > long_mv_received and short_mv_sent < long_mv_sent:
        return 0.1
    elif short_mv_received < long_mv_received and short_mv_sent > long_mv_sent:
        return -0.1
    else:
        return 0.0


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
    rich_bullish = compare(activity_percentage, RANGES_RICH, VALUES_RICH)

    mv_add_on_bullish = moving_averages_cross_richest()
    rich_bullish += mv_add_on_bullish
    print('add on ', mv_add_on_bullish)
    rich_bullish = round(rich_bullish, 2)

    # Ensure values are within the range [0, 1]
    rich_bullish = min(max(rich_bullish, 0), 1)
    return rich_bullish


def compare_google(last_hour: int, two_hours_before: int) -> float:
    # prevent division by zero
    if last_hour == 0 or two_hours_before == 0:
        last_hour += 1
        two_hours_before += 1

    # moving_averages_google
    if last_hour >= two_hours_before:
        ratio = last_hour / two_hours_before
        google = compare(ratio, RANGES_GOOGLE, VALUES__GOOGLE)
    else:
        ratio = two_hours_before / last_hour
        google = compare(ratio, RANGES_GOOGLE_DOWN, VALUES_GOOGLE_DOWN)

    if last_hour > 70:
        AMPLIFICATION_FACTOR = 1 + ((last_hour - 70) / 30)  # Scale from 1 to 2 as last_hour goes from 70 to 100
        google = google * AMPLIFICATION_FACTOR
    elif last_hour < 30:
        AMPLIFICATION_FACTOR = 1 + ((30 - last_hour) / 30)  # Scale from 1 to 2 as last_hour goes from 0 to 30
        google = google / AMPLIFICATION_FACTOR

    google = min(max(google, 0), 1)
    return google


if __name__ == '__main__':
    print(compare_richest_addresses())
