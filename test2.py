

def calculate_market_sentiment(positive_polarity_24h: float, positive_count_24h: int,
                               negative_polarity_24h: float, negative_count_24h: int,
                               positive_polarity_48h: float, positive_count_48h: int,
                               negative_polarity_48h: float, negative_count_48h: int) -> (float, float):

    # Calculate changes in counts and polarities
    positive_pol_change = positive_polarity_24h - positive_polarity_48h
    positive_count_change = positive_count_24h - positive_count_48h
    negative_pol_change = negative_polarity_24h - negative_polarity_48h
    negative_count_change = negative_count_24h - negative_count_48h

    score, news_bullish, news_bearish = 0, 0, 0
    if positive_pol_change > 0:
        score += 0.1
    elif positive_pol_change < 0:
        score -= 0.1

    if positive_count_change > 0:
        score += 0.1
    elif positive_count_change < 0:
        score -= 0.1

    if negative_pol_change > 0:
        score -= 0.2
    elif negative_pol_change < 0:
        score += 0.2

    if negative_count_change > 0:
        score -= 0.1
    elif negative_count_change < 0:
        score += 0.1

    if score > 0:
        news_bullish = 0.5 + score
    elif score < 0:
        news_bearish = 0.5 + abs(score)
    else:
        news_bullish, news_bearish = 0, 0

    return news_bullish, news_bearish


if __name__ == '__main__':
    print(calculate_market_sentiment(2, 2, 2, 1,
                                     1, 1, 2, 3))

