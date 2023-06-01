import pandas as pd
from plotly.subplots import make_subplots
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

from handy_modules import get_bitcoin_price, calculate_upcoming_events, create_gauge_chart
from database import read_database


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
LATEST_INFO_SAVED = 'data/latest_info_saved.csv'
DATABASE_PATH = 'data/database.csv'
APP_UPDATE_TIME = 10


def visualize_charts():
    database = read_database()
    latest_info_saved = pd.read_csv(LATEST_INFO_SAVED).squeeze("columns")
    initial_trading_state = latest_info_saved.iloc[0]['latest_trading_state']

    macro_bullish = database['macro_bullish'][-1]
    macro_bearish = database['macro_bearish'][-1]
    prediction_bullish = database['prediction_bullish'][-1]
    prediction_bearish = database['prediction_bearish'][-1]
    technical_bullish = database['technical_bullish'][-1]
    technical_bearish = database['technical_bearish'][-1]
    richest_addresses_bullish = database['richest_addresses_bullish'][-1]
    richest_addresses_bearish = database['richest_addresses_bearish'][-1]
    google_search_bullish = database['google_search_bullish'][-1]
    google_search_bearish = database['google_search_bearish'][-1]
    reddit_bullish = database['reddit_bullish'][-1]
    reddit_bearish = database['reddit_bearish'][-1]
    youtube_bullish = database['youtube_bullish'][-1]
    youtube_bearish = database['youtube_bearish'][-1]
    news_bullish = database['news_bullish'][-1]
    news_bearish = database['news_bearish'][-1]

    if initial_trading_state == 'long' or initial_trading_state == 'short':
        order_book_bullish = latest_info_saved.iloc[0]['order_book_hit_profit']
        order_book_bearish = latest_info_saved.iloc[0]['order_book_hit_loss']
        weighted_score_up = latest_info_saved.iloc[0]['score_profit_position']
        weighted_score_down = latest_info_saved.iloc[0]['score_loss_position']

    else:
        order_book_bullish = database['order_book_bullish'][-1]
        order_book_bearish = database['order_book_bearish'][-1]
        weighted_score_up = database['weighted_score_up'][-1]
        weighted_score_down = database['weighted_score_down'][-1]

    fig = make_subplots(rows=2, cols=5,
                        specs=[[{"type": "indicator"}] * 5] * 2,
                        subplot_titles=["Macro Sentiment", "Order Book", "Prediction", "Technical Analysis",
                                        "Richest Addresses", "Google Search Trend", "Reddit Sentiment",
                                        "YouTube Sentiment", "News Sentiment", "Weighted Score"])

    fig.add_trace(create_gauge_chart(
        macro_bullish, macro_bearish, 'macro', show_number=False), row=1, col=1)
    fig.add_trace(create_gauge_chart(
        order_book_bullish, order_book_bearish, 'order_book', show_number=False), row=1, col=2)
    fig.add_trace(create_gauge_chart(
        prediction_bullish, prediction_bearish, 'predicted_price', show_number=False), row=1, col=3)
    fig.add_trace(create_gauge_chart(
        technical_bullish, technical_bearish, 'predicted_price',  show_number=False), row=1, col=4)
    fig.add_trace(create_gauge_chart(
        richest_addresses_bullish, richest_addresses_bearish, 'predicted_price', show_number=False), row=1, col=5)
    fig.add_trace(create_gauge_chart(
        google_search_bullish, google_search_bearish, 'predicted_price',  show_number=False), row=2, col=1)
    fig.add_trace(create_gauge_chart(
        reddit_bullish, reddit_bearish, 'predicted_price',  show_number=False), row=2, col=2)
    fig.add_trace(create_gauge_chart(
        youtube_bullish, youtube_bearish, 'predicted_price',  show_number=False), row=2, col=3)
    fig.add_trace(create_gauge_chart(
        news_bullish, news_bearish, 'predicted_price',  show_number=False), row=2, col=4)
    fig.add_trace(create_gauge_chart(
        weighted_score_up, weighted_score_down, 'predicted_price',  show_number=True), row=2, col=5)

    fig.update_layout(
        font=dict(size=10)
    )

    fed_rate_m_to_m_read = float(latest_info_saved['fed_rate_m_to_m'][0])
    initial_fed_rate_m_to_m = f'Fed rate MtoM: {fed_rate_m_to_m_read}'

    cpi_m_to_m_read = float(latest_info_saved['cpi_m_to_m'][0])
    initial_cpi_m_to_m = f'CPI MtoM: {cpi_m_to_m_read}'

    ppi_m_to_m_read = float(latest_info_saved['ppi_m_to_m'][0])
    initial_ppi_m_to_m = f'PPI MtoM: {ppi_m_to_m_read}'

    initial_bid = int(database['bid_volume'][-1])

    initial_ask = int(database['ask_volume'][-1])

    initial_predicted_price = database['predicted_price'][-1]
    initial_current_price = get_bitcoin_price()

    initial_rsi = float(latest_info_saved['latest_rsi'][0])
    initial_over_200EMA = latest_info_saved['over_200EMA'][0]
    initial_MACD_uptrend = database['technical_potential_up_trend'][-1]
    initial_bb_MA_distance = latest_info_saved['bb_band_MA_distance'][0]

    initial_BTC_received = int(latest_info_saved['total_received_coins_in_last_24'][0])
    initial_BTC_send = int(latest_info_saved['total_sent_coins_in_last_24'][0])

    initial_positive_news_polarity_change = round(latest_info_saved['positive_news_polarity_change'][0], 0)
    initial_negative_news_polarity_change = round(latest_info_saved['negative_news_polarity_change'][0], 0)

    initial_fed_announcement, initial_cpi_announcement, initial_ppi_announcement = calculate_upcoming_events()

    fed_rate_tooltip = dbc.Tooltip(
        "This is the tooltip text",
        target='fed-rate',  # Notice the id here matches the id of html.A component
        placement="bottom",
    )

    app.layout = html.Div([
        dcc.Interval(
            id='timer-interval-component',
            interval=5 * 1000,  # in milliseconds
            n_intervals=0
        ),

        dcc.Interval(
            id='interval-component',
            interval=APP_UPDATE_TIME * 1000,  # in milliseconds
            n_intervals=0
        ),
        html.Div(id='timer'),
        dcc.Graph(id='live-update-graph', figure=fig, style={
            'width': '90%', 'height': '100vh', 'display': 'inline-block'}),
        html.Div([
            html.Div([

                html.A(  # This is your new link for Fed rate MtoM
                    f'{initial_fed_rate_m_to_m}',
                    id='fed-rate',
                    target='_blank',  # Opens link in new tab
                    href="http://your-link.com",  # Replace with your desired URL
                    style={'fontSize': '12px'}
                ),
                fed_rate_tooltip,
                html.P(f'CPI MtoM: {initial_cpi_m_to_m}', id='cpi-rate', style={'fontSize': '12px'}),
                html.P(f'PPI MtoM: {initial_ppi_m_to_m}', id='ppi-rate', style={'fontSize': '12px'}),

                html.P(initial_fed_announcement if initial_fed_announcement != '' else "",
                       id='fed-announcement',
                       style={'fontSize': '11px',
                              'color': 'red' if initial_fed_announcement != '' else None,
                              'fontWeight': 'bold' if initial_fed_announcement != '' else None}),

                html.P(initial_cpi_announcement if initial_cpi_announcement != '' else "",
                       id='cpi-announcement',
                       style={'fontSize': '11px', 'color': 'red' if initial_cpi_announcement != '' else None,
                              'fontWeight': 'bold' if initial_cpi_announcement != '' else None}),

                html.P(initial_ppi_announcement if initial_ppi_announcement else "",
                       id='ppi-announcement',
                       style={'fontSize': '11px', 'color': 'red' if initial_ppi_announcement != '' else None,
                              'fontWeight': 'bold' if initial_ppi_announcement != '' else None}),

            ]),

            html.Div([
                html.P(f'Trading State: {initial_trading_state}', id='trading-state',
                       style={'fontSize': '12px', 'margin': '0'}),
            ], style={'borderTop': '1px solid black', 'lineHeight': '1.8'}),

            html.Div([
                html.P(f'Bid vol: {initial_bid}', id='bid-volume', style={'fontSize': '12px'}),
                html.P(f'Ask vol: {initial_ask}', id='ask-volume', style={'fontSize': '12px'}),
            ], style={'borderTop': '1px solid black'}),

            html.Div([
                html.P(f'Predicted: {initial_predicted_price}', id='predicted-price',
                       style={'fontSize': '12px', 'margin': '0'}),
                html.P(f'Current: {initial_current_price}', id='current-price', style={
                    'fontSize': '12px', 'margin': '0'}),
                html.P(f'Diff: {initial_predicted_price - initial_current_price}', id='price-difference',
                       style={'fontSize': '12px', 'margin': '0'}),
            ], style={'borderTop': '1px solid black', 'lineHeight': '1.8'}),

            html.Div([
                html.P(f'RSI: {initial_rsi}', id='rsi', style={'fontSize': '12px', 'margin': '0'}),
                html.P(f'Over 200EMA: {initial_over_200EMA}', id='over-200ema', style={
                    'fontSize': '12px', 'margin': '0'}),
                html.P(f'MACD up trend: {initial_MACD_uptrend}', id='macd-trend',
                       style={'fontSize': '12px', 'margin': '0'}),
                html.P(f'bb distance MA: {initial_bb_MA_distance}', id='bb-distance',
                       style={'fontSize': '12px', 'margin': '0'}),
            ], style={'borderTop': '1px solid black', 'lineHeight': '1.8'}),

            html.Div([
                html.P(f'Rich receive: {initial_BTC_received}', id='btc-received',
                       style={'fontSize': '12px', 'margin': '0'}),
                html.P(f'Rich send: {initial_BTC_send}', id='btc-sent', style={'fontSize': '12px', 'margin': '0'}),
            ], style={'borderTop': '1px solid black', 'lineHeight': '1.8'}),

            html.Div([
                html.P(f'+ news increase: {initial_positive_news_polarity_change}', id='positive-news',
                       style={'fontSize': '12px', 'margin': '0'}),
                html.P(f'- news increase: {initial_negative_news_polarity_change}', id='negative-news',
                       style={'fontSize': '12px', 'margin': '0'}),
            ], style={'borderTop': '1px solid black', 'lineHeight': '1.8'}),

        ], style={'width': '10%', 'height': '100vh', 'display': 'inline-block', 'verticalAlign': 'top'}),
    ])
    app.run_server(host='0.0.0.0', port=8051, debug=False)


@app.callback(Output('live-update-graph', 'figure'),
              [Input('interval-component', 'n_intervals')])
def update_graph_live(n):
    # This function should return new values for all your variables.
    database = read_database()

    latest_info_saved = pd.read_csv(LATEST_INFO_SAVED).squeeze("columns")

    initial_trading_state = latest_info_saved.iloc[0]['latest_trading_state']

    macro_bullish = database['macro_bullish'][-1]
    macro_bearish = database['macro_bearish'][-1]
    prediction_bullish = database['prediction_bullish'][-1]
    prediction_bearish = database['prediction_bearish'][-1]
    technical_bullish = database['technical_bullish'][-1]
    technical_bearish = database['technical_bearish'][-1]
    richest_addresses_bullish = database['richest_addresses_bullish'][-1]
    richest_addresses_bearish = database['richest_addresses_bearish'][-1]
    google_search_bullish = database['google_search_bullish'][-1]
    google_search_bearish = database['google_search_bearish'][-1]
    reddit_bullish = database['reddit_bullish'][-1]
    reddit_bearish = database['reddit_bearish'][-1]
    youtube_bullish = database['youtube_bullish'][-1]
    youtube_bearish = database['youtube_bearish'][-1]
    news_bullish = database['news_bullish'][-1]
    news_bearish = database['news_bearish'][-1]

    if initial_trading_state == 'long' or initial_trading_state == 'short':
        order_book_bullish = latest_info_saved.iloc[0]['order_book_hit_profit']
        order_book_bearish = latest_info_saved.iloc[0]['order_book_hit_loss']
        weighted_score_up = latest_info_saved.iloc[0]['score_profit_position']
        weighted_score_down = latest_info_saved.iloc[0]['score_loss_position']

    else:
        order_book_bullish = database['order_book_bullish'][-1]
        order_book_bearish = database['order_book_bearish'][-1]
        weighted_score_up = database['weighted_score_up'][-1]
        weighted_score_down = database['weighted_score_down'][-1]

    fig = make_subplots(rows=2, cols=5,
                        specs=[[{"type": "indicator"}] * 5] * 2,
                        subplot_titles=["Macro Sentiment", "Order Book", "Prediction", "Technical Analysis",
                                        "Richest Addresses", "Google Search Trend", "Reddit Sentiment",
                                        "YouTube Sentiment", "News Sentiment", "Weighted Score"])
    fig.for_each_annotation(lambda a: a.update(font=dict(size=15)))  # Update font size for each annotation

    fig.add_trace(create_gauge_chart(
        macro_bullish, macro_bearish, 'macro', show_number=False), row=1, col=1)
    fig.add_trace(create_gauge_chart(
        order_book_bullish, order_book_bearish, 'order_book', show_number=False), row=1, col=2)
    fig.add_trace(create_gauge_chart(
        prediction_bullish, prediction_bearish, 'predicted_price', show_number=False), row=1, col=3)
    fig.add_trace(create_gauge_chart(
        technical_bullish, technical_bearish, 'predicted_price',  show_number=False), row=1, col=4)
    fig.add_trace(create_gauge_chart(
        richest_addresses_bullish, richest_addresses_bearish, 'predicted_price', show_number=False), row=1, col=5)
    fig.add_trace(create_gauge_chart(
        google_search_bullish, google_search_bearish, 'predicted_price',  show_number=False), row=2, col=1)
    fig.add_trace(create_gauge_chart(
        reddit_bullish, reddit_bearish, 'predicted_price',  show_number=False), row=2, col=2)
    fig.add_trace(create_gauge_chart(
        youtube_bullish, youtube_bearish, 'predicted_price',  show_number=False), row=2, col=3)
    fig.add_trace(create_gauge_chart(
        news_bullish, news_bearish, 'predicted_price',  show_number=False), row=2, col=4)
    fig.add_trace(create_gauge_chart(
        weighted_score_up, weighted_score_down, 'predicted_price',  show_number=True), row=2, col=5)

    fig.update_layout(
        font=dict(size=10)
    )

    return fig


@app.callback([
    Output('fed-rate', 'children'),
    Output('cpi-rate', 'children'),
    Output('ppi-rate', 'children'),
    Output('fed-announcement', 'children'),
    Output('cpi-announcement', 'children'),
    Output('ppi-announcement', 'children'),
    Output('trading-state', 'children'),
    Output('bid-volume', 'children'),
    Output('ask-volume', 'children'),
    Output('predicted-price', 'children'),
    Output('current-price', 'children'),
    Output('price-difference', 'children'),
    Output('rsi', 'children'),
    Output('over-200ema', 'children'),
    Output('macd-trend', 'children'),
    Output('bb-distance', 'children'),
    Output('btc-received', 'children'),
    Output('btc-sent', 'children'),
    Output('positive-news', 'children'),
    Output('negative-news', 'children')
], [Input('interval-component', 'n_intervals')])
def update_values(n):
    # This function should return new values for all your variables.
    database = read_database()

    latest_info_saved = pd.read_csv(LATEST_INFO_SAVED).squeeze("columns")
    new_trading_state = latest_info_saved.iloc[0]['latest_trading_state']

    fed_rate_m_to_m_read = float(latest_info_saved['fed_rate_m_to_m'][0])
    new_fed_rate = f'Fed rate MtoM: {fed_rate_m_to_m_read}'

    cpi_m_to_m_read = float(latest_info_saved['cpi_m_to_m'][0])
    new_cpi_rate = f'CPI MtoM: {cpi_m_to_m_read}'

    ppi_m_to_m_read = float(latest_info_saved['ppi_m_to_m'][0])
    new_ppi_rate = f'PPI MtoM: {ppi_m_to_m_read}'

    new_bid_volume = int(database['bid_volume'][-1])

    new_ask_volume = int(database['ask_volume'][-1])

    new_predicted_price = database['predicted_price'][-1]
    new_current_price = get_bitcoin_price()
    new_price_difference = new_current_price - new_predicted_price

    new_rsi = float(latest_info_saved['latest_rsi'][0])
    new_over_200ema = latest_info_saved['over_200EMA'][0]
    new_macd_trend = database['technical_potential_up_trend'][-1]
    new_bb_distance = latest_info_saved['bb_band_MA_distance'][0]

    new_btc_received = int(latest_info_saved['total_received_coins_in_last_24'][0])
    new_btc_sent = int(latest_info_saved['total_sent_coins_in_last_24'][0])

    new_positive_news = round(latest_info_saved['positive_news_polarity_change'][0], 0)
    new_negative_news = round(latest_info_saved['negative_news_polarity_change'][0], 0)

    latest_info_saved.to_csv(LATEST_INFO_SAVED, index=False)

    new_fed_announcement, new_cpi_announcement, new_ppi_announcement = calculate_upcoming_events()

    return (new_fed_rate, new_cpi_rate, new_ppi_rate,
            new_fed_announcement, new_cpi_announcement, new_ppi_announcement,
            f'Trading State: {new_trading_state}', f'Bid vol: {new_bid_volume}', f'Ask vol: {new_ask_volume}',
            f'Predicted: {new_predicted_price}', f'Current: {new_current_price}', f'Diff: {new_price_difference}',
            f'RSI: {new_rsi}', f'Over 200EMA: {new_over_200ema}', f'MACD up trend: {new_macd_trend}',
            f'bb distance MA: {new_bb_distance}', f'Rich receive: {new_btc_received}',
            f'Rich send: {new_btc_sent}', f'+ news increase: {new_positive_news}',
            f'- news increase: {new_negative_news}')


@app.callback(
    Output('timer', 'children'),
    [Input('timer-interval-component', 'n_intervals')]
)
def update_timer(n):

    countdown = 10 if n % 2 == 0 else 5
    return f'Next update in {countdown} seconds'


if __name__ == '__main__':
    visualize_charts()
