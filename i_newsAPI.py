import requests
import json
import configparser
from textblob import TextBlob
import os
from datetime import datetime, timedelta
from typing import Tuple

from z_handy_modules import retry_on_error

SENTIMENT_POSITIVE_THRESHOLD = 0.1
SENTIMENT_NEGATIVE_THRESHOLD = -0.001

# Load the config file
config = configparser.ConfigParser()
config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config/config.ini")
config.read(config_path)
API_NEWSAPI = config.get("API", "Newsapi")


@retry_on_error(3, 5, (Exception, requests.exceptions.RequestException, json.JSONDecodeError),
                fallback_values=(0.0, 0.0, 0, 0))
def check_news_api_sentiment() -> Tuple[float, float, int, int]:
    """
        Check the sentiment of news articles about Bitcoin within the specified date range.

        :return: A tuple containing the average positive polarity,
         average negative polarity, positive count, and negative count.
        """
    start = datetime.now() - timedelta(days=1)
    end = datetime.now()

    start_date = start.strftime('%Y-%m-%d')
    end_date = end.strftime('%Y-%m-%d')

    endpoint = 'https://newsapi.org/v2/everything'
    params = {
        'q': '(bitcoin OR cryptocurrency)',
        'language': 'en',
        'sortBy': 'publishedAt',
        'apiKey': API_NEWSAPI,
        'from': start_date,
        'to': end_date
    }
    positive_polarity_score = 0.0
    negative_polarity_score = 0.0
    positive_count = 0
    negative_count = 0

    response = requests.get(endpoint, params=params)
    data = json.loads(response.text)
    for article in data['articles']:
        print(article)
        content = article['content']

        blob = TextBlob(content)
        sentiment_score = blob.sentiment.polarity
        print('sentiment_score:', sentiment_score)
        if sentiment_score > SENTIMENT_POSITIVE_THRESHOLD:
            positive_polarity_score += sentiment_score
            positive_count += 1
        elif sentiment_score < SENTIMENT_NEGATIVE_THRESHOLD:
            negative_polarity_score += sentiment_score
            negative_count += 1

        # Handle division by zero cases
    avg_positive_polarity = positive_polarity_score / positive_count if positive_count > 0 else 0
    avg_negative_polarity = negative_polarity_score / negative_count if negative_count > 0 else 0

    return avg_positive_polarity, abs(avg_negative_polarity), positive_count, negative_count


if __name__ == "__main__":
    start_outer = datetime.now() - timedelta(days=1)
    end_outer = datetime.now()
    positive_polarity_score_outer, negative_polarity_score_outer, \
        positive_count_outer, negative_count_outer = check_news_api_sentiment()
    print(f'positive_polarity: {positive_polarity_score_outer} '
          f'and negative_polarity: {negative_polarity_score_outer}')
    print(f'positive_count: {positive_count_outer} '
          f'negative_count: {negative_count_outer}')
