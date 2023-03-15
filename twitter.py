import tweepy
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# Twitter API credentials
consumer_key = "OerQrw03cE5ofQwEoSDPOXYqc"
consumer_secret = "hvixzZ4QuDtlFuZQjmDgbNc6ZeRLAL5I0v3BNFE9FxeJgiiovy"
access_token = "1376546948837163008-n1ncM1pMyqK9Q4wvikoIqem6ibqQI9"
access_token_secret = "yHorqQkr2faSO979xsk1XIDDapnjCp7V9psyTQmlFK7sV"

# Authenticate to Twitter
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

# Create API object
api = tweepy.API(auth)

# Define the hashtag and time range
hashtag = "#bitcoin"
now = datetime.now()
yesterday = now - timedelta(days=1)

# Use tweepy.Cursor() to search for tweets with the hashtag and time range
tweets = tweepy.Cursor(api.search_tweets, hashtag, lang="en", since=yesterday, until=now).items()

# Count the number of tweets
count = 0
for tweet in tweets:
    count += 1

logging.info(f"Number of tweets with {hashtag} in the last 24 hours: {count}")
