import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash
from dash import dcc
from dash import html
import pandas as pd
from datetime import datetime
from database import read_database
from handy_modules import get_bitcoin_price

LATEST_INFO_SAVED = 'data/latest_info_saved.csv'
latest_info_saved = pd.read_csv(LATEST_INFO_SAVED).squeeze("columns")
database = read_database()


def calculate_upcoming_events():
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


def visualize_charts(shared_data):
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
    fed_rate_m_to_m = f'Fed rate MtoM: {fed_rate_m_to_m_read}'

    cpi_m_to_m_read = float(latest_info_saved['cpi_m_to_m'][0])
    cpi_m_to_m = f'CPI MtoM: {cpi_m_to_m_read}'

    ppi_m_to_m_read = float(latest_info_saved['ppi_m_to_m'][0])
    ppi_m_to_m = f'PPI MtoM: {ppi_m_to_m_read}'

    bid = int(database['bid_volume'][-1])
    bid_volume = f'Bid vol: {bid}'

    ask = int(database['ask_volume'][-1])
    ask_vol = f'Ask vol: {ask}'

    predicted_price = database['predicted_price'][-1]
    current_price = get_bitcoin_price()

    rsi = float(latest_info_saved['latest_rsi'][0])
    over_200EMA = latest_info_saved['over_200EMA'][0]
    MACD_uptrend = database['technical_potential_up_trend'][-1]
    bb_MA_distance = latest_info_saved['bb_band_MA_distance'][0]

    BTC_received = int(latest_info_saved['total_received_coins_in_last_24'][0])
    BTC_send = int(latest_info_saved['total_sent_coins_in_last_24'][0])

    positive_news_polarity_change = round(latest_info_saved['positive_news_polarity_change'][0], 0)
    negative_news_polarity_change = round(latest_info_saved['negative_news_polarity_change'][0], 0)

    latest_info_saved.to_csv(LATEST_INFO_SAVED, index=False)

    fed_announcement, cpi_fed_announcement, ppi_fed_announcement, \
        fed_within_2_days, cpi_within_2_days, ppi_within_2_days = calculate_upcoming_events()

    app = dash.Dash(__name__)
    app.layout = html.Div([
        dcc.Graph(id='example-chart', figure=fig, style={'width': '90%', 'height': '100vh', 'display': 'inline-block'}),
        html.Div([
            html.Div([
                html.P(fed_rate_m_to_m, style={'fontSize': '12px'}),
                html.P(cpi_m_to_m, style={'fontSize': '12px'}),
                html.P(ppi_m_to_m, style={'fontSize': '12px'}),
                html.P(fed_announcement if fed_announcement != "N/A" else "",
                       style={'fontSize': '11px',
                              'color': 'red' if fed_within_2_days else None,
                              'fontWeight': 'bold' if fed_within_2_days else None}),
                html.P(cpi_fed_announcement if cpi_fed_announcement != "N/A" else "",
                       style={'fontSize': '11px',
                              'color': 'red' if cpi_within_2_days else None,
                              'fontWeight': 'bold' if cpi_within_2_days else None}),
                html.P(ppi_fed_announcement if ppi_fed_announcement != "N/A" else "",
                       style={'fontSize': '11px',
                              'color': 'red' if ppi_within_2_days else None,
                              'fontWeight': 'bold' if ppi_within_2_days else None}),
            ]),
            html.Div([
                html.P(bid_volume, style={'fontSize': '12px'}),
                html.P(ask_vol, style={'fontSize': '12px'}),
            ], style={'borderTop': '1px solid black'}),

            html.Div([
                html.P(f'Predicted: {predicted_price}', style={'fontSize': '12px', 'margin': '0'}),
                html.P(f'Current: {current_price}', style={'fontSize': '12px', 'margin': '0'}),
                html.P(f'Diff: {current_price - predicted_price}', style={'fontSize': '12px', 'margin': '0'}),
            ], style={'borderTop': '1px solid black', 'lineHeight': '1.8'}),

            html.Div([
                html.P(f'RSI: {rsi}', style={'fontSize': '12px', 'margin': '0'}),
                html.P(f'Over 200EMA: {over_200EMA}', style={'fontSize': '12px', 'margin': '0'}),
                html.P(f'MACD up trend: {MACD_uptrend}', style={'fontSize': '12px', 'margin': '0'}),
                html.P(f'bb distance MA: {bb_MA_distance}', style={'fontSize': '12px', 'margin': '0'}),
            ], style={'borderTop': '1px solid black', 'lineHeight': '1.8'}),

            html.Div([
                html.P(f'Rich receive: {BTC_received}', style={'fontSize': '12px', 'margin': '0'}),
                html.P(f'Rich send: {BTC_send}', style={'fontSize': '12px', 'margin': '0'}),
            ], style={'borderTop': '1px solid black', 'lineHeight': '1.8'}),

            html.Div([
                html.P(f'+ news increase: {positive_news_polarity_change}',
                       style={'fontSize': '12px', 'margin': '0'}),
                html.P(f'- news increase: {negative_news_polarity_change}',
                       style={'fontSize': '12px', 'margin': '0'}),
            ], style={'borderTop': '1px solid black', 'lineHeight': '1.8'}),

        ], style={'width': '10%', 'height': '100vh', 'display': 'inline-block', 'verticalAlign': 'top'}),
    ])

    app.run_server(host='0.0.0.0', port=8051, debug=False)


if __name__ == "__main__":
    shared_data_outer = {
        'macro_bullish': 1,
        'macro_bearish': 0,
        'order_book_bullish': 1,
        'order_book_bearish': 0,
        'prediction_bullish': 0,
        'prediction_bearish': 1,
        'technical_bullish': 0,
        'technical_bearish': 0,
        'richest_addresses_bullish': 1,
        'richest_addresses_bearish': 0,
        'google_search_bullish': 0.5,
        'google_search_bearish': 0.5,
        'reddit_bullish': 0,
        'reddit_bearish': 0,
        'youtube_bullish': 0,
        'youtube_bearish': 0,
        'news_bullish': 0,
        'news_bearish': 0,
        'weighted_score_up': 0,
        'weighted_score_down': 0,
    }

    visualize_charts(shared_data_outer)
