from typing import Tuple, Optional
import pandas as pd
from compares import compare_macro_m_to_m

LATEST_INFO_SAVED = 'data/latest_info_saved.csv'


def calculate_macro_sentiment(rate_this_month: Optional[float], rate_month_before: Optional[float],
                              cpi_m_to_m: Optional[float], ppi_m_to_m: Optional[float]) -> Tuple[float, float]:

    latest_info_saved = pd.read_csv(LATEST_INFO_SAVED).squeeze("columns")

    if rate_this_month and rate_month_before:
        rate_m_to_m = float(rate_this_month - rate_month_before)
        rate_bullish, rate_bearish = compare_macro_m_to_m(rate_m_to_m)
        latest_info_saved.loc[0, 'rate_bullish'] = rate_bullish
        latest_info_saved.loc[0, 'rate_bearish'] = rate_bearish
        latest_info_saved.loc[0, 'fed_rate_m_to_m'] = float(rate_this_month - rate_this_month)
    else:
        rate_bullish = float(latest_info_saved['rate_bullish'][0])
        rate_bearish = float(latest_info_saved['rate_bearish'][0])

    if cpi_m_to_m:
        cpi_bullish, cpi_bearish = compare_macro_m_to_m(cpi_m_to_m)
        latest_info_saved.loc[0, 'cpi_bullish'] = cpi_bullish
        latest_info_saved.loc[0, 'cpi_bearish'] = cpi_bearish
        latest_info_saved.loc[0, 'cpi_m_to_m'] = cpi_m_to_m

    else:
        cpi_bullish = float(latest_info_saved['cpi_bullish'][0])
        cpi_bearish = float(latest_info_saved['cpi_bearish'][0])

    if ppi_m_to_m:
        ppi_bullish, ppi_bearish = compare_macro_m_to_m(ppi_m_to_m)
        latest_info_saved.loc[0, 'ppi_bullish'] = ppi_bullish
        latest_info_saved.loc[0, 'ppi_bearish'] = ppi_bearish
        latest_info_saved.loc[0, 'ppi_m_to_m'] = ppi_m_to_m

    else:
        ppi_bullish = float(latest_info_saved['ppi_bullish'][0])
        ppi_bearish = float(latest_info_saved['ppi_bearish'][0])

    # Save the CSV
    latest_info_saved.to_csv(LATEST_INFO_SAVED, index=False)

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
        normalized_score_up, normalized_score_down = 0.0, 0.0
    else:
        normalized_score_up = weighted_score_up / total_score
        normalized_score_down = weighted_score_down / total_score

    return round(normalized_score_up, 2), round(normalized_score_down, 2)


if __name__ == "__main__":
    print('calculate_macro_sentiment:', calculate_macro_sentiment(0, 0, 0, 0))