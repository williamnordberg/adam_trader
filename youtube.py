import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import datetime


def check_bitcoin_youtube_videos_increase():
    # Set up the API client
    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = "client_secret.json"
    scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]

    # Authenticate and build the service object
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(client_secrets_file, scopes)
    credentials = flow.run_local_server(port=0)

    youtube = googleapiclient.discovery.build(api_service_name, api_version, credentials=credentials)

    # Get the date ranges for the last 24 hours and the 24 hours before that
    now = datetime.datetime.utcnow()
    last_24_hours_start = (now - datetime.timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%SZ')
    last_48_hours_start = (now - datetime.timedelta(days=2)).strftime('%Y-%m-%dT%H:%M:%SZ')
    last_24_hours_end = now.strftime('%Y-%m-%dT%H:%M:%SZ')

    # Search for videos with the #bitcoin hashtag published in the last 24 hours
    search_request_last_24_hours = youtube.search().list(
        part="id,snippet",
        q="#bitcoin",
        type="video",
        videoDefinition="high",
        videoDuration="short",
        videoDimension="2d",
        publishedAfter=last_24_hours_start,
        publishedBefore=last_24_hours_end,
        maxResults=50
    )

    search_results_last_24_hours = []
    while search_request_last_24_hours:
        search_response = search_request_last_24_hours.execute()
        search_results_last_24_hours.extend(search_response['items'])
        search_request_last_24_hours = youtube.search().list_next(search_request_last_24_hours, search_response)

    # Search for videos with the #bitcoin hashtag published in the 24 hours before that
    search_request_last_48_to_24_hours = youtube.search().list(
        part="id,snippet",
        q="#bitcoin",
        type="video",
        videoDefinition="high",
        videoDuration="short",
        videoDimension="2d",
        publishedAfter=last_48_hours_start,
        publishedBefore=last_24_hours_start,
        maxResults=50
    )

    search_results_last_48_to_24_hours = []
    while search_request_last_48_to_24_hours:
        search_response = search_request_last_48_to_24_hours.execute()
        search_results_last_48_to_24_hours.extend(search_response['items'])
        search_request_last_48_to_24_hours = youtube.search().list_next(search_request_last_48_to_24_hours, search_response)

    # Calculate the increase or decrease in the number of videos with the #bitcoin hashtag
    num_last_24_hours = len(search_results_last_24_hours)
    num_last_48_to_24_hours = len(search_results_last_48_to_24_hours)
    delta = num_last_24_hours - num_last_48_to_24_hours

    # Check if the number of videos with the #bitcoin hashtag increased by 15% or more
    if num_last_48_to_24_hours == 0:
        return False
    increase_percentage = (delta / num_last_48_to_24_hours) * 100
    if increase_percentage >= 15:
        return True
    else:
        return False



