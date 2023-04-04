from abc import ABC
from typing import List
from pytrends.exceptions import ResponseError
import requests
import logging
from pytrends.request import TrendReq as UTrendReq

GET_METHOD = 'get'
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

headers = {
    'authority': 'ogs.google.com',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'accept-language': 'en-US,en;q=0.9',
    'cookie': 'HSID=AqymjKDgSOMJ1vMwD; SSID=AXzsuZ6JYrbJb3pmn; APISID=Q5RMGGx5W_eBuz5f/AVEhryxIGC1RaxVKk; '
              'SAPISID=KfHQoj6zAoeJrRhN/AZGz-e4rIsEIWn-zq; __Secure-1PAPISID=KfHQoj6zAoeJrRhN/AZGz-e4rIsEIWn-zq; '
              '__Secure-3PAPISID=KfHQoj6zAoeJrRhN/AZGz-e4rIsEIWn-zq; OTZ=6939745_24_24__24_; '
              '__Secure-ENID=10.SE=JzKxg8vqIe3XA3L8AVE6Vm09jpYUapluLI'
              '-kpQofoUxagjKBAqqERYLCkq38zb0klsJUqWDe_tMZROp9tKkmf'
              '-bdEJ6_IuPO3KL1yosV5AXh5gbrgcgi9vBIYqHqb31L1S8YL41cCl6khD_4XCjTjW9ZWGl2GpHUXuolBxHGIykZK3q4jmmR4MxxzZTAJDi0qy2FCUrrh75C3yFBwGrxiBy8IvI1TyJVy32C8XBj91yaNNax3Ee5UUM1MLOCC28; SID=UQhiy40z7t2NhHM1Tr6UniEB2LvmMi-jUpkRvgTJk8BgUlAc00dpxOSKR6Lo_HRlvbsazg.; __Secure-1PSID=UQhiy40z7t2NhHM1Tr6UniEB2LvmMi-jUpkRvgTJk8BgUlAcQO8pudJIJ5UZg1yCC9cYDA.; __Secure-3PSID=UQhiy40z7t2NhHM1Tr6UniEB2LvmMi-jUpkRvgTJk8BgUlAcKd-UKPPF35ymeX68Y5-DYQ.; AEC=ARSKqsJAD0RYX5-ggzgPAFUm7wkTASa0sFmRIZN4ZCmaBFblt0hybhUfRII; NID=511=NzwgWD41u6HoiCqNuP6-icjT7OfMFPjuco0hWDvGgDZMBvKzHUaormjRv_bAeCxaa0OVOp7v2Q5nCjYJF0_51UR1_DjkHHgx-8Xs_p6_EMupwpXdaaZo71UAxP44371Uu-fc11zJKFZAeaAsWu-hB75kqXp5kTN9vKV6Y8NDFQVyCymlb50vdY9R5BHGTPzl51rUtZd4OAu2oOPPBey3zMBq8cp8fbHEToAEFXZ0DXhRmpo0vgG45AMGHikrAW8NovwRizDD5TjAsx8v1_kdHl8lbkIww4bLdcocdFD3rNkmV3LtGqkA_7NxPA; 1P_JAR=2023-03-20-03; SEARCH_SAMESITE=CgQI7JcB; SIDCC=AFvIBn97Z5tqN1lOcWMfnnQTL6eYY9mf3PJto5W-CI0WYhF2_AUiXKcU14i3vrklMaEZhnQRJdZj; __Secure-1PSIDCC=AFvIBn-IRyl5VIEsBO4EPxaUcHTrFbevt10xjF1V7XCa8EO4qchX1-Li_cb1sLrUbY1b8PtojyEm; __Secure-3PSIDCC=AFvIBn8WyGqiNET2Y6s8FXDRGpkKzeIK7y8xMqpkav1j-XQnRqy7UZRyvttdLDRDZx5bKjgJ8EGE',
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


class TrendReq(UTrendReq, ABC):
    def _get_data(self, url, method=GET_METHOD, trim_chars=0, **kwargs):
        return super()._get_data(url, method=GET_METHOD, trim_chars=trim_chars, headers=headers, **kwargs)


def check_internet_connection() -> bool:
    """
    Check if there is an internet connection.

    Returns:
        bool: True if there is an internet connection, False otherwise.
    """
    try:
        requests.get("http://www.google.com", timeout=3)
        return True
    except requests.ConnectionError:
        logging.warning("No internet connection available.")
        return False


def check_search_trend(keywords: List[str]):
    """
    Check if there is a significant increase in search volume for a list of keywords in the past 7 days.

    Args:
        keywords (List[str]): The list of keywords to search for.

    Returns:
        news_bullish: a value between 0 (the lowest probability) and 1 (highest probability).
        news_bearish: a value between 0 (the lowest probability) and 1 (highest probability).
    """

    # Check for internet connection
    if not check_internet_connection():
        logging.info('unable to get google trend')
        return 0, 0

    # Convert all keywords to lowercase
    keywords = [keyword.lower() for keyword in keywords]

    try:
        pytrends = TrendReq(hl='en-US', tz=360, requests_args={'headers': headers})

        pytrends.build_payload(keywords, cat=0, timeframe='now 7-d', geo='', gprop='')

        trend = pytrends.interest_over_time()

        # Check if the last hour's search volume is significantly higher for all keywords
        last_hour = int(trend.iloc[-1].values[0])
        two_hours_before = int(trend.iloc[-2].values[0])
        # Check the threshold number of increase in the search
        if last_hour >= two_hours_before:
            if last_hour >= (two_hours_before * 1.8):
                return 1, 0
            elif last_hour >= (two_hours_before * 1.6):
                return 0.85, 0.15
            elif last_hour >= (two_hours_before * 1.35):
                return 0.75, 0.25
            elif last_hour >= (two_hours_before * 1.2):
                return 0.6, 0.4
            return 0, 0

        elif last_hour <= two_hours_before:
            if two_hours_before >= (last_hour * 1.8):
                return 0, 11
            elif two_hours_before >= (last_hour * 1.6):
                return 0.15, 0.85
            elif two_hours_before >= (last_hour * 1.35):
                return 0.25, 0.75
            elif two_hours_before >= (last_hour * 1.2):
                return 0.84, 0.16
            return 0, 0

    except ResponseError as e:
        logging.error(f"An error occurred: {e}")
        return 0, 0


if __name__ == "__main__":
    google_bullish, google_bearish = check_search_trend(["Bitcoin"])
    logging.info(f'google_bullish: {google_bullish}   google_bearish:{google_bearish}')
