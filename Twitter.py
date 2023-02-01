import tweepy
import time

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

# Check if Elon Musk has tweeted in the last 10 hours
elon_musk_tweets = api.user_timeline(screen_name='elonmusk', count=1)

# Get the time difference between now and the most recent tweet
time_diff = time.time() - time.mktime(elon_musk_tweets[0].created_at.timetuple())

# If the time difference is less than 10 hours, print a warning message
