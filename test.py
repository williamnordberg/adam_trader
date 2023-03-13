import requests
import json
from textblob import TextBlob


def check_sentiment_of_news():
    # Set your API key
    API_KEY = '7b1ad64379694add8ae9c48b23fcd3f6'

    # Set the endpoint and parameters for the News API
    endpoint = 'https://newsapi.org/v2/everything'
    params = {
        'q': 'cryptocurrency OR bitcoin OR blockchain',  # Search for articles related to cryptocurrencies
        'language': 'en',  # Only get articles in English
        'sortBy': 'publishedAt',  # Sort articles by date published
        'apiKey': API_KEY
    }

    # Initialize counters for positive and negative articles
    positive_count = 0
    negative_count = 0

    try:
        # Make a request to the News API and get the response
        response = requests.get(endpoint, params=params)
        response.raise_for_status()  # Raise an exception if the status code is not 200
        data = json.loads(response.text)

        # Iterate through each article and perform sentiment analysis
        for article in data['articles']:
            content = article['content']

            # Perform sentiment analysis using TextBlob
            blob = TextBlob(content)
            sentiment_score = blob.sentiment.polarity

            # Classify the sentiment as positive, negative, or neutral
            if sentiment_score > 0.1:
                positive_count += 1
            elif sentiment_score < -0.1:
                negative_count += 1

        # Check if the number of positive articles is 80% or more than the number of negative articles
        print('positive_count', positive_count)
        print('negative_count', negative_count)
        if positive_count >= 1.8 * negative_count:
            return True
        else:
            return False

    except requests.exceptions.RequestException as e:
        print(f'Error occurred: {e}')
        return False


sentiment_positive = check_sentiment_of_news()
print('sentiment_positive:', sentiment_positive)
