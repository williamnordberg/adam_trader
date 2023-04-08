import requests
from bs4 import BeautifulSoup
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


def check_news_sentiment_scrapper():
    positive_polarity_score = 0.0
    positive_count = 0
    negative_polarity_score = 0.0
    negative_count = 0

    # Check for internet connection
    if not check_internet_connection():
        logging.info('unable to get news sentiment')
        return 0, 0, 0, 0

    # Set up the search query
    search_query = "Bitcoin"
    url = f"https://news.google.com/search?q={search_query}&hl=en-US&gl=US&ceid=US%3Aen&tbs=qdr:d"

    # Send a request to Google News and get the HTML response
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    # Find all the article titles and print them out
    articles = soup.find_all("a", class_="DY5T1d")
    for article in articles:
        content = article.text

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

            # prevent division by zero
    if positive_count > 0:
        positive_polarity = positive_polarity_score / positive_count
    else:
        positive_polarity = 0

    # prevent division by zero
    if negative_count > 0:
        negative_polarity = negative_polarity_score / negative_count
    else:
        negative_polarity = 0

    return positive_polarity, negative_polarity, positive_count, negative_count


if __name__ == "__main__":
    positive_polarity_score_outer, negative_polarity_score_outer, \
        positive_count_outer, negative_count_outer = check_news_sentiment_scrapper()

    logging.info(f'positive_polarity: {positive_polarity_score_outer}'
                 f' and negative_polarity: {negative_polarity_score_outer}')
    logging.info(f'positive_count: {positive_count_outer} '
                 f'negative_count: {negative_count_outer}')
