import logging
import dash
import dash_core_components as dcc
from dash import html
from dash.dependencies import Input, Output

# Set up logger
logging.basicConfig(filename='app.log', level=logging.INFO)

app = dash.Dash(__name__)


@app.callback(Output('live-log', 'children'),
              Input('interval-component', 'n_intervals'))
def update_log(_):
    # Each update, we will read the log file and return its contents
    with open('app.log', 'r') as f:
        content = f.read()

    return html.Pre(content)


@app.callback(Output('live-update-text', 'children'),
              Input('interval-component', 'n_intervals'))
def update_metrics(n):
    logging.info('Metrics updated')
    return f'Metrics updated: {n}'


app.layout = html.Div(
    [
        dcc.Interval(
            id='interval-component',
            interval=1000,  # in milliseconds
            n_intervals=0
        ),
        html.H2('Live metrics:'),
        html.Div(id='live-update-text'),
        html.H2('Live log:'),
        html.Div(id='live-log'),
    ]
)

if __name__ == '__main__':
    app.run_server(debug=True)
