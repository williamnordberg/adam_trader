import requests
import datetime

access_token = 'EAAMdVilFWYUBANGmHnRTjS07ZAGRGNO8pZAvZAd5qluKwpJxpwSJXQHPOWS5nY2F0yrSZCr5ot7iRb2mWJrYVUyqJLWy7JBsqiMc9ZBKmZAelZCFqQU4KMMvhsPy8dVChWJ3REkSpxmvOPnuvUBUN39TlU0VhyZBzqnJvdCmlkDcCkxtZBObEF5xV'
since_date = int((datetime.datetime.now() - datetime.timedelta(days=1)).timestamp())

url = f'https://graph.facebook.com/me/posts?since={since_date}&access_token={access_token}'

response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    posts = data.get('data', [])
    count = sum(1 for post in posts if '#bitcoin' in post.get('message', ''))
    print(count)
else:
    print('API call failed')
