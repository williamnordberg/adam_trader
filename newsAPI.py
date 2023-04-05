import requests
import json
import configparser
from textblob import TextBlob
import logging
import os
import datetime

SENTIMENT_POSITIVE_THRESHOLD = 0.1
SENTIMENT_NEGATIVE_THRESHOLD = -0.001

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load the config file
config = configparser.ConfigParser()
config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.ini")
config.read(config_path)
API_NEWSAPI = config.get("API", "Newsapi")


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


def check_news_api_sentiment(start, end):
    # Check for internet connection
    if not check_internet_connection():
        logging.info('unable to get news sentiment')
        return 0, 0, 0, 0

    start_date = start.strftime('%Y-%m-%d')

    end_date = end.strftime('%Y-%m-%d')

    endpoint = 'https://newsapi.org/v2/everything'
    params = {
        'q': 'bitcoin',
        'language': 'en',
        'sortBy': 'publishedAt',
        'apiKey': API_NEWSAPI,
        'from': start_date,
        'to': end_date
    }
    positive_polarity_score = 0.0
    positive_count = 0
    negative_polarity_score = 0.0
    negative_count: int = 0

    try:
        response = requests.get(endpoint, params=params)
        response.raise_for_status()
        data = json.loads(response.text)

        for article in data['articles']:
            content = article['content']

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

        return positive_polarity_score / positive_count, negative_polarity_score / negative_count, \
            positive_count, negative_count

    except requests.exceptions.RequestException as e:
        logging.error(f'Error occurred: {e}')
        return 0, 0, 0, 0
    except json.JSONDecodeError as e:
        logging.error(f'Error decoding JSON response: {e}')
        return 0, 0, 0, 0


if __name__ == "__main__":
    start_outer = datetime.datetime.now() - datetime.timedelta(days=1)
    end_outer = datetime.datetime.now()

    positive_polarity_score_outer, negative_polarity_score_outer, \
        positive_count_outer, negative_count_outer = check_news_api_sentiment(start_outer, end_outer)

    logging.info(f'positive_polarity: {positive_polarity_score_outer/positive_count_outer}'
                 f'and negative_polarity: {negative_polarity_score_outer/negative_count_outer}')
    logging.info(f'positive_count: {positive_count_outer} '
                 f'negative_count: {negative_count_outer}')
