import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd

app = dash.Dash(__name__)

# Load initial data
df = pd.read_csv('yourfile.csv')
initial_title = df['title'].iloc[-1]

app.layout = html.Div([
    dcc.Interval(
            id='interval-component',
            interval=5*1000,  # in milliseconds
            n_intervals=0
        ),
    html.H1(id='live-update-text', children=initial_title),
    dcc.Graph(id='live-update-graph'),
])

# Callback to update the graph based on the Interval component
@app.callback(Output('live-update-graph', 'figure'),
              [Input('interval-component', 'n_intervals')])
def update_graph_live(n):
    # Place the code to read your data and create your figure here
    # For example:
    df = pd.read_csv('yourfile.csv')
    # ... rest of your code to create fig ...
    return fig

# Callback to update the title based on the Interval component
@app.callback(Output('live-update-text', 'children'),
              [Input('interval-component', 'n_intervals')])
def update_text_live(n):
    df = pd.read_csv('yourfile.csv')
    title = df['title'].iloc[-1]
    return title

if __name__ == '__main__':
    app.run_server(debug=True)
