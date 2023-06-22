import pandas as pd
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from dash import dash_table
import logging

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

TRADE_DETAILS_PATH = 'data/trades_details.csv'

def visualize_trade_details():
    df = pd.read_csv(TRADE_DETAILS_PATH)

    # Display all columns except index
    columns = [{"name": i, "id": i} for i in df.columns]

    # Create table
    table = dash_table.DataTable(
        data=df.to_dict('records'),
        columns=columns,
        fixed_rows={'headers': True, 'data': 0},  # Enable fixed headers
        style_header={'backgroundColor': 'rgb(30, 30, 30)'},
        style_cell={
            'backgroundColor': 'rgb(50, 50, 50)',
            'color': 'white'
        },
    )

    return table

def create_layout():
    interval_component = dcc.Interval(
        id='interval-component',
        interval=50 * 1000,  # in milliseconds
        n_intervals=0
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
            ),
            interval_component  # add the interval component to the layout
        ]
    )

    app.layout = trade_details_div

if __name__ == '__main__':
    create_layout()

    @app.callback(Output('trade_details_table', 'children'),
                  [Input('interval-component', 'n_intervals')])
    def update_trade_details(n):
        return visualize_trade_details()

    app.run_server(host='0.0.0.0', port=8051, debug=False)
