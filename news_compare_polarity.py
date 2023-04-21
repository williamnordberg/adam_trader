from typing import Tuple


def compare_polarity(last_24_hours_positive_polarity: float, saved_positive_polarity: float,
                     last_24_hours_negative_polarity: float, saved_negative_polarity: float)\
        -> Tuple[float, float]:
    positive_percentage_increase = (last_24_hours_positive_polarity - saved_positive_polarity
                                    ) / saved_positive_polarity * 100
    print('positive_percentage_increase', positive_percentage_increase)
    negative_percentage_increase = (last_24_hours_negative_polarity - saved_negative_polarity
                                    ) / saved_negative_polarity * 100
    print('negative_percentage_increase', negative_percentage_increase)

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
    # last_24_hours_positive_polarity, saved_positive_polarity,
    # last_24_hours_negative_polarity, saved_negative_polarity
    x, y = compare_polarity(2, 1, 2, 2)
    print(f'bullish: {x}, bearish: {y}')
