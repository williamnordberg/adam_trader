import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import datetime
import pickle
import os.path
from google.auth.transport.requests import Request
import logging

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
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
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
       published in the last 24 hours compared to the 24 hours before that.

       Returns:
           bool: True if there's a 15% or more increase in the number of videos, False otherwise.
       """
    youtube = get_authenticated_service()

    now = datetime.datetime.utcnow()
    last_24_hours_start = (now - datetime.timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%SZ')
    last_48_hours_start = (now - datetime.timedelta(days=2)).strftime('%Y-%m-%dT%H:%M:%SZ')
    last_24_hours_end = now.strftime('%Y-%m-%dT%H:%M:%SZ')

    search_results_last_24_hours = get_youtube_videos(youtube, last_24_hours_start, last_24_hours_end)
    search_results_last_48_to_24_hours = get_youtube_videos(youtube, last_48_hours_start, last_24_hours_start)

    num_last_24_hours = len(search_results_last_24_hours)
    num_last_48_to_24_hours = len(search_results_last_48_to_24_hours)
    delta = num_last_24_hours - num_last_48_to_24_hours

    if num_last_48_to_24_hours == 0:
        return False

    increase_percentage = (delta / num_last_48_to_24_hours) * 100
    return increase_percentage >= 15


if __name__ == "__main__":
    bitcoin_youtube_increase_15_percent = check_bitcoin_youtube_videos_increase()
    logging.info(f'bitcoin_youtube_increase_15_percent: {bitcoin_youtube_increase_15_percent}')
