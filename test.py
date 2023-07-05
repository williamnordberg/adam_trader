import logging
from typing import List, Tuple
from pytrends.request import TrendReq as UTrendReq
from pytrends.exceptions import ResponseError
from requests.exceptions import RequestException, ConnectionError, Timeout, TooManyRedirects


from z_read_write_csv import save_value_to_database, \
    should_update, save_update_time, retrieve_latest_factor_values_database
from z_handy_modules import retry_on_error
from z_compares import compare_google_reddit_youtube

headers = {
    'authority': 'trends.google.com',
    'accept': 'application/json, text/plain, /',
    'accept-language': 'en-US,en;q=0.5',
    'cookie': 'HSID=AdcKfk_1mAM433GfE; SSID=AsxV9rh2FIY9PJmZQ; APISID=4_3quztPi8mrmBJx/ArmLIYnAU1nekqQzH; SAPISID=2lIiX6Tj2Nt6g51d/AmmZuyJ6wWkCH_oHV; _Secure-1PAPISID=2lIiX6Tj2Nt6g51d/AmmZuyJ6wWkCH_oHV; __Secure-3PAPISID=2lIiX6Tj2Nt6g51d/AmmZuyJ6wWkCH_oHV; SEARCH_SAMESITE=CgQIuJgB; SID=XQgKWDtvzBiMaRI7RA56arPOvH3qh60ElvI71tJ3df8ep7IlwNkVTHJlzE_osgeTMu-afA.; __Secure-1PSID=XQgKWDtvzBiMaRI7RA56arPOvH3qh60ElvI71tJ3df8ep7IlI1U72Lb4_fdJ5B3ZU77PCA.; __Secure-3PSID=XQgKWDtvzBiMaRI7RA56arPOvH3qh60ElvI71tJ3df8ep7IlE2_3IcYkgTIUX-QYrEMuhw.; AEC=Ad49MVEPzYv0WqBnoX2jLu-mAZ5CNCQA5BmKPz2DCKN7_W31p5OT7Y6iOw; 1P_JAR=2023-07-05-03; NID=511=sAEXqat3gVlSDxKF_M-vUFYRkVf1kxoXNG8O6SZuKi3v2E4aStabDaSzxLYZRjlvVAIH7TmxxIqS8mhd7FC9xmh755AHz9MCXcoQ50LlmohkGo3UFEDXCV2ZaVQrTC-tMbFfUG96z89X5rityw1i35g8x7ieWre_4y3ortAZbtqWLS_9lyKNHI9B7v5bWNjaQOipQKVYEkNauEOosBMAFkR29fAjH38n2RSQV3TlEDMmk6tRLHZUg73ght1UsnfFjjvufZqbRqj1-lM0pi-oQDew9xBc7_YIBlpI2-DrLfxdnBYAeYFewxONuB3InGJV_8l48dw; __Secure-1PSIDTS=sidts-CjIBPu3jIdWwFkOY44BZ9SMOoFWuihPBhHNHG02vLRyS3Awn27tC-ndL4Ajqa1nP4PxTwxAA; __Secure-3PSIDTS=sidts-CjIBPu3jIdWwFkOY44BZ9SMOoFWuihPBhHNHG02vLRyS3Awn27tC-ndL4Ajqa1nP4PxTwxAA; OTZ=7103723_24_2424; SIDCC=AP8dLtzivtzJ0Rw_VyCppkP2N4Rt0xU79XiH6pJSaUclTnEaFYrDT6xgI6Rtxf9D9YHc8G3d3EQ; __Secure-1PSIDCC=AP8dLtxWRYXXDYdFaob_hsK1Kqpxd6kg4udc51-7h0CrfDSOqOb9_Q_X2jYyES1IQccgDGfrZqY; __Secure-3PSIDCC=AP8dLtyvqSyYPdwiZJ1uvZ9N0bfelUnSovHr_hujMnFirEwBtTaGYnJ3tT9FJs3bNP40U9sdUh21',
    'referer': 'https://trends.google.com/trends/explore?date=now%207-d&q=Fourth%20of%20july&hl=en',
    'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Brave";v="114"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-model': '""',
    'sec-ch-ua-platform': '"macOS"',
    'sec-ch-ua-platform-version': '"13.0.0"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'sec-gpc': '1',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
}

class TrendReq(UTrendReq):
    def _get_data(self, url, method='get', trim_chars=0, **kwargs):
        return super()._get_data(url, method=method, trim_chars=trim_chars, headers=headers, **kwargs)


@retry_on_error(max_retries=3, delay=5, allowed_exceptions=(
        ResponseError, RequestException, ConnectionError, Timeout,
        TooManyRedirects), fallback_values=(0.0, 0.0))
def check_search_trend_wrapper(keywords: List[str]) -> Tuple[float, float]:
    """
    Check if there is a significant increase in search volume for a list of keywords in the past 1 hour.

    Args:
        keywords (List[str]): The list of keywords to search for.

    Returns:
        bullish_score: a value between 0 (the lowest probability) and 1 (highest probability).
        bearish_score: a value between 0 (the lowest probability) and 1 (highest probability).
    """

    keywords = [keyword.lower() for keyword in keywords]

    pytrends = TrendReq(hl='en-US', tz=360, requests_args={'headers': headers})
    pytrends.build_payload(keywords, cat=0, timeframe='now 7-d', geo='', gprop='')

    trend = pytrends.interest_over_time()
    print('trend', trend)
    last_hour, two_hours_before = trend.iloc[-1].values[0], trend.iloc[-2].values[0]
    print('last_hour, two_hours_before', last_hour, two_hours_before)
    google_bullish,  google_bearish = compare_google_reddit_youtube(last_hour, two_hours_before)

    save_value_to_database('hourly_google_search', last_hour)
    save_update_time('google_search')

    return google_bullish,  google_bearish


def check_search_trend(keywords: List[str]) -> Tuple[float, float]:
    if should_update('google_search'):
        google_bullish, google_bearish = check_search_trend_wrapper(keywords)
        save_value_to_database('google_search_bullish', google_bullish)
        save_value_to_database('google_search_bearish', google_bearish)
        return google_bullish, google_bearish
    else:
        return retrieve_latest_factor_values_database('google_search')


if __name__ == "__main__":
    bullish_score_outer, bearish_score_outer = check_search_trend_wrapper(["Bitcoin"])
    logging.info(f'google_bullish: {bullish_score_outer}   google_bearish:{bearish_score_outer}')
