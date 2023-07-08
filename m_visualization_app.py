import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import logging

from m_visualization_divs import create_html_divs, create_progress_bar
from m_visualization_side import generate_tooltips, read_layout_data, create_scroll_up_button, \
    create_update_intervals
from m_visualization_create_figures import visualize_trade_details, visualized_combined, \
    visualized_news, visualized_youtube, visualized_reddit, visualized_google, visualized_richest, \
    visualize_macro, visualize_prediction, visualize_trade_results, create_gauge_charts, visualization_log, \
    create_trade_details_div
from z_handy_modules import COLORS

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = dash.Dash(__name__, external_stylesheets=[
    dbc.themes.BOOTSTRAP, 'https://use.fontawesome.com/releases/v5.8.1/css/all.css'])

APP_UPDATE_TIME = 60
TIMER_PROGRESS_UPDATE_TIME = 10
PROGRESS_STEPS = 6
PROGRESS_STEP_AMOUNT = 100 / PROGRESS_STEPS
TIME_PER_STEP = APP_UPDATE_TIME / PROGRESS_STEPS


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
def update_figures(n):
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
            visualization_log('logs/app.log', 200),
            create_gauge_charts())


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
        f'MACD up tr: {MACD_uptrend}', f'bb distance: {bb_MA_distance}', f'Rich receive: {round(BTC_received/1000, 1)} K', \
        f'Rich send: {round(BTC_send/1000, 1)} K', f'+ POL news inc: {positive_news_polarity_change}', \
        f'- POL news inc: {negative_news_polarity_change}'


@app.callback(
    [Output('timer', 'children'),
     Output('progress', 'value')],
    [Input('timer-interval-component', 'n_intervals')])
def update_timer_and_progress(n):
    current_step = (n * TIMER_PROGRESS_UPDATE_TIME // TIME_PER_STEP) % PROGRESS_STEPS

    timer_countdown = APP_UPDATE_TIME - current_step * TIME_PER_STEP
    timer_display = f'Next update in {int(timer_countdown)} sec'

    progress_countdown = 100 - current_step * PROGRESS_STEP_AMOUNT

    return timer_display, progress_countdown


def create_graphs(fig_dict):
    graph_list = []
    graph_ids = ['live-update-graph', 'trade_results_chart', 'macro_chart', 'prediction_chart',
                 'richest_chart', 'google_chart', 'reddit_chart',
                 'youtube_chart', 'news_chart', 'combined_chart']
    fig_list = [fig_dict['fig'], fig_dict['fig_trade_result'], fig_dict['fig_macro'],
                fig_dict['fig_prediction'], fig_dict['fig_richest'], fig_dict['fig_google'],
                fig_dict['fig_reddit'], fig_dict['fig_youtube'], fig_dict['fig_news'],
                fig_dict['fig_combined']]

    for i in range(len(graph_ids)):
        graph_list.append(dcc.Graph(id=graph_ids[i], figure=fig_list[i],
                                    style={'width': '100%', 'height': '100vh'}))

    return graph_list


# noinspection PyTypeChecker
def create_layout(fig_dict):

    initial_layout_data = read_layout_data()
    timer_interval_component, interval_component = create_update_intervals()
    progress_bar = create_progress_bar()

    graphs = create_graphs(fig_dict)
    html_divs = create_html_divs(initial_layout_data)

    first_figure = dcc.Graph(
        id='live-update-graph',
        figure=graphs[:1],
        style={'width': '89%', 'height': '100vh', 'display': 'inline-block', 'marginTop': '-18px'}
    )

    # div wrapping the layout and taking up 10% width
    layout_div = html.Div(
        children=[timer_interval_component, interval_component, create_scroll_up_button()] + html_divs,
        style={'width': '11%', 'height': '100vh', 'display': 'inline-block', 'verticalAlign': 'top'}
    )

    # div wrapping the rest of the figures, taking up 100% width
    figure_div = html.Div(
        children=graphs[1:] + generate_tooltips(),
        style={'width': '100%', 'height': '90vh', 'display': 'inline-block', 'verticalAlign': 'top',

               }
    )

    trade_details_div = create_trade_details_div()

    app.layout = html.Div(

        style={'backgroundColor': COLORS['background'], 'color': COLORS['white']},
        children=[
            html.Div(children=[progress_bar], style={'display': 'inline-block', 'width': '100%', 'height': '05vh'}),
            html.Div(id='dummy-output', style={'display': 'none'}),
            first_figure,
            layout_div,
            html.H3('Terminal putput', style={'textAlign': 'center'}),
            html.Div(children=[
                dcc.Textarea(id='log-data', style={
                    'width': '90%',
                    'height': '40vh',
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

    app.clientside_callback(
        """
        function(n_clicks) {
            if(n_clicks > 0){
                window.scrollTo(0, 0);
            }
            return null;
        }
        """,
        Output('dummy-output', 'children'),
        [Input('top-button', 'n_clicks')],
    )

    app.run_server(host='0.0.0.0', port=8051, debug=False)


def visualize_charts():
    fig_dict = {
        'fig': create_gauge_charts(),
        'fig_trade_result': visualize_trade_results(),
        'fig_macro': visualize_macro(),
        'fig_prediction': visualize_prediction(),
        'fig_richest': visualized_richest(),
        'fig_google': visualized_google(),
        'fig_reddit': visualized_reddit(),
        'fig_youtube': visualized_youtube(),
        'fig_news': visualized_news(),
        'fig_combined': visualized_combined(),
    }
    create_layout(fig_dict)


if __name__ == '__main__':
    visualize_charts()
