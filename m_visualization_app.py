# Standard library imports
import logging

# Related third party imports
from flask import Flask
import dash
import dash_bootstrap_components as dbc
from dash import html

# Local application/library specific imports
from z_handy_modules import COLORS
from m_visual_server_config import setup_auth, load_configuration
from m_visual_app_callbacks import register_callbacks, setup_clientside_callback
from m_visualization_divs import create_widget, create_news_div, create_layout_div
from m_visualization_side import create_progress_bar
from m_visualization_create_figures import (create_trade_details_div,
                                            create_loading_component, create_log_output,
                                            create_figure_div, create_first_graph)

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# Create Flask and Dash instances
server = Flask(__name__)
server.secret_key = load_configuration()

app = dash.Dash(__name__, server=server, url_base_pathname='/', external_stylesheets=[
    dbc.themes.BOOTSTRAP, 'https://use.fontawesome.com/releases/v5.8.1/css/all.css'])

# Setup authentication
setup_auth(app, server)

# Register callbacks
register_callbacks(app)


def create_layout():

    app.layout = html.Div(
        style={'backgroundColor': COLORS['background'], 'color': COLORS['white']},
        children=[
            create_progress_bar(),
            create_loading_component(),
            html.Div(id='dummy-output', style={'display': 'none'}),
            create_first_graph(),
            create_layout_div(),
            create_log_output(),
            create_trade_details_div(),
            *create_widget(),
            html.Div(id='news-div', children=[create_news_div()]),
            create_figure_div()

        ]
    )

    # Setup clientside callback and run server
    setup_clientside_callback(app)
    app.run_server(host='0.0.0.0', port=8051, debug=False)


def visualize_charts():
    create_layout()


if __name__ == '__main__':
    visualize_charts()
