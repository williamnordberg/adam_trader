import requests
import datetime

access_token = 'EAAMdVilFWYUBANGmHnRTjS07ZAGRGNO8pZAvZAd5qluKwpJxpwSJXQHPOWS5nY2F0yrSZCr5ot7iRb2mWJrYVUyqJLWy7JBsqiMc9ZBKmZAelZCFqQU4KMMvhsPy8dVChWJ3REkSpxmvOPnuvUBUN39TlU0VhyZBzqnJvdCmlkDcCkxtZBObEF5xV'
hashtag = 'bitcoin'
since_date = int((datetime.datetime.now() - datetime.timedelta(days=1)).timestamp())

url = f'https://graph.facebook.com/search?q=%23{hashtag}&limit=1000&access_token={access_token}'
#https://graph.facebook.com/ search?q=%23YOU-HASH-VALUE &limit=10000 &access_token=YOUR-ACCESS-TOKEN
response = requests.get(url)
print(response.status_code)
print(response.content)

if response.status_code == 200:
    data = response.json()
    posts = data.get('data', [])
    count = len(posts)
    print(count)
else:
    print('API call failed')
