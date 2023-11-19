import requests
from bs4 import BeautifulSoup
from textblob import TextBlob
import dash
from dash import Input, Output, State, dcc, html

app = dash.Dash(__name__)
URL = 'https://www.bbc.com/sport/athletics/67432970'

app.layout = html.Div([
    dcc.Input(id='url-input', type='text', placeholder='Enter news article URL'),
    html.Button('Classify', id='submit-button', n_clicks=0),
    html.Div(id='output-container')
])


@app.callback(
    Output('output-container', 'children'),
    [Input('submit-button', 'n_clicks')],
    [State('url-input', 'value')]
)
def update_output(n_clicks, url):
    if n_clicks > 0 and url:
        try:
            category = sentiment_analyser(url)
            return f'Polarity is: {category}'
        except Exception as e:
            return f'Error: {str(e)}'
    else:
        return 'Enter a URL and click classify.'


def scrapper(url):
    try:
        response = requests.get(url)
    except Exception as e:
        print(f'Exception is: {e}')
        return

    soup = BeautifulSoup(response.content, 'html.parser')
    return soup.text


def sentiment_analyser(url):
    content = scrapper(url)
    blob = TextBlob(content)
    return blob.sentiment.polarity


if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port='8050', debug=True)