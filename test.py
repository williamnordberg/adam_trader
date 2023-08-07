import logging
from typing import Tuple
from z_read_write_csv import save_value_to_database, save_update_time

MIN_CONTRIBUTING_FACTORS_WEIGHT = 0.6
WEIGHTS = {
    "macro_indicators": 0.2,
    "order_book": 0.2,
    "predicted_price": 0.15,
    "technical_analysis": 0.125,
    "richest_addresses": 0.125,
    "google_search": 0.05,
    "reddit": 0.05,
    "youtube": 0.05,
    "sentiment_of_news": 0.05,
}


def count_contributing_factors(*factors: Tuple[float, float]) -> float:
    total_weight = 0.0
    for weight, (bullish, bearish) in zip(WEIGHTS.values(), factors):
        if bullish != 0 or bearish != 0:
            total_weight += weight
    return total_weight


def make_trading_decision(factor_values) -> Tuple[float, float]:
    factors = (
        (factor_values['macro_bullish'],
        (factor_values['order_book_bullish'],
        (factor_values['prediction_bullish'],
        (factor_values['technical_bullish'],
        (factor_values['richest_bullish'],
        (factor_values['google_bullish'],
        (factor_values['reddit_bullish'],
        (factor_values['youtube_bullish'],
        (factor_values['news_bullish'],
    )

    weight_of_contributing_factors = count_contributing_factors(*factors)
    weighted_score_up = weighted_score_down = 0
    for key, weight in WEIGHTS.items():
        bullish = factor_values[f"{key}_bullish"]
        weighted_score_up += weight * bullish
        weighted_score_down += weight * (1 - bullish)

    save_update_time('weighted_score')

    if weight_of_contributing_factors < MIN_CONTRIBUTING_FACTORS_WEIGHT:
        logging.info(f"Minimum contributing factors weight not met: "
                     f"{weight_of_contributing_factors}/ out of {MIN_CONTRIBUTING_FACTORS_WEIGHT}")
        save_value_to_database('weighted_score_up', 0.0)
        save_value_to_database('weighted_score_down', 0.0)
        return 0.0, 0.0

    total_score = weighted_score_up + weighted_score_down
    normalized_score_up = round((weighted_score_up / total_score), 2)
    normalized_score_down = round((weighted_score_down / total_score), 2)

    save_value_to_database('weighted_score_up', normalized_score_up)
    save_value_to_database('weighted_score_down', normalized_score_down)

    return normalized_score_up, normalized_score_down


if __name__ == "__main__":
    factor_values_outer = {
        'macro_bullish': 1,
        'macro_bearish': 0.0,
        'order_book_bullish': 0.3,
        'order_book_bearish': 0.7,
        'prediction_bullish': 0.7,
        'prediction_bearish': 0.3,
        'technical_bullish': 1,
        'technical_bearish': 0.0,
        'richest_bullish': 0.0,
        'richest_bearish': 1,
        'google_bullish': 0.0,
        'google_bearish': 1,
        'reddit_bullish': 0.1,
        'reddit_bearish': 0.9,
        'youtube_bullish': 1,
        'youtube_bearish': 0.0,
        'news_bullish': 0.0,
        'news_bearish': 0.0,
        'weighted_score_up': 0.0,
        'weighted_score_down': 0.0
    }
    print(make_trading_decision(factor_values_outer))
