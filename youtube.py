import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import datetime
import pickle
import os.path
from google.auth.transport.requests import Request
import logging
from datetime import timedelta
from datetime import datetime
import pandas as pd
from reddit import compare

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def get_authenticated_service():
    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = "youtube_client_secret.json"
    scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]

    creds = None
    token_file = 'youtube_token.pickle'
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
        except Exception as e:
            logging.error(f"Error refreshing token: {e}")
            logging.info("Manually authenticate and save the token in youtube_token.pickle")
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                client_secrets_file, scopes)
            creds = flow.run_local_server(port=0)

        with open(token_file, 'wb') as token:
            pickle.dump(creds, token)

    youtube = googleapiclient.discovery.build(api_service_name, api_version, credentials=creds)
    return youtube


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


def check_bitcoin_youtube_videos_increase():
    """
       Checks if there's a 15% or more increase in the number of YouTube videos with the #bitcoin hashtag
       published in the last 24 hours compared to the 24 hours before that, but only if the last update was
       earlier than 8 hours ago.

       Returns:
        youtube_bullish: a value between 0 (the lowest probability) and 1 (highest probability).
        youtube_bearish: a value between 0 (the lowest probability) and 1 (highest probability).


       """
    # Read the latest info saved
    latest_info_saved = pd.read_csv('latest_info_saved.csv').squeeze("columns")

    # Check if the last update was earlier than 8 hours ago
    last_youtube_update_time_str = latest_info_saved['last_youtube_update_time'][0]
    last_youtube_update_time = datetime.strptime(last_youtube_update_time_str, '%Y-%m-%d %H:%M:%S')
    if datetime.now() - last_youtube_update_time > timedelta(hours=8):
        # If so, check the increase in the number of YouTube videos with the #bitcoin hashtag
        youtube = get_authenticated_service()

        now = datetime.utcnow()
        last_24_hours_start = (now - timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%SZ')
        last_48_hours_start = (now - timedelta(days=2)).strftime('%Y-%m-%dT%H:%M:%SZ')
        last_24_hours_end = now.strftime('%Y-%m-%dT%H:%M:%SZ')

        search_results_last_24_hours = get_youtube_videos(youtube, last_24_hours_start, last_24_hours_end)
        search_results_last_48_to_24_hours = get_youtube_videos(youtube, last_48_hours_start, last_24_hours_start)

        num_last_24_hours = len(search_results_last_24_hours)
        num_last_48_to_24_hours = len(search_results_last_48_to_24_hours)

        youtube_bullish, youtube_bearish = compare(num_last_24_hours, num_last_48_to_24_hours)

        # Save the update time to disk
        now = datetime.now()
        now_str = now.strftime('%Y-%m-%d %H:%M:%S')
        latest_info_saved.loc[0, 'last_youtube_update_time'] = now_str

        latest_info_saved.loc[0, 'youtube_bullish'] = youtube_bullish
        latest_info_saved.loc[0, 'youtube_bearish'] = youtube_bearish
        latest_info_saved.to_csv('latest_info_saved.csv', index=False)

        return youtube_bullish, youtube_bearish
    else:
        # If not, return the last value of the increase
        logging.info('Last youtube update was less than 8 hours ago. Skipping...')
        youtube_bullish = latest_info_saved['youtube_bullish'][0]
        youtube_bearish = latest_info_saved['youtube_bearish'][0]
        return youtube_bullish, youtube_bearish


if __name__ == "__main__":
    youtube_bullish_outer, youtube_bearish_outer = check_bitcoin_youtube_videos_increase()
    logging.info(f'youtube_bullish: {youtube_bullish_outer} , youtube_bearish: {youtube_bearish_outer}')
