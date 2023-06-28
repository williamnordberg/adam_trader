import logging
from typing import Tuple
from read_write_csv import write_latest_data

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def position_decision(macro_bullish: float, macro_bearish: float,
                      order_book_bullish: float, order_book_bearish: float,
                      probability_to_hit_target: float, probability_to_hit_stop_loss: float,
                      prediction_bullish: float, prediction_bearish: float,
                      technical_bullish: float, technical_bearish: float,
                      richest_addresses_bullish: float, richest_addresses_bearish: float,
                      google_search_bullish: float, google_search_bearish: float,
                      reddit_bullish: float, reddit_bearish: float,
                      youtube_bullish: float, youtube_bearish: float,
                      news_bullish: float, news_bearish: float) -> Tuple[float, float]:

    """
    Makes a trading decision based on the conditions met.
    """
    weights = {
        "macro_indicators": 0.2,
        "order_book": 0.2,
        'probability_to_hit_target_or_stop': 0.15,
        "predicted_price": 0.10,
        "technical_analysis": 0.125,
        "richest_addresses": 0.125,
        "google_search": 0.01,
        "reddit": 0.01,
        "youtube": 0.02,
        "sentiment_of_news": 0.05,
    }

    # Calculate the weighted score for each alternative:
    weighted_score_up = (
            weights["macro_indicators"] * macro_bullish +
            weights["order_book"] * order_book_bullish +
            weights["probability_to_hit_target_or_stop"] * probability_to_hit_target +
            weights["predicted_price"] * prediction_bullish +
            weights["technical_analysis"] * technical_bullish +
            weights["richest_addresses"] * richest_addresses_bullish +
            weights["google_search"] * google_search_bullish +
            weights["reddit"] * reddit_bullish +
            weights["youtube"] * youtube_bullish +
            weights["sentiment_of_news"] * news_bullish
    )

    weighted_score_down = (
            weights["macro_indicators"] * macro_bearish +
            weights["order_book"] * order_book_bearish +
            weights["probability_to_hit_target_or_stop"] * probability_to_hit_stop_loss +
            weights["predicted_price"] * prediction_bearish +
            weights["technical_analysis"] * technical_bearish +
            weights["richest_addresses"] * richest_addresses_bearish +
            weights["google_search"] * google_search_bearish +
            weights["reddit"] * reddit_bearish +
            weights["youtube"] * youtube_bearish +
            weights["sentiment_of_news"] * news_bearish
    )
    # Normalize the scores
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

    logging.info(f'score_up: {score_up}, score_down: {score_down}')
