import requests
import json
import configparser
from textblob import TextBlob
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

SENTIMENT_THRESHOLD = 0.15

# Load the config file
config = configparser.ConfigParser()
config.read('config.ini')
API_NEWSAPI = config.get('API', 'Newsapi')


def check_sentiment_of_news():
    """
    Check the sentiment of news articles related to cryptocurrencies.

    Return: True if the sentiment is positive, False otherwise
    """
    endpoint = 'https://newsapi.org/v2/everything'
    params = {
        'q': 'cryptocurrency OR bitcoin OR blockchain',
        'language': 'en',
        'sortBy': 'publishedAt',
        'apiKey': API_NEWSAPI
    }

    positive_count = 0
    negative_count = 0

    try:
        response = requests.get(endpoint, params=params)
        response.raise_for_status()
        data = json.loads(response.text)

        for article in data['articles']:
            content = article['content']

            try:
                blob = TextBlob(content)
                sentiment_score = blob.sentiment.polarity

                if sentiment_score > SENTIMENT_THRESHOLD:
                    positive_count += 1
                elif sentiment_score < -SENTIMENT_THRESHOLD:
                    negative_count += 1
            except Exception as e:
                logging.error(f"Error analyzing content: {e}")

        if positive_count >= 1.8 * negative_count:
            return True
        else:
            return False

    except requests.exceptions.RequestException as e:
        logging.error(f'Error occurred: {e}')
        return False
    except json.JSONDecodeError as e:
        logging.error(f'Error decoding JSON response: {e}')
        return False


if __name__ == "__main__":
    API_KEY = API_NEWSAPI
    sentiment_positive = check_sentiment_of_news()
    logging.info(f'sentiment_positive: {sentiment_positive}')
