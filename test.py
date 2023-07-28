@app.callback(
    Output('news-div', 'children'),
    [Input('interval-component', 'n_intervals')])
def update_news(n):
    return create_news_div()