from typing import Tuple
from z_read_write_csv import write_latest_data

# Define constants
INDICATORS = ["macro", "order_book", "probability_to_hit", "predicted", "technical", 
              "richest_addresses", "google_search", "reddit", "youtube", "news"]
WEIGHTS = [0.2, 0.2, 0.15, 0.10, 0.125, 0.125, 0.01, 0.01, 0.02, 0.05]


def position_decision(indicators: dict) -> Tuple[float, float]:
    assert all(key in indicators for key in INDICATORS), "Missing indicator"

    weighted_score_up = sum(indicators[ind+"_bullish"] * weight for ind, weight in zip(INDICATORS, WEIGHTS))
    weighted_score_down = sum(indicators[ind+"_bearish"] * weight for ind, weight in zip(INDICATORS, WEIGHTS))

    total_score = weighted_score_up + weighted_score_down
    normalized_score_up = weighted_score_up / total_score
    normalized_score_down = weighted_score_down / total_score

    write_latest_data('score_profit_position', round(normalized_score_up, 2))
    write_latest_data('score_loss_position',  round(normalized_score_down, 2))

    return normalized_score_up, normalized_score_down

if __name__ == "__main__":
    score_up, score_down = position_decision(1, 0,
                                             0, 1,
                                             1, 0,
                                             1, 1,
                                             0, 1,
                                             1, 0,
                                             1, 0,
                                             1, 0,
                                             1, 0,
                                             1, 0)

    print(f'score_up: {score_up}, score_down: {score_down}')
