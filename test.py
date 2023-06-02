import dash
from dash import html
import dash_bootstrap_components as dbc

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div([
    dbc.Button("Click to see popover", id="progress1"),
    dbc.Popover(
        [
            dbc.PopoverHeader("Progress bar"),
            dbc.PopoverBody("This is a progress bar"),
        ],
        id="popover",
        target="progress1",
        trigger="click",
    ),
])

if __name__ == "__main__":
    app.run_server(debug=True)
