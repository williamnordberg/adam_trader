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

BACKGROUND_COLOR = '#000000'
TEXT_COLOR = '#FFFFFF'
LATEST_INFO_SAVED = 'data/latest_info_saved.csv'
DATABASE_PATH = 'data/database.csv'
APP_UPDATE_TIME = 50


def read_gauge_chart_data():
    database = read_database()
    latest_info_saved = pd.read_csv(LATEST_INFO_SAVED).squeeze("columns")

    data_dict = {
        'trading_state': latest_info_saved.iloc[0]['latest_trading_state'],
        'macro_bullish': database['macro_bullish'][-1],
        'macro_bearish': database['macro_bearish'][-1],
        'prediction_bullish': database['prediction_bullish'][-1],
        'prediction_bearish': database['prediction_bearish'][-1],
        'technical_bullish': database['technical_bullish'][-1],
        'technical_bearish': database['technical_bearish'][-1],
        'richest_addresses_bullish': database['richest_addresses_bullish'][-1],
        'richest_addresses_bearish': database['richest_addresses_bearish'][-1],
        'google_search_bullish': database['google_search_bullish'][-1],
        'google_search_bearish': database['google_search_bearish'][-1],
        'reddit_bullish': database['reddit_bullish'][-1],
        'reddit_bearish': database['reddit_bearish'][-1],
        'youtube_bullish': database['youtube_bullish'][-1],
        'youtube_bearish': database['youtube_bearish'][-1],
        'news_bullish': database['news_bullish'][-1],
        'news_bearish': database['news_bearish'][-1],
        'weighted_score_up': latest_info_saved.iloc[0]['latest_weighted_score_up'],
        'weighted_score_down': latest_info_saved.iloc[0]['latest_weighted_score_down'],
    }

    if data_dict['trading_state'] in ['long', 'short']:
        data_dict.update({
            'order_book_bullish': latest_info_saved.iloc[0]['order_book_hit_profit'],
            'order_book_bearish': latest_info_saved.iloc[0]['order_book_hit_loss']
        })
    else:
        data_dict.update({
            'order_book_bullish': database['order_book_bullish'][-1],
            'order_book_bearish': database['order_book_bearish'][-1]
        })

    return data_dict


# noinspection PyTypeChecker
def create_gauge_charts():
    data_dict = read_gauge_chart_data()
    fig = make_subplots(rows=2, cols=5,
                        specs=[[{"type": "indicator"}] * 5] * 2,
                        subplot_titles=["Macro Sentiment", "Order Book", "Prediction", "Technical Analysis",
                                        "Richest Addresses", "Google Search Trend", "Reddit Sentiment",
                                        "YouTube Sentiment", "News Sentiment", "Weighted Score"])

    fig.add_trace(create_gauge_chart(
        data_dict['macro_bullish'], data_dict['macro_bearish'], 'macro'), row=1, col=1)
    fig.add_trace(create_gauge_chart(
        data_dict['order_book_bullish'], data_dict['order_book_bearish'], 'order_book'), row=1, col=2)
    fig.add_trace(create_gauge_chart(
        data_dict['prediction_bullish'], data_dict['prediction_bearish'],
        'predicted_price'), row=1, col=3)
    fig.add_trace(create_gauge_chart(
        data_dict['technical_bullish'], data_dict['technical_bearish'],
        'technical_analysis'), row=1, col=4)
    fig.add_trace(create_gauge_chart(data_dict['richest_addresses_bullish'], data_dict['richest_addresses_bearish'],
                                     'richest_addresses'), row=1, col=5)
    fig.add_trace(create_gauge_chart(
        data_dict['google_search_bullish'], data_dict['google_search_bearish'],
        'google_search'), row=2, col=1)
    fig.add_trace(create_gauge_chart(
        data_dict['reddit_bullish'], data_dict['reddit_bearish'], 'reddit'), row=2, col=2)
    fig.add_trace(create_gauge_chart(
        data_dict['youtube_bullish'], data_dict['youtube_bearish'], 'youtube'), row=2, col=3)
    fig.add_trace(create_gauge_chart(
        data_dict['news_bullish'], data_dict['news_bearish'], 'sentiment_of_news'), row=2, col=4)
    fig.add_trace(create_gauge_chart(
        data_dict['weighted_score_up'], data_dict['weighted_score_down'],
        'weighted_score'), row=2, col=5)

    fig.update_layout(plot_bgcolor=BACKGROUND_COLOR, paper_bgcolor=BACKGROUND_COLOR)

    for annotation in fig['layout']['annotations']:
        annotation['font'] = dict(color=TEXT_COLOR, size=16)  # set color and size of subplot titles

    return fig


def read_layout_data():
    database = read_database()
    latest_info_saved = pd.read_csv(LATEST_INFO_SAVED).squeeze("columns")
    fed_announcement, cpi_announcement, ppi_announcement = calculate_upcoming_events()

    layout_data = {
        "trading_state": f'Trading state: {latest_info_saved["latest_trading_state"][0]}',
        "fed_rate_m_to_m": f'Fed rate MtM: {float(latest_info_saved["fed_rate_m_to_m"][0])}',
        "cpi_m_to_m": f'CPI MtoM: {float(latest_info_saved["cpi_m_to_m"][0])}',
        "ppi_m_to_m": f'PPI MtoM: {float(latest_info_saved["ppi_m_to_m"][0])}',
        "bid_volume": int(database['bid_volume'][-1]),
        "ask_volume": int(database['ask_volume'][-1]),
        "predicted_price": database['predicted_price'][-1],
        "current_price": get_bitcoin_price(),
        "rsi": float(latest_info_saved['latest_rsi'][0]),
        "over_200EMA": latest_info_saved['over_200EMA'][0],
        "MACD_uptrend": database['technical_potential_up_trend'][-1],
        "bb_MA_distance": latest_info_saved['bb_band_MA_distance'][0],
        "BTC_received": int(latest_info_saved['total_received_coins_in_last_24'][0]),
        "BTC_send": int(latest_info_saved['total_sent_coins_in_last_24'][0]),
        "positive_news_polarity_change": round(latest_info_saved['positive_news_polarity_change'][0], 0),
        "negative_news_polarity_change": round(latest_info_saved['negative_news_polarity_change'][0], 0),
        "fed_announcement": fed_announcement,
        "cpi_announcement": cpi_announcement,
        "ppi_announcement": ppi_announcement
    }

    return layout_data


def generate_tooltips():
    return [
        dbc.Tooltip("Federal interest rate month to month increase", target='fed-rate', placement="bottom"),
        dbc.Tooltip("Consumer Price Index month to month increase", target='cpi-rate', placement="bottom"),
        dbc.Tooltip("Producer Price Index month to month increase", target='ppi-rate', placement="bottom"),
        dbc.Tooltip("Federal announcement details", target='fed-announcement', placement="bottom"),
        dbc.Tooltip("CPI announcement details", target='cpi-announcement', placement="bottom"),
        dbc.Tooltip("PPI announcement details", target='ppi-announcement', placement="bottom"),
        dbc.Tooltip("Trading state details", target='trading-state', placement="bottom"),
        dbc.Tooltip("Bid volume details", target='bid-volume', placement="bottom"),
        dbc.Tooltip("Ask volume details", target='ask-volume', placement="bottom"),
        dbc.Tooltip("Predicted price details", target='predicted-price', placement="bottom"),
        dbc.Tooltip("Current price details", target='current-price', placement="bottom"),
        dbc.Tooltip("Price difference details", target='price-difference', placement="bottom"),
        dbc.Tooltip("Relative Strength Index details", target='rsi', placement="bottom"),
        dbc.Tooltip("Details over 200EMA", target='over-200ema', placement="bottom"),
        dbc.Tooltip("MACD up trend details", target='macd-trend', placement="bottom"),
        dbc.Tooltip("Bollinger Bands distance details", target='bb-distance', placement="bottom"),
        dbc.Tooltip("Details of rich receiving Bitcoin", target='btc-received', placement="bottom"),
        dbc.Tooltip("Details of rich sending Bitcoin", target='btc-sent', placement="bottom"),
        dbc.Tooltip("Positive news increase details", target='positive-news', placement="bottom"),
        dbc.Tooltip("Negative news increase details", target='negative-news', placement="bottom"),
        dbc.Tooltip("Macro sentiment is a measure of the overall sentiment towards Bitcoin. "
                    "This sentiment can be influenced by a variety of factors, such as the current economic climate, "
                    "the sentiment towards cryptocurrencies in general, and news events related to Bitcoin.",
                    target='macro'),
        dbc.Tooltip("Order Book represents the interest of buyers and sellers for Bitcoin at various price levels. "
                    "A higher number of buy orders compared to sell orders can indicate bullish sentiment.",
                    target='order_book'),
        dbc.Tooltip("This is the prediction of the future price of Bitcoin based on our algorithm. "
                    "A positive number indicates a bullish prediction.",
                    target='predicted_price'),
        dbc.Tooltip(
            "Technical Analysis is a method of predicting the future price of Bitcoin based on past market data, "
            "primarily price and volume. A positive number indicates a bullish technical analysis.",
            target='technical_analysis'),
        dbc.Tooltip("This shows the actions of the richest Bitcoin addresses. If they are buying more than selling, "
                    "it could indicate bullish sentiment.",
                    target='richest_addresses'),
        dbc.Tooltip("Google Search Trend indicates the interest over time for Bitcoin on Google's search engine. "
                    "An increase in search interest may indicate bullish sentiment.",
                    target='google_search'),
        dbc.Tooltip("Reddit Sentiment represents the overall sentiment towards Bitcoin in Reddit comments. "
                    "A positive number indicates a bullish sentiment.",
                    target='reddit'),
        dbc.Tooltip("YouTube Sentiment represents the overall sentiment towards Bitcoin in YouTube comments. "
                    "A positive number indicates a bullish sentiment.",
                    target='youtube'),
        dbc.Tooltip("News Sentiment represents the overall sentiment towards Bitcoin in news articles. "
                    "A positive number indicates a bullish sentiment.",
                    target='sentiment_of_news'),
        dbc.Tooltip("Weighted Score is a composite measure that takes into account all the factors above. "
                    "A positive score indicates bullish sentiment.",
                    target='weighted_score'),
    ]


def create_layout(fig):
    layout_data = read_layout_data()

    # Extracting data from layout_data dictionary
    initial_trading_state = layout_data["trading_state"]
    initial_fed_rate_m_to_m = layout_data["fed_rate_m_to_m"]
    initial_cpi_m_to_m = layout_data["cpi_m_to_m"]
    initial_ppi_m_to_m = layout_data["ppi_m_to_m"]
    initial_bid = layout_data["bid_volume"]
    initial_ask = layout_data["ask_volume"]
    initial_predicted_price = layout_data["predicted_price"]
    initial_current_price = layout_data["current_price"]
    initial_rsi = layout_data["rsi"]
    initial_over_200EMA = layout_data["over_200EMA"]
    initial_MACD_uptrend = layout_data["MACD_uptrend"]
    initial_bb_MA_distance = layout_data["bb_MA_distance"]
    initial_BTC_received = layout_data["BTC_received"]
    initial_BTC_send = layout_data["BTC_send"]
    initial_positive_news_polarity_change = layout_data["positive_news_polarity_change"]
    initial_negative_news_polarity_change = layout_data["negative_news_polarity_change"]
    initial_fed_announcement = layout_data["fed_announcement"]
    initial_cpi_announcement = layout_data["cpi_announcement"]
    initial_ppi_announcement = layout_data["ppi_announcement"]

    app.layout = html.Div(style={'backgroundColor': BACKGROUND_COLOR, 'color': TEXT_COLOR}, children=[
        dcc.Interval(
            id='timer-interval-component',
            interval=5 * 1000,  # in milliseconds
            n_intervals=0
        ),
        dbc.Progress(value=50, color=BACKGROUND_COLOR, striped=True, animated=True, id="progress",
                     className="custom-progress"),
        dbc.Popover(
            [
                dbc.PopoverHeader("Next update time"),
                dbc.PopoverBody("This shows the next updating time"),
            ],
            id="popover",
            target="progress",
            trigger="click",
            placement="auto",
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

                html.A(
                    f'{initial_fed_rate_m_to_m}',
                    id='fed-rate',
                    target='_blank',  # Opens link in new tab
                    href="https://www.forexfactory.com/calendar",
                    style={'fontSize': '13px'}
                ),
                html.P(f'CPI MtoM: {initial_cpi_m_to_m}', id='cpi-rate', style={
                    'fontSize': '13px', 'marginBottom': '0px'}),
                html.P(f'PPI MtoM: {initial_ppi_m_to_m}', id='ppi-rate', style={
                    'fontSize': '13px', 'marginBottom': '0px'}),

                html.P(initial_fed_announcement if initial_fed_announcement != '' else "",
                       id='fed-announcement',
                       style={'fontSize': '13px', 'marginBottom': '0px',
                              'color': 'red' if initial_fed_announcement != '' else None,
                              'fontWeight': '' if initial_fed_announcement != '' else None}),

                html.P(initial_cpi_announcement if initial_cpi_announcement != '' else "",
                       id='cpi-announcement',
                       style={'fontSize': '13px', 'marginBottom': '0px', 'color': 'red' if initial_cpi_announcement != '' else None,
                              'fontWeight': '' if initial_cpi_announcement != '' else None}),

                html.P(initial_ppi_announcement if initial_ppi_announcement else "",
                       id='ppi-announcement',
                       style={'fontSize': '13px', 'marginBottom': '0px', 'color': 'red' if initial_ppi_announcement != '' else None,
                              'fontWeight': '' if initial_ppi_announcement != '' else None}),

            ]),

            html.Div([
                html.P(f'T State: {initial_trading_state}', id='trading-state',
                       style={'fontSize': '13px',
                              'margin': '0px',
                              'color': 'green' if initial_trading_state == 'Trading state: long' or
                                                  initial_trading_state == 'long' else (
                               'red' if initial_trading_state == 'Trading state: short' or
                                        initial_trading_state == 'short' else TEXT_COLOR)}),
            ], style={'borderTop': '1px solid white', 'lineHeight': '1.8'}),

            html.Div([
                html.P(f'Bid vol: {initial_bid}', id='bid-volume', style={'fontSize': '14px', 'margin': '0px'}),
                html.P(f'Ask vol: {initial_ask}', id='ask-volume', style={'fontSize': '14px', 'margin': '0px'}),
            ], style={'borderTop': '1px solid white'}),

            html.Div([
                html.P(f'Predicted: {initial_predicted_price}', id='predicted-price',
                       style={'fontSize': '13px', 'margin': '0px'}),
                html.P(f'Current: {initial_current_price}', id='current-price', style={
                    'fontSize': '13px', 'margin': '0px'}),
                html.P(f'Diff: {initial_predicted_price - initial_current_price}', id='price-difference',
                       style={'fontSize': '13px', 'margin': '0px'}),
            ], style={'borderTop': '1px solid white', 'lineHeight': '1.8'}),

            html.Div([
                html.P(f'RSI: {initial_rsi}', id='rsi', style={'fontSize': '14px', 'margin': '0px'}),
                html.P(f'Over 200EMA: {initial_over_200EMA}', id='over-200ema', style={
                    'fontSize': '13px', 'margin': '0px'}),
                html.P(f'MACD up tr: {initial_MACD_uptrend}', id='macd-trend',
                       style={'fontSize': '13px', 'margin': '0px'}),
                html.P(f'bb distance: {initial_bb_MA_distance}', id='bb-distance',
                       style={'fontSize': '13px', 'margin': '0px'}),
            ], style={'borderTop': '1px solid white', 'lineHeight': '1.8'}),

            html.Div([
                html.P(f'Rich receive: {initial_BTC_received}', id='btc-received',
                       style={'fontSize': '13px', 'margin': '0px'}),
                html.P(f'Rich send: {initial_BTC_send}', id='btc-sent', style={'fontSize': '13px', 'margin': '0px'}),
            ], style={'borderTop': '1px solid white', 'lineHeight': '1.8'}),

            html.Div([
                html.P(f'+ news increase: {initial_positive_news_polarity_change}', id='positive-news',
                       style={'fontSize': '12px', 'margin': '0px'}),
                html.P(f'- news increase: {initial_negative_news_polarity_change}', id='negative-news',
                       style={'fontSize': '12px', 'margin': '0px'}),
            ], style={'borderTop': '1px solid white', 'lineHeight': '1.8'}),

        ], style={'width': '10%', 'height': '100vh', 'display': 'inline-block', 'verticalAlign': 'top'}),
    ] + generate_tooltips()
    )

    app.run_server(host='0.0.0.0', port=8051, debug=False)


def visualize_charts():
    fig = create_gauge_charts()
    create_layout(fig)


@app.callback(Output('live-update-graph', 'figure'),
              [Input('interval-component', 'n_intervals')])
def update_gauge_chart_live(n):
    fig = create_gauge_charts()
    return fig


@app.callback([
    Output('fed-rate', 'children'),
    Output('cpi-rate', 'children'),
    Output('ppi-rate', 'children'),
    Output('fed-announcement', 'children'),
    Output('cpi-announcement', 'children'),
    Output('ppi-announcement', 'children'),
    Output('trading-state', 'children'),
    Output('trading-state', 'style'),
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
def update_layout_values_live(n):

    # This function should return new values for all your variables.
    database = read_database()

    latest_info_saved = pd.read_csv(LATEST_INFO_SAVED).squeeze("columns")
    new_trading_state = latest_info_saved.iloc[0]['latest_trading_state']
    fed_rate_m_to_m_read = float(latest_info_saved['fed_rate_m_to_m'][0])
    new_fed_rate = f'Fed rate MtM: {fed_rate_m_to_m_read}'

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

    new_trading_state_style = {'fontSize': '13px', 'margin': '0px',
                               'color': 'green' if new_trading_state == 'Trading state: long' or new_trading_state == 'long' else (
                                   'red' if new_trading_state == 'Trading state: short' or new_trading_state == 'short' else TEXT_COLOR)}

    return (new_fed_rate, new_cpi_rate, new_ppi_rate,
            new_fed_announcement, new_cpi_announcement, new_ppi_announcement,
            f'T State: {new_trading_state}', new_trading_state_style, f'Bid vol: {new_bid_volume}', f'Ask vol: {new_ask_volume}',
            f'Predicted: {new_predicted_price}', f'Current: {new_current_price}', f'Diff: {new_price_difference}',
            f'RSI: {new_rsi}', f'Over 200EMA: {new_over_200ema}', f'MACD up tr: {new_macd_trend}',
            f'bb distance: {new_bb_distance}', f'Rich receive: {new_btc_received}',
            f'Rich send: {new_btc_sent}', f'+ news increase: {new_positive_news}',
            f'- news increase: {new_negative_news}')


@app.callback(
    Output('timer', 'children'),
    [Input('timer-interval-component', 'n_intervals')]
)
def update_timer(n):
    countdown = APP_UPDATE_TIME - (n * 5) % APP_UPDATE_TIME
    return f'Next update in {countdown} seconds'


@app.callback(
    Output('progress', 'value'),
    [Input('timer-interval-component', 'n_intervals')]
)
def update_progress(n):
    countdown = 100 if n % 10 == 0 else 100 - (n % 10) * 10
    return countdown


if __name__ == '__main__':
    visualize_charts()
