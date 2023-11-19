import dash
from dash import html, dcc, Input, Output, State
import requests
from bs4 import BeautifulSoup
from transformers import BertTokenizer, BertForSequenceClassification
import torch

# Load pre-trained model and tokenizer (ensure this is the correct model)
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertForSequenceClassification.from_pretrained('bert-base-uncased')

app = dash.Dash(__name__)

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
            category = classify_article(url)
            return f'Predicted Category: {category}'
        except Exception as e:
            return f'Error: {str(e)}'
    else:
        return 'Enter a URL and click classify.'


def text_scraper(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        article_text = ' '.join([p.get_text() for p in soup.find_all('p')])
        return article_text
    except requests.RequestException:
        raise ValueError("Failed to retrieve the article.")


def classify_article(url):
    article_text = text_scraper(url)

    # Encode the article text
    inputs = tokenizer(article_text, return_tensors="pt", truncation=True, max_length=512)

    # Predict
    with torch.no_grad():
        outputs = model(**inputs)

    # Convert output to probabilities
    probabilities = torch.nn.functional.softmax(outputs.logits, dim=-1)

    # Replace with actual categories based on the model's training
    categories = ["Category1", "Category2", "Category3", ...]

    # Get the highest probability category
    category = categories[probabilities.argmax()]

    return category


if __name__ == '__main__':
    app.run_server(debug=True)
