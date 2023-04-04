def compare_polarity(positive_polarity_24_hours_before, latest_positive_polarity_score,
                     negative_polarity_24_hours_before, latest_negative_polarity_score):
    positive_percentage_increase = (positive_polarity_24_hours_before - latest_positive_polarity_score
                                    ) / latest_positive_polarity_score * 100
    negative_percentage_increase = (negative_polarity_24_hours_before - latest_negative_polarity_score
                                    ) / latest_negative_polarity_score * 100

    if positive_percentage_increase > negative_percentage_increase:
        if positive_polarity_24_hours_before >= 1.1 * latest_positive_polarity_score:
            return 0.6, 0.4
        elif positive_polarity_24_hours_before >= 1.2 * latest_positive_polarity_score:
            return 0.7, 0.3
        elif positive_polarity_24_hours_before >= 1.3 * latest_positive_polarity_score:
            return 0.8, 0.2
        elif positive_polarity_24_hours_before >= 1.4 * latest_positive_polarity_score:
            return 0.9, 0.1
        elif positive_polarity_24_hours_before >= 1.5 * latest_positive_polarity_score:
            return 1, 0
    elif positive_percentage_increase < negative_percentage_increase:
        if negative_polarity_24_hours_before >= 1.1 * latest_negative_polarity_score:
            return 0.4, 0.6
        elif negative_polarity_24_hours_before >= 1.2 * latest_negative_polarity_score:
            return 0.3, 0.7
        elif negative_polarity_24_hours_before >= 1.3 * latest_negative_polarity_score:
            return 0.2, 0.8
        elif negative_polarity_24_hours_before >= 1.4 * latest_negative_polarity_score:
            return 0.1, 0.9
        elif negative_polarity_24_hours_before >= 1.5 * latest_negative_polarity_score:
            return 0, 1
    elif positive_percentage_increase == negative_percentage_increase:
        return 0, 0
