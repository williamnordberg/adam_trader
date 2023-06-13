

def calculate_market_sentiment(positive_polarity_24h: float, positive_count_24h: int,
                               negative_polarity_24h: float, negative_count_24h: int,
                               positive_polarity_48h: float, positive_count_48h: int,
                               negative_polarity_48h: float, negative_count_48h: int) -> (float, float):

    # Calculate changes in counts and polarities
    positive_count_change = positive_count_24h - positive_count_48h
    negative_count_change = negative_count_24h - negative_count_48h
    positive_pol_change = positive_polarity_24h - positive_polarity_48h
    negat_pol_change = negative_polarity_24h - negative_polarity_48h

    print('positive_count_change', positive_count_change)
    print('negative_count_change', negative_count_change)
    print('positive_polarity_change', positive_pol_change)
    print('negative_polarity_change', negat_pol_change)

    # Positive count increases, positive polarity increases, negative count decreases, negative polarity decreases
    if positive_count_change > 0 > negative_count_change and positive_pol_change > 0 > negat_pol_change:
        news_bullish, news_bearish = 1, 0

    # Positive count increases, positive polarity decreases, negative count decreases, negative polarity decreases
    elif positive_count_change > 0 and positive_pol_change < 0 and negative_count_change < 0 and negat_pol_change < 0:
        news_bullish, news_bearish = 0.8, 0.2

    # Positive count decreases, positive polarity increases, negative count decreases, negative polarity decreases
    elif positive_count_change < 0 and positive_pol_change > 0 and negative_count_change < 0 and negat_pol_change < 0:
        news_bullish, news_bearish = 0.8, 0.2

    # Positive count decreases, positive polarity decreases, negative count decreases, negative polarity decreases
    elif positive_count_change < 0 and positive_pol_change < 0 and negative_count_change < 0 and negat_pol_change < 0:
        news_bullish, news_bearish = 0, 0

    # Positive count increases, positive polarity increases, negative count increases, negative polarity increases
    elif positive_count_change > 0 and positive_pol_change > 0 and negative_count_change > 0 and negat_pol_change > 0:
        news_bullish, news_bearish = 0, 0

    # Positive count increases, positive polarity decreases, negative count increases, negative polarity increases
    elif positive_count_change > 0 and positive_pol_change < 0 and negative_count_change > 0 and negat_pol_change > 0:
        news_bullish, news_bearish = 0.3, 0.7

    # Positive count decreases, positive polarity increases, negative count increases, negative polarity increases
    elif positive_count_change < 0 and positive_pol_change > 0 and negative_count_change > 0 and negat_pol_change > 0:
        news_bullish, news_bearish = 0.2, 0.8

    # Positive count decreases, positive polarity decreases, negative count increases, negative polarity increases
    elif positive_count_change < 0 and positive_pol_change < 0 and negative_count_change > 0 and negat_pol_change > 0:
        news_bullish, news_bearish = 0, 1

    # Positive count increases, positive polarity increases, negative count decreases, negative polarity increases
    elif positive_count_change > 0 and positive_pol_change > 0 and negative_count_change < 0 and negat_pol_change > 0:
        news_bullish, news_bearish = 0.8, 0.2

    # Positive count increases, positive polarity decreases, negative count decreases, negative polarity increases
    elif positive_count_change > 0 and positive_pol_change < 0 and negative_count_change < 0 and negat_pol_change > 0:
        news_bullish, news_bearish = 0.7, 0.3

    # Positive count decreases, positive polarity increases, negative count decreases, negative polarity increases
    elif positive_count_change < 0 and positive_pol_change > 0 and negative_count_change < 0 and negat_pol_change > 0:
        news_bullish, news_bearish = 0, 0

    # Positive count decreases, positive polarity decreases, negative count decreases, negative polarity increases
    elif positive_count_change < 0 and positive_pol_change < 0 and negative_count_change < 0 and negat_pol_change > 0:
        news_bullish, news_bearish = 0.4, 0.6

    # Positive count increases, positive polarity increases, negative count increases, negative polarity decreases
    elif positive_count_change > 0 and positive_pol_change > 0 and negative_count_change > 0 and negat_pol_change < 0:
        news_bullish, news_bearish = 0.7, 0.3

    # Positive count increases, positive polarity decreases, negative count increases, negative polarity decreases
    elif positive_count_change > 0 and positive_pol_change < 0 and negative_count_change > 0 and negat_pol_change < 0:
        news_bullish, news_bearish = 0.3, 0.7

    # Positive count decreases, positive polarity increases, negative count increases, negative polarity decreases
    elif positive_count_change < 0 and positive_pol_change > 0 and negative_count_change > 0 and negat_pol_change < 0:
        news_bullish, news_bearish = 0, 0

    # Positive count decreases, positive polarity decreases, negative count increases, negative polarity decreases
    elif positive_count_change < 0 and positive_pol_change < 0 and negative_count_change > 0 and negat_pol_change < 0:
        news_bullish, news_bearish = 0.2, 0.8
    else:
        print('here')
        news_bullish, news_bearish = 0, 0

    return news_bullish, news_bearish


if __name__ == '__main__':
    print(calculate_market_sentiment(2, 2, 2, 2,
                                     1, 1, 2, 3))

