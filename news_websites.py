import requests
import json
from textblob import TextBlob

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
        title = article['title']
        content = article['content']

        # Perform sentiment analysis using TextBlob
        blob = TextBlob(content)
        sentiment_score = blob.sentiment.polarity

        # Classify the sentiment as positive, negative, or neutral
        if sentiment_score > 0.1:
            sentiment = 'positive'
            positive_count += 1
        elif sentiment_score < -0.1:
            sentiment = 'negative'
            negative_count += 1
        else:
            sentiment = 'neutral'

        # Print the title and sentiment of the article
        print(title)
        print(sentiment)

    # Print the total number of positive and negative articles
    print(f'Total number of positive articles: {positive_count}')
    print(f'Total number of negative articles: {negative_count}')

except requests.exceptions.RequestException as e:
    print(f'Error occurred: {e}')
