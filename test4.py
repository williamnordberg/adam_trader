import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash
from dash import dcc
from dash import html
from datetime import datetime
from handy_modules import get_bitcoin_price
from dash.dependencies import Input, Output
from database import parse_date

app = dash.Dash(__name__)
LATEST_INFO_SAVED = 'data/latest_info_saved.csv'
DATABASE_PATH = 'data/database.csv'
UPDATE_TIME = 2


def calculate_upcoming_events():
    latest_info_saved = pd.read_csv(LATEST_INFO_SAVED).squeeze("columns")
    fed = datetime.strptime(latest_info_saved['interest_rate_announcement_date'][0], "%Y-%m-%d %H:%M:%S")
    cpi = datetime.strptime(latest_info_saved['cpi_announcement_date'][0], "%Y-%m-%d %H:%M:%S")
    ppi = datetime.strptime(latest_info_saved['ppi_announcement_date'][0], "%Y-%m-%d %H:%M:%S")

    now = datetime.utcnow()

    time_until_fed = fed - now
    time_until_cpi = cpi - now
    time_until_ppi = ppi - now

    fed_announcement = "N/A"
    cpi_fed_announcement = "N/A"
    ppi_fed_announcement = "N/A"

    if time_until_fed.days >= 0:
        hours, remainder = divmod(time_until_fed.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        fed_announcement = f"Next FED: {time_until_fed.days}D, {hours}H,, {minutes}m"

    if time_until_cpi.days >= 0:
        hours, remainder = divmod(time_until_cpi.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        cpi_fed_announcement = f"Next CPI: {time_until_cpi.days}D, {hours}H, {minutes}m"

    if time_until_ppi.days >= 0:
        hours, remainder = divmod(time_until_ppi.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        ppi_fed_announcement = f"Next PPI: {time_until_ppi.days}D, {hours}H, {minutes}m"

    return fed_announcement, cpi_fed_announcement, ppi_fed_announcement, \
        time_until_fed.days <= 2, time_until_cpi.days <= 2, time_until_ppi.days <= 2


def create_gauge_chart(bullish, bearish, show_number=True):
    if bullish == 0 and bearish == 0:
        value = 50
        gauge_steps = [
            {"range": [0, 1], "color": "lightgray"},
        ]
        title = ""
        bar_thickness = 0
    else:
        value = (bullish / (bullish + bearish)) * 1
        gauge_steps = [
            {"range": [0, 1], "color": "lightcoral"}
        ]
        title = "Bull" if bullish > bearish else "Bear"
        bar_thickness = 1

    return go.Indicator(
        mode="gauge+number+delta" if show_number and title == "" else "gauge",
        value=value,
        title={"text": title, "font": {"size": 13, "color": "green" if title == "Bull" else "Red"}},
        domain={"x": [0, 1], "y": [0, 1]},
        gauge={
            "axis": {"range": [0, 1]},
            "bar": {"color": "green", "thickness": bar_thickness},
            "steps": gauge_steps,
        },
        number={"suffix": "%" if show_number and title == "" else "", "font": {"size": 20}},
    )


def visualize_charts():

    database = pd.read_csv(DATABASE_PATH, converters={"date": parse_date})
    database.set_index("date", inplace=True)

    latest_info_saved = pd.read_csv(LATEST_INFO_SAVED).squeeze("columns")

    initial_trading_state = latest_info_saved.iloc[0]['latest_trading_state']

    if initial_trading_state == 'long' or initial_trading_state == 'short':
        shared_data = dict({
            'trading_state': initial_trading_state,
            'macro_bullish': database['macro_bullish'][-1],
            'macro_bearish': database['macro_bearish'][-1],
            'order_book_bullish': latest_info_saved.iloc[0]['order_book_hit_profit'],
            'order_book_bearish': latest_info_saved.iloc[0]['order_book_hit_loss'],
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
            'weighted_score_up': latest_info_saved.iloc[0]['score_profit_position'],
            'weighted_score_down': latest_info_saved.iloc[0]['score_loss_position'],
        })
    else:
        shared_data = dict({
            'trading_state': initial_trading_state,
            'macro_bullish': database['macro_bullish'][-1],
            'macro_bearish': database['macro_bearish'][-1],
            'order_book_bullish': database['order_book_bullish'][-1],
            'order_book_bearish': database['order_book_bearish'][-1],
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
            'weighted_score_up': database['weighted_score_up'][-1],
            'weighted_score_down': database['weighted_score_down'][-1],
        })

    macro_bullish = shared_data['macro_bullish']
    macro_bearish = shared_data['macro_bearish']
    order_book_bullish = shared_data['order_book_bullish']
    order_book_bearish = shared_data['order_book_bearish']
    prediction_bullish = shared_data['prediction_bullish']
    prediction_bearish = shared_data['prediction_bearish']
    technical_bullish = shared_data['technical_bullish']
    technical_bearish = shared_data['technical_bearish']
    richest_addresses_bullish = shared_data['richest_addresses_bullish']
    richest_addresses_bearish = shared_data['richest_addresses_bearish']
    google_search_bullish = shared_data['google_search_bullish']
    google_search_bearish = shared_data['google_search_bearish']
    reddit_bullish = shared_data['reddit_bullish']
    reddit_bearish = shared_data['reddit_bearish']
    youtube_bullish = shared_data['youtube_bullish']
    youtube_bearish = shared_data['youtube_bearish']
    news_bullish = shared_data['news_bullish']
    news_bearish = shared_data['news_bearish']
    weighted_score_up = shared_data['weighted_score_up']
    weighted_score_down = shared_data['weighted_score_down']

    fig = make_subplots(rows=2, cols=5,
                        specs=[[{"type": "indicator"}] * 5] * 2,
                        subplot_titles=["Macro Sentiment", "Order Book", "Prediction", "Technical Analysis",
                                        "Richest Addresses", "Google Search Trend", "Reddit Sentiment",
                                        "YouTube Sentiment", "News Sentiment", "Weighted Score"])

    fig.add_trace(create_gauge_chart(macro_bullish, macro_bearish, show_number=False), row=1, col=1)
    fig.add_trace(create_gauge_chart(order_book_bullish, order_book_bearish, show_number=False), row=1, col=2)
    fig.add_trace(create_gauge_chart(prediction_bullish, prediction_bearish, show_number=False), row=1, col=3)
    fig.add_trace(create_gauge_chart(technical_bullish, technical_bearish, show_number=False), row=1, col=4)
    fig.add_trace(create_gauge_chart(richest_addresses_bullish, richest_addresses_bearish,
                                     show_number=False), row=1, col=5)
    fig.add_trace(create_gauge_chart(google_search_bullish, google_search_bearish, show_number=False), row=2, col=1)
    fig.add_trace(create_gauge_chart(reddit_bullish, reddit_bearish, show_number=False), row=2, col=2)
    fig.add_trace(create_gauge_chart(youtube_bullish, youtube_bearish, show_number=False), row=2, col=3)
    fig.add_trace(create_gauge_chart(news_bullish, news_bearish, show_number=False), row=2, col=4)
    fig.add_trace(create_gauge_chart(weighted_score_up, weighted_score_down, show_number=True), row=2, col=5)

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

    initial_fed_announcement, initial_cpi_fed_announcement, initial_ppi_fed_announcement, \
        initial_fed_within_2_days, initial_cpi_within_2_days, initial_ppi_within_2_days = calculate_upcoming_events()

    app.layout = html.Div([
        dcc.Interval(
            id='interval-component',
            interval=3 * 1000,  # in milliseconds (every 7 seconds)
            n_intervals=0
        ),
        dcc.Graph(id='live-update-graph', figure=fig, style={
            'width': '90%', 'height': '100vh', 'display': 'inline-block'}),
        html.Div([
            html.Div([
                html.P(f'Fed rate MtoM: {initial_fed_rate_m_to_m}', id='fed-rate', style={'fontSize': '12px'}),
                html.P(f'CPI MtoM: {initial_cpi_m_to_m}', id='cpi-rate', style={'fontSize': '12px'}),
                html.P(f'PPI MtoM: {initial_ppi_m_to_m}', id='ppi-rate', style={'fontSize': '12px'}),
                html.P(initial_fed_announcement, id='fed-announcement', style={
                    'fontSize': '11px', 'color': 'red' if initial_fed_within_2_days else None,
                    'fontWeight': 'bold' if initial_fed_within_2_days else None}),
                html.P(initial_cpi_fed_announcement, id='cpi-announcement', style={
                    'fontSize': '11px', 'color': 'red' if initial_cpi_within_2_days else None,
                    'fontWeight': 'bold' if initial_cpi_within_2_days else None}),
                html.P(initial_ppi_fed_announcement, id='ppi-announcement', style={
                    'fontSize': '11px', 'color': 'red' if initial_ppi_within_2_days else None,
                    'fontWeight': 'bold' if initial_ppi_within_2_days else None}),
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
    database = pd.read_csv(DATABASE_PATH, converters={"date": parse_date})
    database.set_index("date", inplace=True)

    latest_info_saved = pd.read_csv(LATEST_INFO_SAVED).squeeze("columns")

    initial_trading_state = latest_info_saved.iloc[0]['latest_trading_state']

    if initial_trading_state == 'long' or initial_trading_state == 'short':
        shared_data = dict({
            'trading_state': initial_trading_state,
            'macro_bullish': database['macro_bullish'][-1],
            'macro_bearish': database['macro_bearish'][-1],
            'order_book_bullish': latest_info_saved.iloc[0]['order_book_hit_profit'],
            'order_book_bearish': latest_info_saved.iloc[0]['order_book_hit_loss'],
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
            'weighted_score_up': latest_info_saved.iloc[0]['score_profit_position'],
            'weighted_score_down': latest_info_saved.iloc[0]['score_loss_position'],
        })
    else:
        shared_data = dict({
            'trading_state': initial_trading_state,
            'macro_bullish': database['macro_bullish'][-1],
            'macro_bearish': database['macro_bearish'][-1],
            'order_book_bullish': database['order_book_bullish'][-1],
            'order_book_bearish': database['order_book_bearish'][-1],
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
            'weighted_score_up': database['weighted_score_up'][-1],
            'weighted_score_down': database['weighted_score_down'][-1],
        })

    macro_bullish = shared_data['macro_bullish']
    macro_bearish = shared_data['macro_bearish']
    order_book_bullish = shared_data['order_book_bullish']
    order_book_bearish = shared_data['order_book_bearish']
    prediction_bullish = shared_data['prediction_bullish']
    prediction_bearish = shared_data['prediction_bearish']
    technical_bullish = shared_data['technical_bullish']
    technical_bearish = shared_data['technical_bearish']
    richest_addresses_bullish = shared_data['richest_addresses_bullish']
    richest_addresses_bearish = shared_data['richest_addresses_bearish']
    google_search_bullish = shared_data['google_search_bullish']
    google_search_bearish = shared_data['google_search_bearish']
    reddit_bullish = shared_data['reddit_bullish']
    reddit_bearish = shared_data['reddit_bearish']
    youtube_bullish = shared_data['youtube_bullish']
    youtube_bearish = shared_data['youtube_bearish']
    news_bullish = shared_data['news_bullish']
    news_bearish = shared_data['news_bearish']
    weighted_score_up = shared_data['weighted_score_up']
    weighted_score_down = shared_data['weighted_score_down']

    fig = make_subplots(rows=2, cols=5,
                        specs=[[{"type": "indicator"}] * 5] * 2,
                        subplot_titles=["Macro Sentiment", "Order Book", "Prediction", "Technical Analysis",
                                        "Richest Addresses", "Google Search Trend", "Reddit Sentiment",
                                        "YouTube Sentiment", "News Sentiment", "Weighted Score"])

    fig.add_trace(create_gauge_chart(macro_bullish, macro_bearish, show_number=False), row=1, col=1)
    fig.add_trace(create_gauge_chart(order_book_bullish, order_book_bearish, show_number=False), row=1, col=2)
    fig.add_trace(create_gauge_chart(prediction_bullish, prediction_bearish, show_number=False), row=1, col=3)
    fig.add_trace(create_gauge_chart(technical_bullish, technical_bearish, show_number=False), row=1, col=4)
    fig.add_trace(create_gauge_chart(richest_addresses_bullish, richest_addresses_bearish,
                                     show_number=False), row=1, col=5)
    fig.add_trace(create_gauge_chart(google_search_bullish, google_search_bearish, show_number=False), row=2, col=1)
    fig.add_trace(create_gauge_chart(reddit_bullish, reddit_bearish, show_number=False), row=2, col=2)
    fig.add_trace(create_gauge_chart(youtube_bullish, youtube_bearish, show_number=False), row=2, col=3)
    fig.add_trace(create_gauge_chart(news_bullish, news_bearish, show_number=False), row=2, col=4)
    fig.add_trace(create_gauge_chart(weighted_score_up, weighted_score_down, show_number=True), row=2, col=5)

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
    database = pd.read_csv(DATABASE_PATH, converters={"date": parse_date})
    database.set_index("date", inplace=True)

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

    new_fed_announcement, new_cpi_announcement, new_ppi_announcement, \
        fed_within_2_days, cpi_within_2_days, ppi_within_2_days = calculate_upcoming_events()

    return (f'Fed rate MtoM: {new_fed_rate}', f'CPI MtoM: {new_cpi_rate}', f'PPI MtoM: {new_ppi_rate}',
            new_fed_announcement, new_cpi_announcement, new_ppi_announcement,
            f'Trading State: {new_trading_state}', f'Bid vol: {new_bid_volume}', f'Ask vol: {new_ask_volume}',
            f'Predicted: {new_predicted_price}', f'Current: {new_current_price}', f'Diff: {new_price_difference}',
            f'RSI: {new_rsi}', f'Over 200EMA: {new_over_200ema}', f'MACD up trend: {new_macd_trend}',
            f'bb distance MA: {new_bb_distance}', f'Rich receive: {new_btc_received}',
            f'Rich send: {new_btc_sent}', f'+ news increase: {new_positive_news}',
            f'- news increase: {new_negative_news}')


if __name__ == '__main__':
    visualize_charts()
