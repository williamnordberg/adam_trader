import logging
from position import long_position_is_open, short_position_is_open

long_threshold = 0.2
short_threshold = 0.2


def make_trading_decision(macro_bullish, macro_bearish,
                          order_book_bullish, order_book_bearish,
                          prediction_bullish, prediction_bearish,
                          technical_bullish, technical_bearish,
                          richest_addresses_bullish, richest_addresses_bearish,
                          google_search_bullish, google_search_bearish,
                          reddit_bullish, reddit_bearish,
                          youtube_bullish, youtube_bearish,
                          news_bullish, news_bearish):

    """
    Makes a trading decision based on the conditions met.
    """
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

    if weighted_score_up > weighted_score_down and weighted_score_up > long_threshold:
        logging.info('Opening a long position')
        profit_after_trade, loss_after_trade = long_position_is_open()
        logging.info(f"profit_after_trade:{profit_after_trade}, loss_after_trade:"
                     f"{loss_after_trade}")
    elif weighted_score_down > weighted_score_up and weighted_score_down > short_threshold:
        logging.info('Opening short position')
        profit_after_trade, loss_after_trade = short_position_is_open()
        logging.info(f"profit_after_trade:{profit_after_trade}, "
                     f"loss_after_trade:{loss_after_trade}")
