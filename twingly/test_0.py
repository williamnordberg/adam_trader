from bs4 import BeautifulSoup
import requests
from textblob import TextBlob
import psycopg2
from flask import Flask, jsonify

BASE_URL = "https://www.bbc.com/news/world"
app = Flask(__name__)


@app.route('/headlines', methods=['GET'])
def get_headlines():
    conn = psycopg2.connect(
        dbname="my_datbasea",
        user="delta",
        password="Ea123123",
        host="localhost"
    )
    cur = conn.cursor()
    query = "SELECT * FROM news_headlines"
    cur.execute(query)
    rows = cur.fetchall()
    cur.close()
    conn.close()

    # Convert the results to a list of dictionaries for easy JSON conversion
    headlines_list = [{"id": row[0], "title": row[1], "sentiment": row[2]} for row in rows]
    return jsonify(headlines_list)


def headlines_scraper(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    headlines = soup.find_all('h3')
    headlines_ren = [head.get_text().strip() for head in headlines]
    return headlines_ren


def sentiment_analyser(news_headlines):
    polarity = []
    for head in news_headlines:
        blob = TextBlob(head)
        polarity.append(blob.sentiment.polarity)
        print(f'{head}, {blob.sentiment.polarity}')
    return polarity


def save_data(headlines, polarities):
    conn = psycopg2.connect(
        dbname="my_datbasea",
        user="delta",
        password="Ea123123",
        host="localhost"
    )

    cur = conn.cursor()
    create_table_query = '''
    CREATE TABLE IF NOT EXISTS news_headlines (
        id SERIAL PRIMARY KEY,
        title VARCHAR(255),
        sentiment NUMERIC
    );
    '''
    cur.execute(create_table_query)
    conn.commit()

    insert_query = "INSERT INTO news_headlines (title, sentiment) VALUES (%s, %s)"

    for headline, polarity in zip(headlines, polarities):
        cur.execute(insert_query, (headline, polarity))

    conn.commit()

    # Close the cursor and connection
    cur.close()
    conn.close()


if __name__ == '__main__':
    headlines_outer = headlines_scraper(BASE_URL)
    polarities_outer = sentiment_analyser(headlines_outer)
    # save_data(headlines_outer, polarities_outer)
    app.run(debug=True)

