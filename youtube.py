import os
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import datetime

# Set up the API client
api_service_name = "youtube"
api_version = "v3"
client_secrets_file = "client_secret.json"
scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]

# Authenticate and build the service object
flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(client_secrets_file, scopes)
credentials = flow.run_local_server(port=0)

youtube = googleapiclient.discovery.build(api_service_name, api_version, credentials=credentials)

# Search for videos with the #bitcoin hashtag published in the last 24 hours
search_request = youtube.search().list(
    part="id,snippet",
    q="#bitcoin",
    type="video",
    videoDefinition="high",
    videoDuration="short",
    videoDimension="2d",
    publishedAfter=(datetime.datetime.utcnow() - datetime.timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%SZ'),
    maxResults=50
)

search_results = []
while search_request:
    search_response = search_request.execute()
    search_results.extend(search_response['items'])
    search_request = youtube.search().list_next(search_request, search_response)

# Print the number of videos found in the last 24 hours
print(f"Number of videos with the #bitcoin hashtag found in the last 24 hours: {len(search_results)}")
