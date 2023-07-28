import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
import logging
from flask import Flask

from m_visual_server_config import setup_auth, load_configuration
from m_visual_app_callbacks import register_callbacks, setup_clientside_callback
from m_visualization_divs import create_html_divs, create_widget, create_news_div
from m_visualization_side import generate_tooltips, create_scroll_up_button, \
    create_update_intervals, create_progress_bar
from m_visualization_create_figures import (create_graphs, create_trade_details_div,
                                            create_loading_component, create_log_output)
from z_handy_modules import COLORS

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

server = Flask(__name__)
server.secret_key = load_configuration()

app = dash.Dash(__name__, server=server, url_base_pathname='/', external_stylesheets=[
    dbc.themes.BOOTSTRAP, 'https://use.fontawesome.com/releases/v5.8.1/css/all.css'])

setup_auth(app, server)

register_callbacks(app)


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


def create_figure_div(graphs):
    figure_div = html.Div(
        children=graphs[1:] + generate_tooltips(),
        style={'width': '100%', 'height': '90vh', 'display': 'inline-block', 'verticalAlign': 'top'}
    )
    return figure_div


# noinspection PyTypeChecker
def create_layout():
    graphs = create_graphs()
    first_figure = dcc.Graph(
        id='live-update-graph',
        figure=graphs[:1],
        style={'width': '89%', 'height': '100vh', 'display': 'inline-block', 'marginTop': '-18px'}
    )

    figure_div = create_figure_div(graphs)

    app.layout = html.Div(
        style={'backgroundColor': COLORS['background'], 'color': COLORS['white']},
        children=[
            create_progress_bar(),
            create_loading_component(),
            html.Div(id='dummy-output', style={'display': 'none'}),
            first_figure,
            create_layout_div(),
            html.H3('Terminal output', style={'textAlign': 'center'}),
            create_log_output(),
            create_trade_details_div(),
            *create_widget(),
            html.Div(id='news-div', children=[create_news_div()]),
            figure_div
        ]
    )

    setup_clientside_callback(app)
    app.run_server(host='0.0.0.0', port=8051, debug=False)


def visualize_charts():
    create_layout()


if __name__ == '__main__':
    visualize_charts()
