import feedparser
from textblob import TextBlob
import logging
from typing import Tuple
import json
from bs4 import BeautifulSoup
import os
from difflib import SequenceMatcher
from datetime import datetime, timedelta, timezone
from dateutil.parser import parse

from z_handy_modules import retry_on_error

SENTIMENT_POSITIVE_THRESHOLD = 0.1
SENTIMENT_NEGATIVE_THRESHOLD = -0.001

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


def is_not_similar(news, existing_news):
    for existing in existing_news:
        # you can adjust the 0.8 threshold to higher or lower, depending on how similar you want the titles to be
        if similar(news['title'], existing['title']) > 0.8:
            return False
    return True


def convert_to_utc_format(pub_date_str: str) -> str:
    pub_date = datetime.strptime(pub_date_str, '%a, %d %b %Y %H:%M:%S %z')
    utc_pub_date = pub_date.astimezone(timezone.utc).replace(tzinfo=None)
    formatted_utc_pub_date = utc_pub_date.strftime('%Y-%m-%d %H:%M')
    return formatted_utc_pub_date


@retry_on_error(max_retries=3, delay=5, allowed_exceptions=(Exception,),
                fallback_values=(0.0, 0.0, 0, 0))
def check_news_coin_desk() -> Tuple[float, float, int, int]:

    positive_polarity_score = 0.0
    negative_polarity_score = 0.0
    positive_count = 0
    negative_count = 0

    # These lists will store dictionaries of news data
    positive_news = []
    negative_news = []

    url = 'https://www.coindesk.com/arc/outboundfeeds/rss/'
    response = feedparser.parse(url)

    for post in response.entries:
        description = BeautifulSoup(post.description, 'html.parser').get_text()
        content = post.title + " " + description
        blob = TextBlob(content)
        sentiment_score = blob.sentiment.polarity
        print(content)
        print(f'score: {sentiment_score}')

        if sentiment_score > SENTIMENT_POSITIVE_THRESHOLD:
            positive_polarity_score += sentiment_score
            formatted_utc_pub_date = convert_to_utc_format(post.published)
            positive_news.append({"title": post.title, "score": round(sentiment_score, 3),
                                  "description": description, "publish_time": formatted_utc_pub_date,
                                  "link": post.link})
            positive_count += 1
        elif sentiment_score < SENTIMENT_NEGATIVE_THRESHOLD:
            negative_polarity_score += sentiment_score
            formatted_utc_pub_date = convert_to_utc_format(post.published)
            negative_news.append({"title": post.title, "score": round(sentiment_score, 3),
                                  "description": description, "publish_time":
                                      formatted_utc_pub_date, "link": post.link})
            negative_count += 1

    # Sort the news from highest to lowest sentiment score
    positive_news.sort(key=lambda x: x["score"], reverse=True)
    negative_news.sort(key=lambda x: x["score"])

    news_data = {
        "positive": positive_news[:3],
        "negative": negative_news[:3]
    }

    if os.path.exists('data/news_data.json'):
        # Load existing data
        try:
            with open('data/news_data.json', 'r') as f:
                existing_data = json.load(f)
        except json.JSONDecodeError:
            existing_data = {"positive": [], "negative": []}
    else:
        # If the file doesn't exist, create an empty structure
        existing_data = {"positive": [], "negative": []}

    # Remove old data (older than 72 hours)
    current_time = datetime.now(tz=timezone.utc).replace(tzinfo=None)
    for sentiment in ["positive", "negative"]:
        existing_data[sentiment] = [news for news in existing_data[sentiment]
                                    if current_time - parse(news["publish_time"]) <= timedelta(hours=72)]

    # Add new data if it doesn't exist
    for sentiment in ["positive", "negative"]:
        for news in news_data[sentiment]:
            if is_not_similar(news, existing_data[sentiment]):
                existing_data[sentiment].append(news)

    # Save back to the file
    with open('data/news_data.json', 'w') as f:
        json.dump(existing_data, f, indent=4)

    return positive_polarity_score / positive_count if positive_count != 0 else 0,\
        abs(negative_polarity_score / negative_count) if negative_count != 0 else 0, positive_count, negative_count


if __name__ == "__main__":
    positive_polarity_score_outer, negative_polarity_score_outer,\
        positive_count_outer, negative_count_outer = check_news_coin_desk()

    logging.info(f'positive_polarity: {positive_polarity_score_outer}'
                 f' and negative_polarity: {negative_polarity_score_outer}')
    logging.info(f'positive_count: {positive_count_outer} '
                 f'negative_count: {negative_count_outer}')
