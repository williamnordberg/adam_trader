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
from feedparser import FeedParserDict
import requests

from z_handy_modules import retry_on_error

SENTIMENT_POSITIVE_THRESHOLD = 0.1
SENTIMENT_NEGATIVE_THRESHOLD = -0.001
OLDEST_NEWS_TO_CONSIDER_HOURS = 24
ANTI_BIASES_NEGATIVE_NEWS_ADD_UP = 0.1
URLS = [
    'https://www.coindesk.com/arc/outboundfeeds/rss/',
    'https://cointelegraph.com/rss',
    'https://cointelegraph.com/editors_pick_rss',
    'https://min-api.cryptocompare.com/data/v2/news/?lang=EN',
]

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')

regulatory_keywords = ['sec', 'tesla', 'etf']  # all should be in lower case
important_topic_multiplier = 1.5


def adjust_negative_score(negative_score: float, correction_factor: float = ANTI_BIASES_NEGATIVE_NEWS_ADD_UP) -> float:
    """
    Function to adjust the negative sentiment score, since our sources are a bit biased toward
    positiveness of market.

    :param negative_score: float, The original negative sentiment score.
    :param correction_factor: float, The correction factor for adjustment.
    :return: float, The adjusted negative sentiment score.
    """
    adjusted_negative_score = negative_score + correction_factor

    # Ensure it doesn't exceed 1
    adjusted_negative_score = min(1.0, adjusted_negative_score)

    return adjusted_negative_score


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


def calculate_sentiment_score(content: str) -> float:
    blob = TextBlob(content)
    sentiment_score = blob.sentiment.polarity

    # Identify important topics
    words = blob.words.lower()
    if any(keyword in words for keyword in regulatory_keywords):
        sentiment_score *= important_topic_multiplier
        # This not let score go out or range [-1, 1]
        if sentiment_score > 1:
            sentiment_score = 1.0
        elif sentiment_score < -1:
            sentiment_score = -1.0

    return sentiment_score


def calculate_temporal_decay(sentiment_score: float, post: FeedParserDict) -> float:
    # Temporal Decay: remove  news older than 24h, and  decrease old news sentiment score
    current_time = datetime.now(tz=timezone.utc)
    publish_time = parse(post.published)
    hours_diff = (current_time - publish_time).total_seconds() / 3600
    decay_factor = max(1 - (hours_diff / OLDEST_NEWS_TO_CONSIDER_HOURS), 0)  # Ensure it doesn't go below 0
    return sentiment_score * decay_factor


def handle_existing_data(news_data: dict):
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
                                    if current_time - parse(news["publish_time"]) <= timedelta(hours=48)]

    # Add new data if it doesn't exist
    for sentiment in ["positive", "negative"]:
        for news in news_data[sentiment]:
            if is_not_similar(news, existing_data[sentiment]):
                existing_data[sentiment].append(news)

    # Save back to the file
    with open('data/news_data.json', 'w') as f:
        json.dump(existing_data, f, indent=4)


def calculate_temporal_decay_cryptocompare(sentiment_score, published_date):

    hours_diff = (datetime.now() - published_date).total_seconds() / (60 * 60)  # convert to hours
    decay_factor = max(1 - (hours_diff / OLDEST_NEWS_TO_CONSIDER_HOURS), 0)  # Ensure it doesn't go below 0
    return sentiment_score * decay_factor


def process_cryptocompare_news(response_json):
    positive_polarity_score, negative_polarity_score, positive_count, negative_count = 0.0, 0.0, 0, 0

    for article in response_json['Data']:
        # make sure the article has a 'title' and 'body' field before processing it
        if 'title' in article and 'body' in article:
            content = article['title'] + ' ' + article['body']
            sentiment = calculate_sentiment_score(content)

            if sentiment > SENTIMENT_POSITIVE_THRESHOLD:
                sentiment = calculate_temporal_decay_cryptocompare(
                    sentiment, datetime.utcfromtimestamp(article['published_on']))
                positive_polarity_score += sentiment
                positive_count += 1
            elif sentiment < SENTIMENT_NEGATIVE_THRESHOLD:
                sentiment = calculate_temporal_decay_cryptocompare(
                    sentiment, datetime.utcfromtimestamp(article['published_on']))
                negative_polarity_score += sentiment
                negative_count += 1
        else:
            logging.info(f"Skipping article without 'title' or 'body': {article}")

    return positive_polarity_score / positive_count if positive_count != 0 else 0,\
        abs(negative_polarity_score / negative_count) if negative_count != 0 else 0


@retry_on_error(max_retries=3, delay=5, allowed_exceptions=(Exception,),
                fallback_values=(0.0, 0.0, 0, 0))
def calculate_news_sentiment() -> Tuple[float, float, int, int]:

    positive_scores = []
    negative_scores = []

    for url in URLS:
        if url == 'https://min-api.cryptocompare.com/data/v2/news/?lang=EN':
            response_json = requests.get(url).json()
            positive_score, negative_score = process_cryptocompare_news(response_json)
            positive_scores.append(positive_score)
            negative_scores.append(negative_score)

        else:
            positive_polarity_score, negative_polarity_score, positive_count, negative_count = 0.0, 0.0, 0, 0
            positive_news, negative_news = [], []
            response = feedparser.parse(url)

            for post in response.entries:
                description = BeautifulSoup(post.description, 'html.parser').get_text()
                content = post.title + " " + description

                sentiment_score = calculate_sentiment_score(content)

                if sentiment_score > SENTIMENT_POSITIVE_THRESHOLD:
                    sentiment_score = calculate_temporal_decay(sentiment_score, post)

                    positive_polarity_score += sentiment_score
                    formatted_utc_pub_date = convert_to_utc_format(post.published)
                    positive_news.append({"title": post.title, "score": round(sentiment_score, 3),
                                          "description": description, "publish_time": formatted_utc_pub_date,
                                          "link": post.link})
                    positive_count += 1

                elif sentiment_score < SENTIMENT_NEGATIVE_THRESHOLD:
                    sentiment_score = calculate_temporal_decay(sentiment_score, post)

                    negative_polarity_score += sentiment_score
                    formatted_utc_pub_date = convert_to_utc_format(post.published)
                    negative_news.append({"title": post.title, "score": round(sentiment_score, 3),
                                          "description": description, "publish_time":
                                              formatted_utc_pub_date, "link": post.link})
                    negative_count += 1

            news_data = {
                "positive": positive_news[:3],
                "negative": negative_news[:3]
            }
            handle_existing_data(news_data)

            positive_scores.append(positive_polarity_score / positive_count if positive_count != 0 else 0)
            negative_scores.append(abs(negative_polarity_score / negative_count) if negative_count != 0 else 0)

    positive_sentiment = sum(positive_scores) / len(positive_scores)
    negative_sentiment = sum(negative_scores) / len(negative_scores)

    # Adjust negative sentiment to avoid bias
    negative_sentiment = adjust_negative_score(negative_sentiment)

    return positive_sentiment, negative_sentiment, len(positive_scores), len(negative_scores)


if __name__ == "__main__":
    positive_pol_outer, negative_pol_outer, pos_count, neg_count = calculate_news_sentiment()
    logging.info(f'positive sentiment: {positive_pol_outer}, neg sentiment: {negative_pol_outer}')
