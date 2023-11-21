from typing import List
from pytrends.request import TrendReq as UTrendReq
from pytrends.exceptions import ResponseError
from requests.exceptions import RequestException, ConnectionError, Timeout, TooManyRedirects
from datetime import datetime
import configparser
import os

from z_read_write_csv import save_value_to_database, \
    should_update, save_update_time, retrieve_latest_factor_values_database, read_database
from z_handy_modules import retry_on_error, get_bitcoin_price
from z_compares import compare_google

# Load the config file
config = configparser.ConfigParser()
config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config/config.ini')

with open(config_path, 'r') as f:
    config_string = f.read()

config.read_string(config_string)
headers = {key: config['header'][key] for key in config['header']}


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
    save_update_time('google_search')
    return round(google_bullish, 2)


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
