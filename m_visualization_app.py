import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import logging

from z_handy_modules import COLORS
from m_visualization_side import generate_tooltips, read_layout_data
from m_visualization_create_figures import visualize_trade_details, visualized_combined,\
    visualized_news, visualized_youtube, visualized_reddit, visualized_google, visualized_richest,\
    visualize_macro, visualize_prediction, visualize_trade_results, create_gauge_charts


log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

TRADE_RESULT_PATH = 'data/trades_results.csv'
TRADE_DETAILS_PATH = 'data/trades_details.csv'
APP_UPDATE_TIME = 50


@app.callback(
    [Output('trade_details_table', 'children'),
     Output('combined_chart', 'figure'),
     Output('news_chart', 'figure'),
     Output('youtube_chart', 'figure'),
     Output('reddit_chart', 'figure'),
     Output('google_chart', 'figure'),
     Output('richest_chart', 'figure'),
     Output('macro_chart', 'figure'),
     Output('prediction_chart', 'figure'),
     Output('trade_results_chart', 'figure'),
     Output('log-data', 'value'),
     Output('live-update-graph', 'figure')],

    [Input('interval-component', 'n_intervals')])
def update_all(n):
    return (visualize_trade_details(),
            visualized_combined(),
            visualized_news(),
            visualized_youtube(),
            visualized_reddit(),
            visualized_google(),
            visualized_richest(),
            visualize_macro(),
            visualize_prediction(),
            visualize_trade_results(),
            visualization_log('logs/app.log', 300),
            create_gauge_charts())


def visualization_log(filename, lines=1):
    with open(filename, 'r') as f:
        return ''.join(list(f)[-lines:])


@app.callback(
    [Output('fed-rate', 'children'),
     Output('cpi-rate', 'children'),
     Output('ppi-rate', 'children'),
     Output('fed-announcement', 'children'),
     Output('cpi-announcement', 'children'),
     Output('ppi-announcement', 'children'),
     Output('trading-state', 'children'),
     Output('trading-state', 'style'),  # Add 'style' as an output
     Output('bid-volume', 'children'),
     Output('ask-volume', 'children'),
     Output('predicted-price', 'children'),
     Output('current-price', 'children'),
     Output('price-difference', 'children'),
     Output('rsi', 'children'),
     Output('over-200EMA', 'children'),
     Output('MACD-uptrend', 'children'),
     Output('MA-distance', 'children'),
     Output('BTC-received', 'children'),
     Output('BTC-sent', 'children'),
     Output('positive-news-change', 'children'),
     Output('negative-news-change', 'children')],
    [Input('interval-component', 'n_intervals')])
def update_divs(n):
    # Get the latest data
    layout_data = read_layout_data()

    # Extract values
    trading_state = layout_data["trading_state"]
    # Generate color based on trading_state
    if trading_state == 'long':
        color = 'green'
    elif trading_state == 'short':
        color = 'red'
    else:
        color = COLORS['white']

    fed_rate_m_to_m = layout_data["fed_rate_m_to_m"]
    cpi_m_to_m = layout_data["cpi_m_to_m"]
    ppi_m_to_m = layout_data["ppi_m_to_m"]
    bid_volume = layout_data["bid_volume"]
    ask_volume = layout_data["ask_volume"]
    predicted_price = int(layout_data["predicted_price"])
    current_price = int(layout_data["current_price"])
    price_difference = int(predicted_price - current_price)
    rsi = layout_data["rsi"]
    over_200EMA = layout_data["over_200EMA"]
    MACD_uptrend = layout_data["MACD_uptrend"]
    bb_MA_distance = int(layout_data["bb_MA_distance"])
    BTC_received = layout_data["BTC_received"]
    BTC_send = layout_data["BTC_send"]
    positive_news_polarity_change = layout_data["positive_news_polarity_change"]
    negative_news_polarity_change = layout_data["negative_news_polarity_change"]
    fed_announcement = layout_data["fed_announcement"]
    cpi_announcement = layout_data["cpi_announcement"]
    ppi_announcement = layout_data["ppi_announcement"]

    return fed_rate_m_to_m, f'CPI MtoM: {cpi_m_to_m}', f'PPI MtoM: {ppi_m_to_m}', fed_announcement, cpi_announcement, \
        ppi_announcement, f'T State: {trading_state}', {'color': color}, f'Bid vol: {bid_volume}', \
        f'Ask vol: {ask_volume}', f'Predicted: {predicted_price}', f'Current: {current_price}', \
        f'Diff: {price_difference}', f'RSI: {rsi}', f'Over 200EMA: {over_200EMA}', \
        f'MACD up tr: {MACD_uptrend}', f'bb distance: {bb_MA_distance}', f'Rich receive: {BTC_received}', \
        f'Rich send: {BTC_send}', f'+ news increase:{positive_news_polarity_change}', \
        f'- news increase: {negative_news_polarity_change}'


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


@app.callback(
    Output('timer', 'children'),
    [Input('timer-interval-component', 'n_intervals')]
)
def update_timer(n):
    countdown = APP_UPDATE_TIME - (n * 5) % APP_UPDATE_TIME
    return f'Next update in {countdown} sec'


def create_update_intervals():
    interval_component = dcc.Interval(
        id='interval-component',
        interval=APP_UPDATE_TIME * 1000,  # in milliseconds
        n_intervals=0
    )
    timer_interval_component = dcc.Interval(
        id='timer-interval-component',
        interval=5 * 1000,  # in milliseconds
        n_intervals=0
    )

    return timer_interval_component, interval_component


def create_graphs(fig, fig_trade_result, fig_macro, fig_prediction, fig_richest, fig_google, fig_reddit,
                  fig_youtube, fig_news, fig_combined):
    graph_list = []
    graph_ids = ['live-update-graph', 'trade_results_chart', 'macro_chart', 'prediction_chart',
                 'richest_chart', 'google_chart', 'reddit_chart',
                 'youtube_chart', 'news_chart', 'combined_chart']
    fig_list = [fig, fig_trade_result, fig_macro, fig_prediction, fig_richest, fig_google, fig_reddit,
                fig_youtube, fig_news, fig_combined]

    for i in range(len(graph_ids)):
        graph_list.append(dcc.Graph(id=graph_ids[i], figure=fig_list[i],
                                    style={'width': '100%', 'height': '100vh'}))

    return graph_list


def create_progress_bar():
    return html.Div([
        dbc.Progress(value=50, color=COLORS['background'], striped=True, animated=True, id="progress",
                     className="custom-progress", style={'position': 'fixed', 'top': '0', 'width': '100%',
                                                         'backgroundColor': COLORS['background']}),
        html.Div(id='timer', style={
            'position': 'fixed',
            'top': '0',
            'width': '100%',
            'textAlign': 'center',
            'color': '#D3D3D3',
            'fontSize': '14px',
            'marginTop': '-3px'
        })
    ])


@app.callback(Output('progress', 'value'),
              [Input('timer-interval-component', 'n_intervals')])
def update_progress(n):
    countdown = 100 if n % 10 == 0 else 100 - (n % 10) * 10
    return countdown


# noinspection PyTypeChecker
def create_layout(fig, fig_trade_result, fig_macro, fig_prediction, fig_richest, fig_google, fig_reddit,
                  fig_youtube, fig_news, fig_combined):
    initial_layout_data = read_layout_data()
    timer_interval_component, interval_component = create_update_intervals()
    progress_bar = create_progress_bar()

    graphs = create_graphs(fig, fig_trade_result, fig_macro, fig_prediction, fig_richest, fig_google, fig_reddit,
                           fig_youtube, fig_news, fig_combined)
    html_divs = create_html_divs(initial_layout_data)

    first_figure = dcc.Graph(
        id='live-update-graph',
        figure=fig,
        style={'width': '89%', 'height': '100vh', 'display': 'inline-block', 'marginTop': '-18px'}
    )

    # div wrapping the layout and taking up 10% width
    layout_div = html.Div(
        children=[timer_interval_component, interval_component] + html_divs,
        style={'width': '11%', 'height': '100vh', 'display': 'inline-block', 'verticalAlign': 'top'}
    )

    # div wrapping the rest of the figures, taking up 100% width
    figure_div = html.Div(
        children=graphs[1:] + generate_tooltips(),
        style={'width': '100%', 'height': '90vh', 'display': 'inline-block', 'verticalAlign': 'top',

               }
    )

    trade_details_div = html.Div(
        [
            html.H3('Latest trades', style={'textAlign': 'center'}),
            html.Div(
                id='trade_details_table',
                style={
                    'width': '90%',
                    'height': '20vh',
                    'overflowY': 'scroll',
                    'fontSize': '14px',
                    'margin': 'auto'  # Center the table
                }
            )
        ]
    )

    app.layout = html.Div(

        style={'backgroundColor': COLORS['background'], 'color': COLORS['white']},
        children=[
            html.Div(children=[progress_bar], style={'display': 'inline-block', 'width': '100%', 'height': '05vh'}),
            first_figure,
            layout_div,
            html.H3('Terminal putput', style={'textAlign': 'center'}),
            html.Div(children=[
                dcc.Textarea(id='log-data', style={
                    'width': '90%',
                    'height': '20vh',
                    'backgroundColor': COLORS['black_chart'],
                    'color': COLORS['white'],
                    'margin': 'auto'
                })
            ],
                style={
                    'display': 'flex',
                    'justifyContent': 'center',
                    'alignItems': 'center',
                    'width': '100%'
                }
            ),
            trade_details_div,
            figure_div,
        ]
    )

    app.run_server(host='0.0.0.0', port=8051, debug=False)


def visualize_charts():
    fig = create_gauge_charts()
    fig_trade_result = visualize_trade_results()
    fig_macro = visualize_macro()
    fig_prediction = visualize_prediction()
    fig_richest = visualized_richest()
    fig_google = visualized_google()
    fig_reddit = visualized_reddit()
    fig_youtube = visualized_youtube()
    fig_news = visualized_news()
    fig_combined = visualized_combined()
    create_layout(fig, fig_trade_result, fig_macro, fig_prediction, fig_richest, fig_google, fig_reddit,
                  fig_youtube, fig_news, fig_combined)


if __name__ == '__main__':
    visualize_charts()
