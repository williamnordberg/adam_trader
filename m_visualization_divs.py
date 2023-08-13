import datetime
import pytz
import json
from dash import dcc, html
import dash_bootstrap_components as dbc

from m_visualization_side import read_layout_data, create_update_intervals, create_scroll_up_button
from z_handy_modules import COLORS

tradingview_widget = "https://www.tradingview.com/widgetembed/?frameElementId=tradingview_76464&symbol=BINANCE%3ABTCUSDT&interval=D&symboledit=1&saveimage=1&toolbarbg=f1f3f6&studies=%5B%5D&hideideas=1&theme=Dark&style=1&timezone=Etc%2FUTC&studies_overrides=%7B%7D&overrides=%7B%7D&enabled_features=%5B%5D&disabled_features=%5B%5D&locale=en&utm_source=www.tradingview.com&utm_medium=widget_new&utm_campaign=chart&utm_term=BINANCE%3ABTCUSDT"


def create_html_divs():
    initial_layout_data = read_layout_data()
    html_div_list = [
        html.Div([

            html.P('L: last update', id='last_update', style={
                'fontSize': '13px', 'margin': '0px'}),
            html.P('N: next update', id='next_update',
                   style={'fontSize': '13px', 'margin': '0px'}),
        ], ),

        html.Div([
            html.A(
                f'{initial_layout_data["fed_rate_m_to_m"]}',
                id='fed-rate',
                target='_blank',  # Opens link in new tab
                href="https://www.forexfactory.com/calendar",
                style={'fontSize': '13px'}
            ),
            html.P(f'CPI MtoM: {initial_layout_data["cpi_m_to_m"]}', id='cpi-rate', style={
                'fontSize': '13px', 'marginBottom': '0px'}),
            html.P(f'PPI MtoM: {initial_layout_data["ppi_m_to_m"]}', id='ppi-rate', style={
                'fontSize': '13px', 'marginBottom': '0px'}),
            html.P(initial_layout_data["fed_announcement"] if initial_layout_data["fed_announcement"] != '' else "",
                   id='fed-announcement',
                   style={'fontSize': '13px', 'marginBottom': '0px',
                          'color': 'red' if initial_layout_data["fed_announcement"] != '' else None,
                          'fontWeight': '' if initial_layout_data["fed_announcement"] != '' else None}),
            html.P(initial_layout_data["cpi_announcement"] if initial_layout_data["cpi_announcement"] != '' else "",
                   id='cpi-announcement', style={'fontSize': '13px',
                                                 'marginBottom': '0px',
                                                 'color': 'red' if initial_layout_data["cpi_announcement"] != '' else
                                                 None,
                                                 'fontWeight': '' if initial_layout_data["cpi_announcement"] != '' else
                                                 None}),
            html.P(initial_layout_data["ppi_announcement"] if initial_layout_data["ppi_announcement"] else "",
                   id='ppi-announcement',
                   style={'fontSize': '13px', 'marginBottom': '0px',
                          'color': 'red' if initial_layout_data["ppi_announcement"] != '' else None,
                          'fontWeight': '' if initial_layout_data["ppi_announcement"] != '' else None}),
        ], style={'borderTop': '1px solid white', 'lineHeight': '1.8'}),
        html.Div([
            html.P(f'T State: {initial_layout_data["trading_state"]}', id='trading-state',
                   style={'fontSize': '13px',
                          'margin': '0px',
                          'color': 'green' if initial_layout_data["trading_state"] == 'long'
                          else ('red' if
                                initial_layout_data["trading_state"] == 'short'
                                else COLORS['white'])}),

            html.P(f'Order volume target: {initial_layout_data["order_volume"]}', id='order_volume',
                   style={'fontSize': '13px', 'margin': '0px'}),

            html.P(f'Position decision score: {initial_layout_data["position_score"]}', id='position_score',
                   style={'fontSize': '13px', 'margin': '0px'}),


        ], style={'borderTop': '1px solid white', 'lineHeight': '1.8'}),

        html.Div([
            html.P(f'Bid vol: {initial_layout_data["bid_volume"]}', id='bid-volume',
                   style={'fontSize': '14px', 'margin': '0px'}),
            html.P(f'Ask vol: {initial_layout_data["ask_volume"]}', id='ask-volume',
                   style={'fontSize': '14px', 'margin': '0px'}),
        ], style={'borderTop': '1px solid white'}),

        html.Div([
            html.P(f'Predicted: {initial_layout_data["predicted_price"]}', id='predicted-price',
                   style={'fontSize': '13px', 'margin': '0px'}),
            html.P(f'Current: {initial_layout_data["current_price"]}', id='current-price', style={
                'fontSize': '13px', 'margin': '0px'}),
            html.P(f'Diff: {int(initial_layout_data["predicted_price"] - initial_layout_data["current_price"])}',
                   id='price-difference',
                   style={'fontSize': '13px',
                          'margin': '0px',
                          'color': 'green' if int(initial_layout_data["predicted_price"] -
                                                  initial_layout_data["current_price"]) > 300
                          else ('red' if int(initial_layout_data["predicted_price"] -
                                             initial_layout_data["current_price"]) < 300
                                else COLORS['white'])}),
        ], style={'borderTop': '1px solid white'}),

        html.Div([
            html.P(f'RSI: {initial_layout_data["rsi"]}', id='rsi', style={'fontSize': '13px', 'margin': '0px'}),
            html.P(f'Over 200EMA: {initial_layout_data["over_200EMA"]}', id='over-200EMA',
                   style={'fontSize': '13px', 'margin': '0px'}),
            html.P(f'MACD uptrend: {initial_layout_data["MACD_uptrend"]}', id='MACD-uptrend',
                   style={'fontSize': '13px', 'margin': '0px'}),
            html.P(f'MA distance: {initial_layout_data["bb_MA_distance"]}', id='MA-distance',
                   style={'fontSize': '13px', 'margin': '0px'}),
        ], style={'borderTop': '1px solid white'}),

        html.Div([
            html.P(f'BTC received: {initial_layout_data["BTC_received"]}', id='BTC-received',
                   style={'fontSize': '13px', 'margin': '0px'}),
            html.P(f'BTC sent: {initial_layout_data["BTC_send"]}', id='BTC-sent', style={
                'fontSize': '13px', 'margin': '0px'}),
        ], style={'borderTop': '1px solid white'}),
    ]

    return html_div_list


def create_widget():
    html_div_list = [
        html.Div(children=[
            html.Iframe(src=tradingview_widget, style={'width': '90%', 'height': '400px'}),
        ],
            style={'display': 'flex', 'justifyContent': 'center', 'alignItems': 'center', 'marginTop': '10px'}),

        html.Div(children=[
            html.Iframe(src='/assets/tradingview_market_data.html', style={'width': '90%', 'height': '300px'}),
        ],
            style={'display': 'flex', 'justifyContent': 'center', 'alignItems': 'center', 'marginTop': '5px'}),

        html.Div(children=[
            html.Iframe(src='/assets/top_winnner_loser.html', style={'width': '45%', 'height': '400px'}),
            html.Iframe(src='/assets/tradingview_crypto_market.html', style={'width': '45%', 'height': '400px'}),
        ], style={'display': 'flex', 'justifyContent': 'space-between', 'margin': '0 5%'}),


        html.Div(children=[
            html.Iframe(src='/assets/tradingview_snaps.html', style={'width': '30%', 'height': '400px'}),
            html.Iframe(src='/assets/coingecko.html', style={'width': '30%', 'height': '400px'}),
            html.Iframe(src='/assets/tradingview_technical_analysis.html', style={'width': '39%', 'height': '400px'})
        ], style={'display': 'flex', 'justifyContent': 'space-between', 'margin': '0 5%'}),

    ]
    return html_div_list


def create_news_div():
    with open('data/news_data.json') as json_file:
        data = json.load(json_file)

    news_data = []
    for sentiment in ["positive", "negative"]:
        for news in data[sentiment]:
            title = news['title']
            score = round(news['score'], 2)
            publish_time = datetime.datetime.strptime(news['publish_time'], "%Y-%m-%d %H:%M")
            publish_time = pytz.utc.localize(publish_time)
            now_time = datetime.datetime.now(pytz.utc)
            time_diff = now_time - publish_time
            minutes, seconds = divmod(time_diff.seconds, 60)
            hours, minutes = divmod(minutes, 60)
            if hours > 0:
                time_string = f"{hours} hours ago"
            else:
                time_string = f"{minutes} minutes ago"
            link = news['link']
            news_data.append((title, score, time_string, publish_time, link))

    # Sort the news data in descending order of publish times
    news_data.sort(key=lambda x: x[3], reverse=True)

    news_div = html.Div(
        children=[
            html.H2('Latest News', style={'textAlign': 'center'}),
            html.Div(
                children=[
                    html.Div(
                        id=title[0],
                        children=[
                            html.Div(f"{title[0]} (score:{title[1]})"),
                            html.A('Read more', href=title[4], target='_blank'),
                            html.Div(title[2], style={'fontSize': 'small'})
                        ],
                        n_clicks=0,
                        style={'padding': '10px', 'cursor': 'pointer'},
                        className='news-title'
                    ) for title in news_data
                ],
                style={'display': 'flex', 'flex-direction': 'column', 'max-height': '200px', 'overflow-y': 'auto',
                       'margin': '10px', 'border': '1px solid white', 'border-radius': '10px', 'width': '90%',
                       'margin-left': 'auto', 'margin-right': 'auto'}
            ),
        ]
    )

    return news_div


def create_layout_div():
    timer_interval_component, interval_component = create_update_intervals()
    html_divs = create_html_divs()

    layout_div = html.Div(
        children=[
            timer_interval_component,
            interval_component,
            create_scroll_up_button(),
            dbc.Button("Logout", id="logout-button", className="mr-2",
                       style={'background-color': COLORS['lightgray'], 'border': 'None', 'outline': 'None'}, size="sm"),
            dcc.Location(id='logout', refresh=True)
        ] + html_divs,
        style={'width': '11%', 'height': '100vh', 'display': 'inline-block', 'verticalAlign': 'top',
               'marginTop': '20px'}
    )
    return layout_div
