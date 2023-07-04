import requests
from bs4 import BeautifulSoup
from textblob import TextBlob
import logging
from typing import Tuple
from z_handy_modules import retry_on_error


SENTIMENT_POSITIVE_THRESHOLD = 0.1
SENTIMENT_NEGATIVE_THRESHOLD = -0.001


@retry_on_error(max_retries=3, delay=5, allowed_exceptions=(
        Exception, requests.exceptions.RequestException),
                fallback_values=(0.0, 0.0, 0, 0))
def check_news_sentiment_scrapper() -> Tuple[float, float, int, int]:
    positive_polarity_score = 0.0
    negative_polarity_score = 0.0
    positive_count = 0
    negative_count = 0

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
            raise Exception

    # prevent division by zero
    positive_polarity = positive_polarity_score / positive_count if positive_count > 0 else 0
    negative_polarity = negative_polarity_score / negative_count if negative_count > 0 else 0

    return positive_polarity, abs(negative_polarity), positive_count, negative_count


if __name__ == "__main__":
    positive_polarity_score_outer, negative_polarity_score_outer, \
        positive_count_outer, negative_count_outer = check_news_sentiment_scrapper()

    logging.info(f'positive_polarity: {positive_polarity_score_outer}'
                 f' and negative_polarity: {negative_polarity_score_outer}')
    logging.info(f'positive_count: {positive_count_outer} '
                 f'negative_count: {negative_count_outer}')
