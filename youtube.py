import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import pickle
import os.path
from google.auth.transport.requests import Request
import logging
from datetime import datetime, timedelta
from handy_modules import compare_google_and_reddit_and_youtube
from database import save_value_to_database
from handy_modules import should_update, save_update_time, retry_on_error_with_fallback, retry_on_error_fallback_0_0
from typing import Tuple
from database import read_database
from googleapiclient.errors import HttpError
from google.auth.exceptions import RefreshError


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def get_authenticated_service():
    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = "config/youtube_client_secret.json"
    scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]

    creds = None
    token_file = 'config/youtube_token.pickle'
    if os.path.exists(token_file):
        with open(token_file, 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        try:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                    client_secrets_file, scopes)
                creds = flow.run_local_server(port=0)
        except RefreshError as e:
            logging.error(f"Error refreshing token: {e}. Token update required.")
            logging.info("Manually authenticate and save the token in youtube_token.pickle")
            # Exception is re-raised so that the retry decorator on youtube_wrapper can handle it
            raise
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
            # If there are other exceptions that are not RefreshError, you can decide how to handle them.
            # You may choose to re-raise them if they should trigger a retry in youtube_wrapper.
            raise

        with open(token_file, 'wb') as token:
            pickle.dump(creds, token)

    youtube = googleapiclient.discovery.build(api_service_name, api_version, credentials=creds)
    return youtube


@retry_on_error_fallback_0_0(max_retries=3, delay=5, allowed_exceptions=(HttpError, RefreshError, ))
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


@retry_on_error_with_fallback(
    max_retries=3, delay=5, allowed_exceptions=(RefreshError,),
    fallback_values=(0, 0))
def youtube_wrapper() -> Tuple[float, float]:
    # If so, check the increase in the number of YouTube videos with the #bitcoin hashtag
    youtube = get_authenticated_service()

    now = datetime.utcnow()
    last_24_hours_start = (now - timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%SZ')
    last_48_hours_start = (now - timedelta(days=2)).strftime('%Y-%m-%dT%H:%M:%SZ')
    last_24_hours_end = now.strftime('%Y-%m-%dT%H:%M:%SZ')

    try:
        search_results_last_24_hours = get_youtube_videos(youtube, last_24_hours_start, last_24_hours_end)
        search_results_last_48_to_24_hours = get_youtube_videos(youtube, last_48_hours_start, last_24_hours_start)

        num_last_24_hours = len(search_results_last_24_hours)
        num_last_48_to_24_hours = len(search_results_last_48_to_24_hours)

        youtube_bullish, youtube_bearish = compare_google_and_reddit_and_youtube(
            num_last_24_hours, num_last_48_to_24_hours)

        # Save latest update time
        save_update_time('youtube')

        # Save to database
        save_value_to_database('last_24_youtube', num_last_24_hours)
        save_value_to_database('youtube_bullish', youtube_bullish)
        save_value_to_database('youtube_bearish', youtube_bearish)
    except Exception as e:
        logging.error(f"Error occurred: {e}")
        save_value_to_database('youtube_bullish', 0)
        save_value_to_database('youtube_bearish', 0)
        youtube_bullish, youtube_bearish = 0, 0

    return youtube_bullish, youtube_bearish


def check_bitcoin_youtube_videos_increase() -> Tuple[float, float]:
    if should_update('youtube'):
        return youtube_wrapper()
    else:
        database = read_database()
        youtube_bullish = database['youtube_bullish'][-1]
        youtube_bearish = database['youtube_bearish'][-1]
        return youtube_bullish, youtube_bearish


if __name__ == "__main__":
    youtube_bullish_outer, youtube_bearish_outer = youtube_wrapper()
    logging.info(f'youtube_bullish: {youtube_bullish_outer} , youtube_bearish: {youtube_bearish_outer}')
