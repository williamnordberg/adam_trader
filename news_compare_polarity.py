from typing import Tuple


def compare_polarity(positive_polarity_24_hours_before: float, latest_positive_polarity_score: float,
                     negative_polarity_24_hours_before: float, latest_negative_polarity_score: float) -> Tuple[float, float]:
    positive_percentage_increase = (positive_polarity_24_hours_before - latest_positive_polarity_score
                                    ) / latest_positive_polarity_score * 100
    negative_percentage_increase = (negative_polarity_24_hours_before - latest_negative_polarity_score
                                    ) / latest_negative_polarity_score * 100

    if positive_percentage_increase > negative_percentage_increase:
        if positive_percentage_increase >= 50:
            return 1, 0
        elif positive_percentage_increase >= 40:
            return 0.9, 0.1
        elif positive_percentage_increase >= 30:
            return 0.8, 0.2
        elif positive_percentage_increase >= 20:
            return 0.7, 0.3
        elif positive_percentage_increase >= 10:
            return 0.6, 0.4

    elif positive_percentage_increase < negative_percentage_increase:
        if negative_percentage_increase >= 50:
            return 0, 1
        elif negative_percentage_increase >= 40:
            return 0.1, 0.9
        elif negative_percentage_increase >= 30:
            return 0.2, 0.8
        elif negative_percentage_increase >= 20:
            return 0.3, 0.7
        elif negative_percentage_increase >= 10:
            return 0.4, 0.6

    return 0, 0


if __name__ == '__main__':
    positive_polarity_24_hours_before_outer, latest_positive_polarity_score_outer, \
        negative_polarity_24_hours_before_outer, latest_negative_polarity_score_outer = \
        0.3868055555555555, 0.27497351851851853, -0.10, -0.01
    x, y = compare_polarity(positive_polarity_24_hours_before_outer, latest_positive_polarity_score_outer,
                            negative_polarity_24_hours_before_outer, latest_negative_polarity_score_outer)
    print(f'bullish: {x}, bearish: {y}')
