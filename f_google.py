from typing import List
from pytrends.request import TrendReq as UTrendReq
from pytrends.exceptions import ResponseError
from requests.exceptions import RequestException, ConnectionError, Timeout, TooManyRedirects
from datetime import datetime

from z_read_write_csv import save_value_to_database, \
    should_update, save_update_time, retrieve_latest_factor_values_database, read_database
from z_handy_modules import retry_on_error, get_bitcoin_price
from z_compares import compare_google

headers = {
    'authority': 'ogs.google.com',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'accept-language': 'en-US,en;q=0.9',
    'cookie': 'HSID=AqymjKDgSOMJ1vMwD; SSID=AXzsuZ6JYrbJb3pmn; APISID=Q5RMGGx5W_eBuz5f/AVEhryxIGC1RaxVKk; '
              'SAPISID=KfHQoj6zAoeJrRhN/AZGz-e4rIsEIWn-zq; __Secure-1PAPISID=KfHQoj6zAoeJrRhN/AZGz-e4rIsEIWn-zq; '
              '__Secure-3PAPISID=KfHQoj6zAoeJrRhN/AZGz-e4rIsEIWn-zq; OTZ=6939745_24_24__24_; '
              '__Secure-ENID=10.SE=JzKxg8vqIe3XA3L8AVE6Vm09jpYUapluLI'
              '-kpQofoUxagjKBAqqERYLCkq38zb0klsJUqWDe_tMZROp9tKkmf'
              '-bdEJ6_IuPO3KL1yosV5AXh5gbrgcgi9vBIYqHqb31L1S8YL41cCl6khD_4XCjTjW9ZWGl2GpHUXuolBxHGIykZK3q4'
              'jmmR4MxxzZTAJDi0qy2FCUrrh75C3yFBwGrxiBy8IvI1TyJVy32C8XBj91yaNNax3Ee5UUM1MLOCC28; SID=UQhiy4'
              '0z7t2NhHM1Tr6UniEB2LvmMi-jUpkRvgTJk8BgUlAc00dpxOSKR6Lo_HRlvbsazg.; __Secure-1PSID=UQhiy40z7t'
              '2NhHM1Tr6UniEB2LvmMi-jUpkRvgTJk8BgUlAcQO8pudJIJ5UZg1yCC9cYDA.; __Secure-3PSID=UQhiy40z7t2NhHM1'
              'Tr6UniEB2LvmMi-jUpkRvgTJk8BgUlAcKd-UKPPF35ymeX68Y5-DYQ.; AEC=ARSKqsJAD0RYX5-ggzgPAFUm7wkTASa0sF'
              'mRIZN4ZCmaBFblt0hybhUfRII; NID=511=NzwgWD41u6HoiCqNuP6-icjT7OfMFPjuco0hWDvGgDZMBvKzHUaormjRv_'
              'bAeCxaa0OVOp7v2Q5nCjYJF0_51UR1_DjkHHgx-8Xs_p6_EMupwpXdaaZo71UAxP44371Uu-fc11zJKFZAeaAsWu-hB75'
              'kqXp5kTN9vKV6Y8NDFQVyCymlb50vdY9R5BHGTPzl51rUtZd4OAu2oOPPBey3zMBq8cp8fbHEToAEFXZ0DXhRmpo0vgG4'
              '5AMGHikrAW8NovwRizDD5TjAsx8v1_kdHl8lbkIww4bLdcocdFD3rNkmV3LtGqkA_7NxPA; 1P_JAR=2023-03-20-03;'
              ' SEARCH_SAMESITE=CgQI7JcB; SIDCC=AFvIBn97Z5tqN1lOcWMfnnQTL6eYY9mf3PJto5W-CI0WYhF2_AUiXKcU14i3'
              'vrklMaEZhnQRJdZj; __Secure-1PSIDCC=AFvIBn-IRyl5VIEsBO4EPxaUcHTrFbevt10xjF1V7XCa8EO4qchX1-Li_c'
              'b1sLrUbY1b8PtojyEm; __Secure-3PSIDCC=AFvIBn8WyGqiNET2Y6s8FXDRGpkKzeIK7y8xMqpkav1j-XQnRqy7UZRy'
              'vttdLDRDZx5bKjgJ8EGE',
    'referer': 'https://trends.google.com/',
    'sec-ch-ua': '"Brave";v="111", "Not(A:Brand";v="8", "Chromium";v="111"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'iframe',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-site',
    'sec-gpc': '1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 '
                  'Safari/537.36',
}


class TrendReq(UTrendReq):
    def _get_data(self, url, method='get', trim_chars=0, **kwargs):
        return super()._get_data(url, method=method, trim_chars=trim_chars, headers=headers, **kwargs)


def consider_market_sentiment(google_search_trend: float) -> float:
    current_price = get_bitcoin_price()
    df = read_database()
    price_24_hours_ago = df['bitcoin_price'].iloc[-24]
    news_sentiment = df['news_bullish'].iloc[-1]
    youtube = df['youtube_bullish'].iloc[-1]
    reddit = df['reddit_bullish'].iloc[-1]

    price_change_percent = ((current_price - price_24_hours_ago) / price_24_hours_ago) * 100

    # check price change to a value between 0 and 1
    price_trend = 0.5 if (-2 < price_change_percent < 2) else max(min((price_change_percent + 7) / 14, 1), 0)

    # Combine the other factors using their mean
    combined_factors = (news_sentiment + youtube + reddit + price_trend) / 4

    # Use the combined factors to influence the Google search trend
    if google_search_trend == 0.5:
        return 0.5
    elif combined_factors > 0.5:
        final_score = (google_search_trend + combined_factors) / 2
    elif combined_factors < 0.5 < google_search_trend:
        final_score = combined_factors * (1 - google_search_trend)
    else:  # combined_factors < 0.5 and google_search_trend < 0.5
        final_score = (combined_factors + google_search_trend) / 2

    # Ensure the final score is in the range [0, 1]
    final_score = min(max(final_score, 0), 1)
    return final_score


@retry_on_error(max_retries=3, delay=5, allowed_exceptions=(
        ResponseError, RequestException, ConnectionError, Timeout,
        TooManyRedirects), fallback_values=0.5)
def check_search_trend_wrapper(keywords: List[str]) -> float:
    """
    Check if there is a significant increase in search volume for a list of keywords in the past 1 hour.

    Args:
        keywords (List[str]): The list of keywords to search for.

    Returns:
        bullish_score: a value between 0 (the lowest probability) and 1 (highest probability).
    """
    # it will be here until google trend server recover
    save_update_time('google_search')
    keywords = [keyword.lower() for keyword in keywords]

    pytrends = TrendReq(hl='en-US', tz=360, requests_args={'headers': headers})
    pytrends.build_payload(keywords, cat=0, timeframe='now 7-d', geo='', gprop='')

    trend = pytrends.interest_over_time()
    isPartial = trend.iloc[-1].values[1]

    # if isPartial is True then last hour is not complete, so we project that
    if isPartial:
        current_minute = datetime.utcnow().minute
        if current_minute >= 30:
            last_hour, two_hours_before = trend.iloc[-1].values[0], trend.iloc[-2].values[0]
            last_hour = last_hour * (60 / current_minute)
        else:
            last_hour, two_hours_before = trend.iloc[-2].values[0], trend.iloc[-3].values[0]
    else:
        last_hour, two_hours_before = trend.iloc[-1].values[0], trend.iloc[-2].values[0]

    google_bullish = compare_google(last_hour, two_hours_before)

    # Here we consider the market sentiment
    google_bullish = consider_market_sentiment(google_bullish)

    save_value_to_database('hourly_google_search', last_hour)
    return google_bullish


def check_search_trend(keywords: List[str]) -> float:
    if should_update('google_search'):
        google_bullish = check_search_trend_wrapper(keywords)
        save_value_to_database('google_search_bullish', round(google_bullish, 2))
        return google_bullish
    else:
        return retrieve_latest_factor_values_database('google_search')


if __name__ == "__main__":
    bullish_score_outer = check_search_trend_wrapper(["Bitcoin"])
    print(f'google_bullish: {bullish_score_outer}')
