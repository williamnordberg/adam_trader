import requests
from textblob import TextBlob
import logging
from typing import Tuple

from z_handy_modules import retry_on_error

SENTIMENT_POSITIVE_THRESHOLD = 0.1
SENTIMENT_NEGATIVE_THRESHOLD = -0.001


@retry_on_error(max_retries=3, delay=5, allowed_exceptions=(Exception,),
                fallback_values=(0.0, 0.0, 0, 0))
def check_news_cryptocompare_sentiment() -> Tuple[float, float, int, int]:

    positive_polarity_score = 0.0
    negative_polarity_score = 0.0
    positive_count = 0
    negative_count = 0

    url = 'https://min-api.cryptocompare.com/data/v2/news/?lang=EN'
    response = requests.get(url)

    # Check if the API request was successful
    if response.status_code == 200:
        # Parse the response JSON
        response_json = response.json()

        # Extract the news articles from the response JSON
        data = response_json['Data']

        for article in data:
            content = article['body']

            try:
                blob = TextBlob(content)
                sentiment_score = blob.sentiment.polarity

                if sentiment_score > SENTIMENT_POSITIVE_THRESHOLD:
                    positive_polarity_score += sentiment_score
                    positive_count += 1
                elif sentiment_score < SENTIMENT_NEGATIVE_THRESHOLD:
                    negative_polarity_score += sentiment_score
                    negative_count += 1

            except Exception as e:
                logging.error(f"Error analyzing content: {e}")
                return 0.0, 0.0, 0, 0
        return positive_polarity_score / positive_count, abs(negative_polarity_score / negative_count), \
            positive_count, negative_count

    else:
        logging.error(f'Error{response.status_code}')
        return 0.0, 0.0, 0, 0


if __name__ == "__main__":
    positive_polarity_score_outer, negative_polarity_score_outer,\
        positive_count_outer, negative_count_outer = check_news_cryptocompare_sentiment()

    logging.info(f'positive_polarity: {positive_polarity_score_outer}'
                 f' and negative_polarity: {negative_polarity_score_outer}')
    logging.info(f'positive_count: {positive_count_outer} '
                 f'negative_count: {negative_count_outer}')
