import requests
from textblob import TextBlob
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

SENTIMENT_THRESHOLD = 0.1
POSITIVITY_PERCENT = 1.8

SENTIMENT_POSITIVE_THRESHOLD = 0.1
SENTIMENT_NEGATIVE_THRESHOLD = -0.001


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


def check_news_cryptocompare_sentiment():

    positive_polarity_score = 0.0
    positive_count = 0
    negative_polarity_score = 0.0
    negative_count = 0

    # Check for internet connection
    if not check_internet_connection():
        logging.info('unable to get news sentiment')
        return 0, 0, 0, 0

    url = 'https://min-api.cryptocompare.com/data/v2/news/?lang=EN'
    response = requests.get(url)

    # Check if the API request was successful
    if response.status_code == 200:
        # Parse the response JSON
        response_json = response.json()

        # Extract the news articles from the response JSON
        data = response_json['Data']

        # Print the titles of the news articles
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
                return 0, 0, 0, 0
        return positive_polarity_score / positive_count, negative_polarity_score / negative_count, \
            positive_count, negative_count

    else:
        logging.error(f'Error{response.status_code}')
        return 0, 0, 0, 0


if __name__ == "__main__":
    positive_polarity_score_outer, negative_polarity_score_outer,\
        positive_count_outer, negative_count_outer = check_news_cryptocompare_sentiment()

    logging.info(f'positive_polarity: {positive_polarity_score_outer}'
                 f' and negative_polarity: {negative_polarity_score_outer}')
    logging.info(f'positive_count: {positive_count_outer} '
                 f'negative_count: {negative_count_outer}')