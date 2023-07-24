from z_handy_modules import COLORS
import dash_bootstrap_components as dbc
from dash import dcc, html

tradingview_widget = "https://www.tradingview.com/widgetembed/?frameElementId=tradingview_76464&symbol=BINANCE%3ABTCUSDT&interval=D&symboledit=1&saveimage=1&toolbarbg=f1f3f6&studies=%5B%5D&hideideas=1&theme=Dark&style=1&timezone=Etc%2FUTC&studies_overrides=%7B%7D&overrides=%7B%7D&enabled_features=%5B%5D&disabled_features=%5B%5D&locale=en&utm_source=www.tradingview.com&utm_medium=widget_new&utm_campaign=chart&utm_term=BINANCE%3ABTCUSDT"


def create_progress_bar():
    return html.Div([
        html.Div(id='timer', style={
            'position': 'fixed',
            'top': '0',
            'width': '100%',
            'textAlign': 'center',
            'color': '#D3D3D3',
            'fontSize': '14px',
            'marginTop': '-3px',
            'zIndex': '9999'
        }),

        dbc.Progress(value=50, color=COLORS['background'], striped=True, animated=True, id="progress",
                     className="custom-progress", style={'position': 'fixed', 'top': '0', 'width': '100%',
                                                         'backgroundColor': COLORS['background'], 'zIndex': '9998'})

    ])


def create_html_divs(initial_layout_data):
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
                   # style={'fontSize': '13px', 'margin': '0px'}),
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

        html.Div([
            html.P(f'+ news change: {initial_layout_data["positive_news_polarity_change"]}',
                   id='positive-news-change', style={'fontSize': '13px', 'margin': '0px'}),
            html.P(f'- news change: {initial_layout_data["negative_news_polarity_change"]}',
                   id='negative-news-change', style={'fontSize': '13px', 'margin': '0px'}),
        ], style={'borderTop': '1px solid white'})
    ]

    return html_div_list


def create_widget():
    html_div_list = [
        html.Div(children=[
            html.Iframe(src=tradingview_widget, style={'width': '90%', 'height': '400px'}),
        ],
            style={'display': 'flex', 'justifyContent': 'center', 'alignItems': 'center', 'marginTop': '10px'}),

        html.Div(children=[
            html.Iframe(src='/assets/tradingview_crypto_market.html', style={'width': '1030px', 'height': '294px'}, ),
        ],
            style={'display': 'flex', 'justifyContent': 'center', 'alignItems': 'center', 'marginTop': '10px'}),

        html.Div(children=[
            html.Iframe(src='/assets/tradingview_market_data.html', style={'width': '90%', 'height': '500px'}),
        ],
            style={'display': 'flex', 'justifyContent': 'center', 'alignItems': 'center', 'marginTop': '5px'}),

        html.Div(children=[
            html.Iframe(src='/assets/tradingview_snaps.html ', style={'width': '90%', 'height': '300px'}),
            html.Iframe(src='/assets/coingecko.html', style={'width': '90%', 'height': '400px'}),
            html.Iframe(src='/assets/tradingview_technical_analysis.html',
                        style={'width': '90%', 'height': '350px'}),

        ],
            style={'display': 'flex', 'justifyContent': 'center', 'alignItems': 'center', 'marginTop': '1px'}),
    ]
    return html_div_list


def create_news_div(data):
    news_titles = []
    for sentiment in ["positive", "negative"]:
        for news in data[sentiment]:
            title = news['title']
            news_titles.append(title)

    news_div = html.Div(
        children=[
            html.Div(
                children=[
                    dcc.Dropdown(
                        id='news-dropdown',
                        options=[{'label': i, 'value': i} for i in news_titles],
                        placeholder="Select a news item",
                        style={'backgroundColor': COLORS['background'], 'color': COLORS['background'],
                               'width': '90%'},
                    ),
                ],
                style={'display': 'flex', 'justify-content': 'center'}
            ),
            html.Div(
                children=[
                    html.Div(id='news-description'),
                ],
                style={'display': 'flex', 'justify-content': 'center', 'width': '90%', 'margin': '0 auto'}
            ),
        ]
    )

    return news_div
