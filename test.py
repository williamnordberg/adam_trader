import requests
from requests.auth import HTTPBasicAuth

# your credentials
client_id = '57GEMEj2JZ2Pl2c-LrinFg'
client_secret = 'RK7Ik2-Zkg7HIsKPZDglThJx4_x2Ng'
username = 'will7i7am'
password = 'Ea@123123'

# get an access token
auth = HTTPBasicAuth(client_id, client_secret)
data = {'grant_type': 'password',
        'username': username,
        'password': password}
headers = {'User-Agent': 'btc_monitor_app:com.www.btc1231231:v1.0 (by /u/will7i7am)'}
response = requests.post('https://www.reddit.com/api/v1/access_token',
                         auth=auth, data=data, headers=headers)
token = response.json().get('access_token')

# use the access token to make a request
headers = {'Authorization': f'bearer {token}',
           'User-Agent': 'your_user_agent'}
response = requests.get('https://oauth.reddit.com/api/v1/me', headers=headers)

# print rate limit headers
print('Used:', response.headers.get('x-ratelimit-used'))
print('Remaining:', response.headers.get('x-ratelimit-remaining'))
print('Reset:', response.headers.get('x-ratelimit-reset'))
