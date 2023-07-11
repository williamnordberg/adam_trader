import bisect
from typing import Tuple
from z_read_write_csv import write_latest_data, read_database

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
RANGES_PREDICTION = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, float('inf'))]
VALUES_PREDICTION_GREATER = [(0.0, 0.0), (6, 4), (7, 3), (8, 2), (9, 1), (1, 0.0)]
VALUES_PREDICTION_LESSER = [(0.0, 0.0), (4, 6), (3, 7), (2, 8), (9, 1), (0.0, 1)]


# 4. Technical in function

# 5.Richest
RANGES_RICH = [(-INF, -50), (-50, -40), (-40, -30), (-30, -20),
               (-20, -10), (-10, 0), (0, 10), (10, 20), (20, 30), (30, 40), (40, 50), (50, INF)]
VALUES_RICH = [(0.0, 1.0), (0.1, 0.9), (0.2, 0.8), (0.3, 0.7),
               (0.4, 0.6), (0.0, 0.0), (0.6, 0.4), (0.7, 0.3), (0.8, 0.2), (0.9, 0.1), (1.0, 0.0)]

# 6,7,8. Google, Reddit, Youtube
RANGES_GOOGLE = [(1.0, 1.1), (1.1, 1.15), (1.15, 1.2), (1.2, 1.25), (1.25, float('inf'))]
VALUES__GOOGLE = [(0.0, 0.0), (0.6, 0.4), (0.75, 0.25), (0.85, 0.15), (1, 0.0)]
RANGES_GOOGLE_DOWN = [(1.0, 1.1), (1.1, 1.15), (1.15, 1.2), (1.2, 1.25), (1.25, float('inf'))]
VALUES_GOOGLE_DOWN = [(0.0, 0.0), (0.4, 0.6), (0.25, 0.75), (0.15, 0.85), (0.0, 1)]

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
    activity_percentage = (total_received - total_sent) / total_sent * 100
    print('activity_percentage', activity_percentage)
    return compare(activity_percentage, RANGES_RICH, VALUES_RICH)


def compare_google_reddit_youtube(last_hour: int, two_hours_before: int) -> Tuple[float, float]:
    # prevent division by zero
    if last_hour == 0 or two_hours_before == 0:
        last_hour += 0.0001
        two_hours_before += 0.0001

    if last_hour >= two_hours_before:
        ratio = last_hour / two_hours_before
        return compare(ratio, RANGES_GOOGLE, VALUES__GOOGLE)
    else:
        ratio = two_hours_before / last_hour
        return compare(ratio, RANGES_GOOGLE_DOWN, VALUES_GOOGLE_DOWN)


def compare_news(last_24_hours_positive_polarity: float,
                 last_24_hours_negative_polarity: float, positive_count_24_hours_before: int,
                 negative_count_24_hours_before: int) -> Tuple[float, float]:
    polarity_threshold = 0.01
    threshold = 1

    df = read_database()
    positive_polarity_48h = df['news_positive_polarity'][-1]
    negative_polarity_48h = df['news_negative_polarity'][-1]

    positive_count_48h = df['news_positive_count'][-1]
    negative_count_48h = df['news_negative_count'][-1]

    # Calculate changes in counts and polarities
    positive_pol_change = abs(last_24_hours_positive_polarity - positive_polarity_48h)
    negative_pol_change = abs(last_24_hours_negative_polarity - negative_polarity_48h)
    positive_count_change = abs(positive_count_24_hours_before - positive_count_48h)
    negative_count_change = abs(negative_count_24_hours_before - negative_count_48h)

    # Save for visualization
    write_latest_data('positive_news_polarity_change', round(positive_pol_change, 2))
    write_latest_data('negative_news_polarity_change', round(negative_pol_change, 2))

    score = 0.5  # start point for score

    if positive_pol_change > polarity_threshold:
        if last_24_hours_positive_polarity > positive_polarity_48h:
            score += 0.1
        else:
            score -= 0.1

    if negative_pol_change > polarity_threshold:
        if last_24_hours_negative_polarity < negative_polarity_48h:
            score += 0.2
        else:
            score -= 0.2

    if positive_count_change > threshold:
        if positive_count_24_hours_before > positive_count_48h:
            score += 0.1
        else:
            score -= 0.1

    if negative_count_change > threshold:
        if negative_count_24_hours_before < negative_count_48h:
            score += 0.1
        else:
            score -= 0.1

    # ensure the score is between 0 and 1
    score = min(max(score, 0), 1)

    # use the score to calculate news_bullish and news_bearish
    if score == 0.5:
        return 0.0, 0.0
    news_bullish = score
    news_bearish = 1 - score

    return round(news_bullish, 2), round(news_bearish, 2)


