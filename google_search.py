from typing import List
from pytrends.exceptions import ResponseError
from pytrends.request import TrendReq
import numpy as np
import requests


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
        print("No internet connection available.")
        return False


def check_search_trend(keywords: List[str], threshold: float = 1.2) -> bool:
    """
    Check if there is a significant increase in search volume for a list of keywords in the past 7 days.

    Args:
        keywords (List[str]): The list of keywords to search for.
        threshold (float): The threshold to use for determining if the last hour's search volume is significantly
        higher. Default is 1.2, which means if the last hour's search volume is 20% higher than the expected value,
        it is considered significant.

    Returns:
        bool: True if there is a significant increase in search volume for all keywords, False otherwise.
    """

    # Check for internet connection
    if not check_internet_connection():
        return False

    # Convert all keywords to lowercase
    keywords = [keyword.lower() for keyword in keywords]

    try:
        pytrends = TrendReq(hl='en-US', tz=360)

        pytrends.build_payload(keywords, cat=0, timeframe='now 7-d', geo='', gprop='')

        trend = pytrends.interest_over_time()

        # Calculate the average increase in search volume for all keywords
        search_volume = trend.values
        increase = np.diff(search_volume, axis=0)
        average_increase = np.mean(increase, axis=0)

        # Check if the last hour's search volume is significantly higher for all keywords
        last_hour = trend.iloc[-1].values
        if any(last_hour <= ((search_volume[-2] + average_increase) * threshold)):
            return False

        return True

    except ResponseError as e:
        print(f"An error occurred: {e}")
        return False


