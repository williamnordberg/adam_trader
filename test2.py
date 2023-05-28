import os
import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go

# File to watch
file_to_watch = 'data/trades_results.csv'

# Initial load of the data
df = pd.read_csv(file_to_watch)

app = dash.Dash(__name__)

app.layout = html.Div([
    dcc.Interval(
            id='interval-component',
            interval=7*1000,  # in milliseconds
            n_intervals=0
        ),
    dcc.Graph(id='live-update-graph'),
])

# timestamp of the last modification of the file
timestamp = os.path.getmtime(file_to_watch)


@app.callback(Output('live-update-graph', 'figure'),
              Input('interval-component', 'n_intervals'))
def update_graph_live(n):

    global timestamp
    global df  # make sure you're using the DataFrame loaded outside the function

    # check if the file has been modified
    new_timestamp = os.path.getmtime(file_to_watch)

    if new_timestamp > timestamp:
        # if yes, reload the data and update the timestamp
        df = pd.read_csv(file_to_watch)
        timestamp = new_timestamp

    # Build your figure using df
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['total_trades'],
                             y=df['PNL'],
                             mode='lines',
                             name='bitcoin_price'))

    fig.update_layout(title='Bitcoin Price Over Time',
                      xaxis_title='Time',
                      yaxis_title='Bitcoin Price',
                      autosize=True)

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
