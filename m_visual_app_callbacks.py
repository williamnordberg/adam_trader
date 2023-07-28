from dash.dependencies import Input, Output
import logging
from flask import Flask
import configparser
import os
from time import sleep

from m_visualization_divs import create_news_div
from m_visualization_side import read_layout_data

from m_visualization_create_figures import visualize_trade_details, visualized_combined, \
    visualized_news, visualized_youtube, visualized_reddit, visualized_google, visualized_richest, \
    visualize_macro, visualize_prediction, visualize_trade_results, create_gauge_charts, visualization_log
from z_handy_modules import COLORS

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# Load the config file
config = configparser.ConfigParser()
config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config/config.ini')

with open(config_path, 'r') as f:
    config_string = f.read()

config.read_string(config_string)
SERVER_SECRET_KEY = config.get('server_key', 'flask')

server = Flask(__name__)
server.secret_key = SERVER_SECRET_KEY
APP_UPDATE_TIME = 60
TIMER_PROGRESS_UPDATE_TIME = 10
PROGRESS_STEPS = 6
PROGRESS_STEP_AMOUNT = 100 / PROGRESS_STEPS
TIME_PER_STEP = APP_UPDATE_TIME / PROGRESS_STEPS


def register_callbacks(app):
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
         Output('live-update-graph', 'figure'),
         Output('news-div', 'children')],
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
                visualization_log('logs/app.log', 500),
                create_gauge_charts(),
                create_news_div())

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
            f'MACD up tr: {MACD_uptrend}', f'bb distance: {bb_MA_distance}', \
            f'Rich receive: {round(BTC_received / 1000, 1)} K', \
            f'Rich send: {round(BTC_send / 1000, 1)} K', f'+ POL news inc: {positive_news_polarity_change}', \
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

    @app.callback(Output('loading', 'style'),
                  Output('dummy-output_cube', 'children'),
                  Input('dummy-output_cube', 'id'))
    def start_up(_):
        # simulate a delay
        sleep(2)

        # hide the Loading component after delay
        return {'display': 'none'}, None


def setup_clientside_callback(app):
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

