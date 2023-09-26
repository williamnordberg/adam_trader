import pandas as pd
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from googleapiclient.errors import UnknownApiNameOrVersion
from textblob import TextBlob
import pickle
import os.path
from google.auth.transport.requests import Request
from dateutil.parser import parse
from datetime import datetime, timedelta, timezone
from googleapiclient.errors import HttpError
from google.auth.exceptions import RefreshError
import logging
from z_handy_modules import retry_on_error
from z_read_write_csv import save_value_to_database, \
    should_update, save_update_time, retrieve_latest_factor_values_database, read_database

SENTIMENT_POSITIVE_THRESHOLD = 0.1
SENTIMENT_NEGATIVE_THRESHOLD = -0.001
SHORT_MOVING_AVERAGE_WINDOW = 5
LONG_MOVING_AVERAGE_WINDOW = 20


def calculate_youtube_sentiments(youtube_bullish, short_ma, long_ma, factor_type):
    adjustment = 0.125

    if factor_type == 'youtube_positive_polarity' or factor_type == 'youtube_positive_count':
        if short_ma >= long_ma:
            youtube_bullish += adjustment
        else:
            youtube_bullish -= adjustment

    elif factor_type == 'youtube_negative_polarity' or factor_type == 'youtube_negative_count':
        if short_ma > long_ma:
            youtube_bullish -= adjustment
        else:
            youtube_bullish += adjustment

    return youtube_bullish


def calculate_bitcoin_youtube_videos_increase():
    youtube_bullish, youtube_bearish = 0.5, 0.5
    data = read_database()
    df = pd.DataFrame(data, columns=['youtube_positive_polarity',
                                     'youtube_negative_polarity', 'youtube_positive_count',
                                     'youtube_negative_count'])

    for col in df.columns:
        short_ma = df[col].rolling(window=SHORT_MOVING_AVERAGE_WINDOW, min_periods=1).mean()
        long_ma = df[col].rolling(window=LONG_MOVING_AVERAGE_WINDOW, min_periods=1).mean()
        youtube_bullish = calculate_youtube_sentiments(
            youtube_bullish, short_ma.iloc[-1], long_ma.iloc[-1], col)

    return youtube_bullish


def calculate_youtube_temporal_decay(sentiment_score: float, publish_time: datetime) -> float:
    current_time = datetime.now(tz=timezone.utc)
    hours_diff = (current_time - publish_time).total_seconds() / 3600

    base = 0.9  # decay factor at 24 hours
    half_life = 24  # half-life in hours
    decay_factor = base ** (hours_diff / half_life)

    return sentiment_score * decay_factor


@retry_on_error(max_retries=3, delay=5, allowed_exceptions=(
        FileNotFoundError, pickle.UnpicklingError, HttpError, UnknownApiNameOrVersion), fallback_values='pass')
def get_authenticated_service():
    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = "config/youtube_client_secret.json"
    # client_secrets_file = "config/youtube_client_secret.json"
    scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]

    token_file = 'config/youtube_token.pickle'

    # Check if token file exists
    if not os.path.exists(token_file):
        # If the file doesn't exist, create a new token by running OAuth 2.0 flow
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
            client_secrets_file, scopes)
        creds = flow.run_local_server(port=0)

        # Save the new token to the file
        with open(token_file, 'wb') as token:
            pickle.dump(creds, token)

    else:
        with open(token_file, 'rb') as token:
            creds = pickle.load(token)

    if os.path.exists(token_file):
        with open(token_file, 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except RefreshError:
                    # creds = None
                    logging.info("Failed to refresh Youtube token. Need to re-authenticate manually.")
                    return None

            # This block is for manually refresh token
            # if creds is None:
            #    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
            #        client_secrets_file, scopes)
            #    creds = flow.run_local_server(port=0)

    with open(token_file, 'wb') as token:
        pickle.dump(creds, token)

    youtube = googleapiclient.discovery.build(api_service_name, api_version, credentials=creds)
    return youtube


@retry_on_error(max_retries=3, delay=5, allowed_exceptions=(HttpError, RefreshError),
                fallback_values='pass')
def get_youtube_videos(youtube, published_after, published_before):
    search_request = youtube.search().list(
        part="id,snippet",
        q="#bitcoin",
        type="video",
        videoDefinition="high",
        videoDuration="short",
        videoDimension="2d",
        publishedAfter=published_after,
        publishedBefore=published_before,
        maxResults=50
    )

    search_results = []
    while search_request:
        search_response = search_request.execute()
        search_results.extend(search_response['items'])
        search_request = youtube.search().list_next(search_request, search_response)
    return search_results


def calculate_sentiment_score(content: str) -> float:
    blob = TextBlob(content)
    return blob.sentiment.polarity


def calculate_sentiment_youtube_videos(youtube):

    now = datetime.utcnow()
    published_after = (now - timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%SZ')
    published_before = now.strftime('%Y-%m-%dT%H:%M:%SZ')

    positive_polarity_score, negative_polarity_score, positive_count, negative_count,\
        total_video_include_out_threshold = 0.0, 0.0, 0, 0, 0

    search_results = get_youtube_videos(youtube, published_after, published_before)
    if search_results is not None:
        for video in search_results:
            total_video_include_out_threshold += 1

            title = video['snippet']['title']
            description = video['snippet']['description']
            content = title + " " + description

            sentiment_score = calculate_sentiment_score(content)
            publish_time = parse(video['snippet']['publishedAt'])
            # Applying temporal decay
            sentiment_score = calculate_youtube_temporal_decay(sentiment_score, publish_time)
            if sentiment_score > SENTIMENT_POSITIVE_THRESHOLD:
                positive_polarity_score += sentiment_score
                positive_count += 1

            elif sentiment_score < SENTIMENT_NEGATIVE_THRESHOLD:
                negative_polarity_score += sentiment_score
                negative_count += 1

        positive_sentiment = positive_polarity_score / positive_count if positive_count != 0 else 0
        negative_sentiment = abs(negative_polarity_score / negative_count) if negative_count != 0 else 0

        return positive_sentiment, negative_sentiment, positive_count, negative_count, total_video_include_out_threshold
    else:
        return None, None, None, None, None


@retry_on_error(
    max_retries=3, delay=5, allowed_exceptions=(RefreshError,),
    fallback_values=0.5)
def youtube_wrapper() -> float:
    youtube = get_authenticated_service()
    if youtube is None:
        logging.info('youtube object is None')
        return 0.5

    positive_polarity, negative_polarity, positive_count, negative_count, total_video_include_out_threshold = \
        calculate_sentiment_youtube_videos(youtube)
    if positive_count is not None:
        # Save to database
        save_value_to_database('last_24_youtube', total_video_include_out_threshold)
        save_value_to_database('youtube_positive_polarity', positive_polarity)
        save_value_to_database('youtube_negative_polarity', negative_polarity)
        save_value_to_database('youtube_positive_count', positive_count)
        save_value_to_database('youtube_negative_count', negative_count)
    else:
        logging.info('calculate_sentiment_youtube_videos return None')
        return 0.5

    youtube_bullish = calculate_bitcoin_youtube_videos_increase()
    save_update_time('youtube')

    return youtube_bullish


def check_bitcoin_youtube_videos_increase() -> float:
    if should_update('youtube'):
        youtube_bullish = youtube_wrapper()
        save_value_to_database('youtube_bullish', youtube_bullish)

        return youtube_bullish
    else:
        return retrieve_latest_factor_values_database('youtube')


if __name__ == "__main__":
    youtube_bullish_outer = youtube_wrapper()
    print(f'youtube_bullish: {youtube_bullish_outer}')
