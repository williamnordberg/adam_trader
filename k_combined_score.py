import logging
from z_read_write_csv import save_value_to_database, save_update_time
from a_config import WEIGHTS, MIN_CONTRIBUTING_FACTORS_WEIGHT


def count_contributing_factors(*factors: float) -> float:
    total_weight = 0.0
    for weight, bullish in zip(WEIGHTS.values(), factors):
        if bullish != 0.5:
            total_weight += weight
    return total_weight


def make_trading_decision(factor_values) -> float:

    weight_of_contributing_factors = count_contributing_factors(*factor_values.values())
    if weight_of_contributing_factors < MIN_CONTRIBUTING_FACTORS_WEIGHT:
        logging.info(f"Minimum contributing factors weight not met to decide opening position: "
                     f"{weight_of_contributing_factors}/ out of {MIN_CONTRIBUTING_FACTORS_WEIGHT}")
        save_value_to_database('weighted_score_up', 0.5)
        return 0.5

    # Compute bearish values
    factors = {key: (value, round(1 - value, 2)) for key, value in factor_values.items()}
    weighted_score_up,  weighted_score_down = 0, 0
    for key, weight in WEIGHTS.items():
        bullish, bearish = factors[key]
        weighted_score_up += weight * bullish
        weighted_score_down += weight * bearish

    save_update_time('weighted_score')

    total_score = weighted_score_up + weighted_score_down
    normalized_score = round((weighted_score_up / total_score), 2)

    save_value_to_database('weighted_score_up', normalized_score)

    return normalized_score


if __name__ == "__main__":
    factor_values_outer = {'macro': 0.68, 'order': 0.68,
                           'prediction': 0.68, 'technical': 0.68,
                           'richest': 0.68, 'google': 0.68, 'reddit': 0.68,
                           'youtube': 0.68, 'news': 0.68}

    print(make_trading_decision(factor_values_outer))
