import logging
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
from z_read_write_csv import save_value_to_database, save_update_time, write_latest_data

MIN_CONTRIBUTING_FACTORS = 4

# Temporary storage for aggregated values
aggregated_values: Dict[str, List[float]] = {
    'weighted_score_up': [],
    'weighted_score_down': []
}


def count_contributing_factors(*factors: Tuple[float, float]) -> int:
    count = 0
    for bullish, bearish in factors:
        if bullish != 0 or bearish != 0:
            count += 1
    return count


def aggregate_and_save_values():
    if not aggregated_values['weighted_score_up']:  # If there are no values, do nothing
        return

    # Calculate the average values for each key in the temporary storage
    avg_values = {key: sum(values) / len(values) for key, values in aggregated_values.items()}

    # Save the average values to the database
    save_value_to_database('weighted_score_up', avg_values['weighted_score_up'])
    save_value_to_database('weighted_score_down', avg_values['weighted_score_down'])

    # Clear the temporary storage
    for key in aggregated_values:
        aggregated_values[key] = []


def make_trading_decision(factor_values) -> Tuple[float, float]:
    """
    Makes a trading decision based on the conditions met.
    """

    save_update_time('weighted_score')

    macro_bullish = factor_values['macro_bullish']
    macro_bearish = factor_values['macro_bearish']
    order_book_bullish = factor_values['order_book_bullish']
    order_book_bearish = factor_values['order_book_bearish']
    prediction_bullish = factor_values['prediction_bullish']
    prediction_bearish = factor_values['prediction_bearish']
    technical_bullish = factor_values['technical_bullish']
    technical_bearish = factor_values['technical_bearish']
    richest_addresses_bullish = factor_values['richest_bullish']
    richest_addresses_bearish = factor_values['richest_bearish']
    google_search_bullish = factor_values['google_bullish']
    google_search_bearish = factor_values['google_bearish']
    reddit_bullish = factor_values['reddit_bullish']
    reddit_bearish = factor_values['reddit_bearish']
    youtube_bullish = factor_values['youtube_bullish']
    youtube_bearish = factor_values['youtube_bearish']
    news_bullish = factor_values['news_bullish']
    news_bearish = factor_values['news_bearish']

    # Calculate the number of contributing factors
    num_contributing_factors = count_contributing_factors(
        (macro_bullish, macro_bearish),
        (order_book_bullish, order_book_bearish),
        (prediction_bullish, prediction_bearish),
        (technical_bullish, technical_bearish),
        (richest_addresses_bullish, richest_addresses_bearish),
        (google_search_bullish, google_search_bearish),
        (reddit_bullish, reddit_bearish),
        (youtube_bullish, youtube_bearish),
        (news_bullish, news_bearish)
    )

    weights = {
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

    # Calculate the weighted score for each alternative:
    weighted_score_up = (
            weights["macro_indicators"] * macro_bullish +
            weights["order_book"] * order_book_bullish +
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
            weights["predicted_price"] * prediction_bearish +
            weights["technical_analysis"] * technical_bearish +
            weights["richest_addresses"] * richest_addresses_bearish +
            weights["google_search"] * google_search_bearish +
            weights["reddit"] * reddit_bearish +
            weights["youtube"] * youtube_bearish +
            weights["sentiment_of_news"] * news_bearish
    )
    # Check if the minimum number of contributing factors is met
    if num_contributing_factors >= MIN_CONTRIBUTING_FACTORS:
        # Normalize the scores
        total_score = weighted_score_up + weighted_score_down

        normalized_score_up = weighted_score_up / total_score
        normalized_score_down = weighted_score_down / total_score

        # Save the latest weighted score
        write_latest_data('latest_weighted_score_up', normalized_score_up)
        write_latest_data('latest_weighted_score_down', normalized_score_down)

        # Save to database Check if an hour has passed since the last database update
        current_time = datetime.now()
        last_hour = current_time.replace(minute=0, second=0, microsecond=0)
        if current_time - last_hour >= timedelta(hours=1):
            aggregate_and_save_values()

        # Save the value in database for a run before an hour pass
        else:
            save_value_to_database('weighted_score_up', round(normalized_score_up, 2))
            save_value_to_database('weighted_score_down', round(normalized_score_down, 2))

        return round(normalized_score_up, 2), round(normalized_score_down, 2)    # ...
    else:
        # Save the latest weighted score
        write_latest_data('latest_weighted_score_up', 0.0)
        write_latest_data('latest_weighted_score_down', 0.0)

        logging.info(f"Minimum contributing factors not met: {num_contributing_factors}/{MIN_CONTRIBUTING_FACTORS}")
        return 0.0, 0.0


if __name__ == "__main__":
    score_up, score_down = 0, 0
