from typing import Tuple


def compare_interest_rate(rate_this_month:  float, rate_month_before: float) -> Tuple[float, float]:

    rate_decrease = rate_month_before - rate_this_month

    if rate_decrease > 0:
        if rate_decrease >= 0.75:
            return 1, 0
        elif rate_decrease >= 0.5:
            return 0.85, 0.15
        elif rate_decrease >= 0.25:
            return 0.7, 0.3
        elif rate_decrease >= 0:
            return 0.6, 0.4

    elif rate_decrease <= 0:
        if rate_decrease <= 0.75:
            return 0, 1
        elif rate_decrease <= 0.5:
            return 0.15, 0.85
        elif rate_decrease <= 0.25:
            return 0.3, 0.7
        elif rate_decrease <= 0:
            return 0.4, 0.6

    return 0, 0


def compare_cpi_m_to_m(cpi_m_to_m: float) -> Tuple[float,  float]:

    if cpi_m_to_m <= 0:
        if cpi_m_to_m <= -0.75:
            return 1, 0
        elif cpi_m_to_m <= 0.5:
            return 0.85, 0.15
        elif cpi_m_to_m <= 0.25:
            return 0.7, 0.3
        else:
            return 0.6, 0.4

    elif cpi_m_to_m > 0:
        if cpi_m_to_m >= 0.75:
            return 0, 1
        elif cpi_m_to_m >= 0.5:
            return 0.15, 0.85
        elif cpi_m_to_m >= 0.25:
            return 0.3, 0.7

    return 0, 0


def compare_ppi_m_to_m(ppi_m_to_m: float) -> Tuple[float, float]:

    if ppi_m_to_m <= 0:
        if ppi_m_to_m <= -0.75:
            return 1, 0
        elif ppi_m_to_m <= -0.5:
            return 0.85, 0.15
        elif ppi_m_to_m <= - 0.25:
            return 0.7, 0.3
        else:
            return 0.6, 0.4

    elif ppi_m_to_m > 0:
        if ppi_m_to_m >= 0.75:
            return 0, 1
        elif ppi_m_to_m >= 0.5:
            return 0.15, 0.85
        elif ppi_m_to_m >= 0.25:
            return 0.3, 0.7

    return 0, 0


def calculate_macro_sentiment(rate_this_month: float, rate_month_before: float,
                              cpi_m_to_m: float, ppi_m_to_m: float) -> Tuple[float, float]:
    print(cpi_m_to_m, ppi_m_to_m)

    if rate_this_month and rate_month_before:
        rate_bullish, rate_bearish = compare_interest_rate(rate_this_month, rate_month_before)
    else:
        rate_bullish, rate_bearish = 0, 0

    if cpi_m_to_m:
        cpi_bullish, cpi_bearish = compare_cpi_m_to_m(cpi_m_to_m)
    else:
        cpi_bullish, cpi_bearish = 0, 0

    if ppi_m_to_m:
        ppi_bullish, ppi_bearish = compare_ppi_m_to_m(ppi_m_to_m)
    else:
        ppi_bullish, ppi_bearish = 0, 0

    weights = {
        "interest_rate": 0.5,
        "cpi": 0.25,
        "ppi": 0.25,
    }

    # Calculate the weighted score for each alternative:
    weighted_score_up = (
            weights["interest_rate"] * rate_bullish +
            weights["cpi"] * cpi_bullish +
            weights["ppi"] * ppi_bullish
    )

    weighted_score_down = (
            weights["interest_rate"] * rate_bearish +
            weights["cpi"] * cpi_bearish +
            weights["ppi"] * ppi_bearish
    )

    total_score = weighted_score_up + weighted_score_down

    # Normalize the scores
    if total_score == 0:
        normalized_score_up, normalized_score_down = 0, 0
    else:
        normalized_score_up = weighted_score_up / total_score
        normalized_score_down = weighted_score_down / total_score

    return normalized_score_up, normalized_score_down
