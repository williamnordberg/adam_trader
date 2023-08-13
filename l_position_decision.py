import logging
from z_read_write_csv import write_latest_data
from a_config import WEIGHTS_POSITION
from k_combined_score import make_trading_decision

MIN_CONTRIBUTING_FACTORS_WEIGHT = 0.5


def calculate_contributing_factors(*factors: float) -> float:
    total_weight = 0.0
    for weight, bullish in zip(WEIGHTS_POSITION.values(), factors):
        if bullish != 0.5:
            total_weight += weight
    return total_weight


def position_decision_wrapper(factor_values_position) -> float:

    weight_of_contributing_factors = calculate_contributing_factors(*factor_values_position.values())
    if weight_of_contributing_factors < MIN_CONTRIBUTING_FACTORS_WEIGHT:
        logging.info(f"Minimum contributing factors weight not met to decide position status: "
                     f"{weight_of_contributing_factors}/ out of {MIN_CONTRIBUTING_FACTORS_WEIGHT}")
        write_latest_data('score_profit_position', 0.5)
        return 0.5

    # Compute bearish values
    factors = {key: (value, round(1 - value, 2)) for key, value in factor_values_position.items()}
    weighted_score_up,  weighted_score_down = 0, 0
    for key, weight in WEIGHTS_POSITION.items():
        bullish, bearish = factors[key]
        weighted_score_up += weight * bullish
        weighted_score_down += weight * bearish

    total_score = weighted_score_up + weighted_score_down
    normalized_score = round((weighted_score_up / total_score), 2)

    return normalized_score


def position_decision(factor_values_position) -> float:

    normalized_score = position_decision_wrapper(factor_values_position)
    write_latest_data('score_profit_position', round(normalized_score, 2))

    # Calculate combined score for database, and Remove the key 'order_target'
    factor_values_outer.pop('order_target', None)
    make_trading_decision(factor_values_position)

    return normalized_score


if __name__ == "__main__":
    factor_values_outer = {
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
    score = position_decision_wrapper(factor_values_outer)
    print(f'score: {score}')
