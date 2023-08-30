flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
    "client_secret.json",
    ["https://www.googleapis.com/auth/youtube.force-ssl"],
)
flow.redirect_uri = 'http://localhost:PORT'


OAuth client created
The client ID and secret can always be accessed from Credentials in APIs & Services

OAuth access is restricted to the test users  listed on your OAuth consent screen
Client ID
265512373743-hsgmdjn8dnovjtp6nbkjfrk7vbcl5k4r.apps.googleusercontent.com
Client secret
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
Creation date
August 30, 2023 at 10:29:16 AM GMT+8
Status
 Enabled
sAAsdasds