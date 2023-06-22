import pandas as pd
from plotly.subplots import make_subplots
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import logging
from datetime import timedelta
from dash import dash_table

from handy_modules import get_bitcoin_price, calculate_upcoming_events, \
    create_gauge_chart, COLORS
from database import read_database

logging.basicConfig(filename='app.log', level=logging.INFO)

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

LATEST_INFO_SAVED = 'data/latest_info_saved.csv'
DATABASE_PATH = 'data/database.csv'
TRADE_RESULT_PATH = 'data/trades_results.csv'
TRADE_DETAILS_PATH = 'data/trades_details.csv'
APP_UPDATE_TIME = 50


def tail(filename, lines=1):
    with open(filename, 'r') as f:
        return ''.join(list(f)[-lines:])


@app.callback(
    Output('log-data', 'value'),
    Input('interval-component', 'n_intervals'))
def update_metrics(n):
    log_file_path = 'app.log'  # path to your log file
    return tail(log_file_path, 300)


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


@app.callback(Output('trade_details_table', 'children'),
              [Input('interval-component', 'n_intervals')])
def update_trade_details(n):
    return visualize_trade_details()


def visualized_combined():
    df = pd.read_csv(DATABASE_PATH)

    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)

    fig = make_subplots(shared_xaxes=True, vertical_spacing=0.02)

    # Calculate the range for the last day as default time range
    latest_date = df.index.max()  # get the latest date in your data
    seven_days_ago = latest_date - timedelta(days=7)

    fig.add_trace(go.Scatter(x=df.index, y=df["weighted_score_up"],
                             name='Combined score bullish', line=dict(color=COLORS['green_chart'])))
    fig.add_trace(go.Scatter(x=df.index, y=df["weighted_score_down"],
                             name='Combined score  bearish', line=dict(color=COLORS['red_chart'])))

    fig.update_yaxes(tickfont=dict(color=COLORS['white']), side='right', showgrid=False)
    fig.update_xaxes(
        showgrid=False,
        rangeselector=dict(
            buttons=list([
                dict(count=1, label="1d", step="day", stepmode="backward"),
                dict(count=7, label="7d", step="day", stepmode="backward"),
                dict(count=1, label="1m", step="month", stepmode="backward"),
                dict(step="all")
            ]),
            bgcolor=COLORS['background'],  # Add your preferred color here
            activecolor=COLORS['lightgray'],  # Change color of the active button
            x=0.0,  # x position of buttons
            y=1.1,  # y position of buttons
        ),
        type="date"
    )
    fig.update_layout(
        xaxis_range=[seven_days_ago, latest_date],
        title={
            'text': "Combined score",
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {
                'color': COLORS['white'],
                'size': 24
            }
        },
        yaxis_title='Value',
        plot_bgcolor=COLORS['black_chart'],
        paper_bgcolor=COLORS['background'],
        font=dict(
            color=COLORS['white'],
            size=12
        ),
        legend=dict(orientation="h",  # horizontal legend
                    yanchor="bottom",
                    y=1.02,  # put it a bit above the bottom of the plot
                    xanchor="right",
                    x=1),  # put it to the right of the plot
        hovermode="x"  # on hover, show info for all data series for that x-value
    )

    return fig


@app.callback(Output('combined_chart', 'figure'),
              [Input('interval-component', 'n_intervals')])
def update_combined(n):
    return visualized_combined()


def visualized_news():
    df = pd.read_csv(DATABASE_PATH)

    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)

    fig = make_subplots(shared_xaxes=True, vertical_spacing=0.02)

    # Calculate the range for the last day as default time range
    latest_date = df.index.max()  # get the latest date in your data
    one_days_ago = latest_date - timedelta(days=1)

    fig.add_trace(go.Scatter(x=df.index, y=df["news_bullish"],
                             name='News bullish', visible='legendonly'))
    fig.add_trace(go.Scatter(x=df.index, y=df["news_bearish"],
                             name='News bearish', visible='legendonly'))
    fig.add_trace(go.Scatter(x=df.index, y=df["news_positive_polarity"],
                             name='Positive Polarity'))
    fig.add_trace(go.Scatter(x=df.index, y=df["news_negative_polarity"],
                             name='Negative polarity'))
    fig.add_trace(go.Scatter(x=df.index, y=df["news_positive_count"],
                             name='Positive Count', visible='legendonly'))
    fig.add_trace(go.Scatter(x=df.index, y=df["news_negative_count"],
                             name='negative count', visible='legendonly'))

    fig.update_yaxes(tickfont=dict(color=COLORS['white']), side='right', showgrid=False)
    fig.update_xaxes(
        showgrid=False,
        rangeselector=dict(
            buttons=list([
                dict(count=1, label="1d", step="day", stepmode="backward"),
                dict(count=7, label="7d", step="day", stepmode="backward"),
                dict(count=1, label="1m", step="month", stepmode="backward"),
                dict(step="all")
            ]),
            bgcolor=COLORS['background'],  # Add your preferred color here
            activecolor=COLORS['lightgray'],  # Change color of the active button
            x=0.0,  # x position of buttons
            y=1.1,  # y position of buttons
        ),
        type="date"
    )
    fig.update_layout(
        xaxis_range=[one_days_ago, latest_date],
        title={
            'text': "News",
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {
                'color': COLORS['white'],
                'size': 24
            }
        },
        yaxis_title='Value',
        plot_bgcolor=COLORS['black_chart'],
        paper_bgcolor=COLORS['background'],
        font=dict(
            color=COLORS['white'],
            size=12
        ),
        legend=dict(orientation="h",  # horizontal legend
                    yanchor="bottom",
                    y=1.02,  # put it a bit above the bottom of the plot
                    xanchor="right",
                    x=1),  # put it to the right of the plot
        hovermode="x"  # on hover, show info for all data series for that x-value
    )

    return fig


@app.callback(Output('news_chart', 'figure'),
              [Input('interval-component', 'n_intervals')])
def update_news(n):
    return visualized_news()


def visualized_youtube():
    df = pd.read_csv(DATABASE_PATH)

    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)

    # Calculate the range for the last day as default time range
    latest_date = df.index.max()  # get the latest date in your data
    seven_days_ago = latest_date - timedelta(days=7)

    fig = make_subplots(shared_xaxes=True, vertical_spacing=0.02)

    fig.add_trace(go.Scatter(x=df.index, y=df["youtube_bullish"],
                             name='YouTube bullish', visible='legendonly'))
    fig.add_trace(go.Scatter(x=df.index, y=df["youtube_bearish"],
                             name='YouTube bearish', visible='legendonly'))
    fig.add_trace(go.Scatter(x=df.index, y=df["last_24_youtube"],
                             name='Number of Video in 24h'))

    fig.update_yaxes(tickfont=dict(color=COLORS['white']), side='right', showgrid=False)
    fig.update_xaxes(
        showgrid=False,
        rangeselector=dict(
            buttons=list([
                dict(count=1, label="1d", step="day", stepmode="backward"),
                dict(count=7, label="7d", step="day", stepmode="backward"),
                dict(count=1, label="1m", step="month", stepmode="backward"),
                dict(step="all")
            ]),
            bgcolor=COLORS['background'],  # Add your preferred color here
            activecolor=COLORS['lightgray'],  # Change color of the active button
            x=0.0,  # x position of buttons
            y=1.1,  # y position of buttons
        ),
        type="date"
    )
    fig.update_layout(
        xaxis_range=[seven_days_ago, latest_date],
        title={
            'text': "Youtube",
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {
                'color': COLORS['white'],
                'size': 24
            }
        },
        yaxis_title='Value',
        plot_bgcolor=COLORS['black_chart'],
        paper_bgcolor=COLORS['background'],
        font=dict(
            color=COLORS['white'],
            size=12
        ),
        legend=dict(orientation="h",  # horizontal legend
                    yanchor="bottom",
                    y=1.02,  # put it a bit above the bottom of the plot
                    xanchor="right",
                    x=1),  # put it to the right of the plot
        hovermode="x"  # on hover, show info for all data series for that x-value
    )

    return fig


@app.callback(Output('youtube_chart', 'figure'),
              [Input('interval-component', 'n_intervals')])
def update_youtube(n):
    return visualized_youtube()


def visualized_reddit():
    df = pd.read_csv(DATABASE_PATH)

    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)

    # Calculate the range for the last day as default time range
    latest_date = df.index.max()  # get the latest date in your data
    seven_days_ago = latest_date - timedelta(days=7)

    fig = make_subplots(shared_xaxes=True, vertical_spacing=0.02)

    fig.add_trace(go.Scatter(x=df.index, y=df["reddit_bullish"],
                             name='Reddit bullish', visible='legendonly'))
    fig.add_trace(go.Scatter(x=df.index, y=df["reddit_bearish"],
                             name='Reddit bearish', visible='legendonly'))
    fig.add_trace(go.Scatter(x=df.index, y=df["reddit_count_bitcoin_posts_24h"],
                             name='Count bitcoin posts 24h', visible='legendonly'))
    fig.add_trace(go.Scatter(x=df.index, y=df["reddit_activity_24h"],
                             name='Reddit activity'))

    fig.update_yaxes(tickfont=dict(color=COLORS['white']), side='right', showgrid=False)
    fig.update_xaxes(
        showgrid=False,
        rangeselector=dict(
            buttons=list([
                dict(count=1, label="1d", step="day", stepmode="backward"),
                dict(count=7, label="7d", step="day", stepmode="backward"),
                dict(count=1, label="1m", step="month", stepmode="backward"),
                dict(step="all")
            ]),
            bgcolor=COLORS['background'],  # Add your preferred color here
            activecolor=COLORS['lightgray'],  # Change color of the active button
            x=0.0,  # x position of buttons
            y=1.1,  # y position of buttons
        ),
        type="date"
    )
    fig.update_layout(
        xaxis_range=[seven_days_ago, latest_date],
        title={
            'text': "Reddit",
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {
                'color': COLORS['white'],
                'size': 24
            }
        },
        yaxis_title='Value',
        plot_bgcolor=COLORS['black_chart'],
        paper_bgcolor=COLORS['background'],
        font=dict(
            color=COLORS['white'],
            size=12
        ),
        legend=dict(orientation="h",  # horizontal legend
                    yanchor="bottom",
                    y=1.02,  # put it a bit above the bottom of the plot
                    xanchor="right",
                    x=1),  # put it to the right of the plot
        hovermode="x"  # on hover, show info for all data series for that x-value
    )

    return fig


@app.callback(Output('reddit_chart', 'figure'),
              [Input('interval-component', 'n_intervals')])
def reddit_google(n):
    return visualized_reddit()


def visualized_google():
    df = pd.read_csv(DATABASE_PATH)

    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)

    fig = make_subplots(shared_xaxes=True, vertical_spacing=0.02)

    # Calculate the range for the last day as default time range
    latest_date = df.index.max()  # get the latest date in your data
    seven_days_ago = latest_date - timedelta(days=7)

    fig.add_trace(go.Scatter(x=df.index, y=df["hourly_google_search"], name='Hourly Google Search'))
    fig.add_trace(go.Scatter(x=df.index, y=df["google_search_bullish"], name='Google Bullish', visible='legendonly'))
    fig.add_trace(go.Scatter(x=df.index, y=df["google_search_bearish"], name='Google Bearish', visible='legendonly'))

    fig.update_yaxes(tickfont=dict(color=COLORS['white']), side='right', showgrid=False)
    fig.update_xaxes(
        showgrid=False,
        rangeselector=dict(
            buttons=list([
                dict(count=1, label="1d", step="day", stepmode="backward"),
                dict(count=7, label="7d", step="day", stepmode="backward"),
                dict(count=1, label="1m", step="month", stepmode="backward"),
                dict(step="all")
            ]),
            bgcolor=COLORS['background'],  # Add your preferred color here
            activecolor=COLORS['lightgray'],  # Change color of the active button
            x=0.0,  # x position of buttons
            y=1.1,  # y position of buttons
        ),
        type="date"
    )
    fig.update_layout(
        xaxis_range=[seven_days_ago, latest_date],
        title={
            'text': "Google search",
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {
                'color': COLORS['white'],
                'size': 24
            }
        },
        yaxis_title='Value',
        plot_bgcolor=COLORS['black_chart'],
        paper_bgcolor=COLORS['background'],
        font=dict(
            color=COLORS['white'],
            size=12
        ),
        legend=dict(orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1),
        hovermode="x"
    )

    return fig


@app.callback(Output('google_chart', 'figure'),
              [Input('interval-component', 'n_intervals')])
def update_google(n):
    return visualized_google()


def visualized_richest():
    df = pd.read_csv(DATABASE_PATH)

    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)

    # Calculate the range for the last day as default time range
    latest_date = df.index.max()  # get the latest date in your data
    seven_days_ago = latest_date - timedelta(days=7)

    fig = make_subplots(shared_xaxes=True, vertical_spacing=0.02)

    fig.add_trace(go.Scatter(x=df.index, y=df["richest_addresses_bullish"],
                             name='Richest bullish', visible='legendonly'))
    fig.add_trace(go.Scatter(x=df.index, y=df["richest_addresses_bearish"],
                             name='Richest bearish', visible='legendonly'))
    fig.add_trace(go.Scatter(x=df.index, y=df["richest_addresses_total_received"],
                             name='Sent in last 24H'))
    fig.add_trace(go.Scatter(x=df.index, y=df["richest_addresses_total_sent"],
                             name='Received in last 24H'))

    fig.update_yaxes(tickfont=dict(color=COLORS['white']), side='right', showgrid=False)
    fig.update_xaxes(
        showgrid=False,
        rangeselector=dict(
            buttons=list([
                dict(count=1, label="1d", step="day", stepmode="backward"),
                dict(count=7, label="7d", step="day", stepmode="backward"),
                dict(count=1, label="1m", step="month", stepmode="backward"),
                dict(step="all")
            ]),
            bgcolor=COLORS['background'],  # Add your preferred color here
            activecolor=COLORS['lightgray'],  # Change color of the active button
            x=0.0,  # x position of buttons
            y=1.1,  # y position of buttons
        ),
        type="date"
    )
    fig.update_layout(
        xaxis_range=[seven_days_ago, latest_date],
        title={
            'text': "Richest Addresses",
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {
                'color': COLORS['white'],
                'size': 24
            }
        },
        yaxis_title='Value',
        plot_bgcolor=COLORS['black_chart'],
        paper_bgcolor=COLORS['background'],
        font=dict(
            color=COLORS['white'],
            size=12
        ),
        legend=dict(orientation="h",  # horizontal legend
                    yanchor="bottom",
                    y=1.02,  # put it a bit above the bottom of the plot
                    xanchor="right",
                    x=1),  # put it to the right of the plot
        hovermode="x"  # on hover, show info for all data series for that x-value
    )

    return fig


@app.callback(Output('richest_chart', 'figure'),
              [Input('interval-component', 'n_intervals')])
def update_richest(n):
    return visualized_richest()


def visualize_prediction():
    df = pd.read_csv(DATABASE_PATH)

    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)

    # Calculate the range for the last day as default time range
    latest_date = df.index.max()  # get the latest date in your data
    one_day_ago = latest_date - timedelta(days=1)

    fig = make_subplots(shared_xaxes=True, vertical_spacing=0.02)

    fig.add_trace(go.Scatter(x=df.index, y=df["predicted_price"], name='Predicted price'))
    fig.add_trace(go.Scatter(x=df.index, y=df["actual_price_12h_later"], name='Actual price'))
    fig.add_trace(go.Scatter(x=df.index, y=df["prediction_bullish"], name='Prediction bullish', visible='legendonly'))
    fig.add_trace(go.Scatter(x=df.index, y=df["prediction_bearish"], name='Prediction bearish', visible='legendonly'))

    fig.update_yaxes(tickfont=dict(color=COLORS['white']), side='right', showgrid=False)
    fig.update_xaxes(
        showgrid=False,
        rangeselector=dict(
            buttons=list([
                dict(count=1, label="1d", step="day", stepmode="backward"),
                dict(count=7, label="7d", step="day", stepmode="backward"),
                dict(count=1, label="1m", step="month", stepmode="backward"),
                dict(step="all")
            ]),
            bgcolor=COLORS['background'],  # Add your preferred color here
            activecolor=COLORS['lightgray'],  # Change color of the active button
            x=0.0,  # x position of buttons
            y=1.1,  # y position of buttons
        ),
        type="date"
    )

    fig.update_layout(
        xaxis_range=[one_day_ago, latest_date],
        title={
            'text': "Prediction",
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {
                'color': COLORS['white'],
                'size': 24
            }
        },
        yaxis_title='Value',
        plot_bgcolor=COLORS['black_chart'],
        paper_bgcolor=COLORS['background'],
        font=dict(
            color=COLORS['white'],
            size=12
        ),
        legend=dict(orientation="h",  # horizontal legend
                    yanchor="bottom",
                    y=1.02,  # put it a bit above the bottom of the plot
                    xanchor="right",
                    x=1),  # put it to the right of the plot
        hovermode="x"  # on hover, show info for all data series for that x-value
    )

    return fig


@app.callback(Output('prediction_chart', 'figure'),
              [Input('interval-component', 'n_intervals')])
def update_prediction(n):
    return visualize_prediction()


def visualize_macro():
    df = pd.read_csv(DATABASE_PATH)

    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)

    fig = make_subplots(shared_xaxes=True, vertical_spacing=0.02)

    fig.add_trace(go.Scatter(x=df.index, y=df['fed_rate_m_to_m'], name='Interest Rate M to M'))
    fig.add_trace(go.Scatter(x=df.index, y=df["cpi_m_to_m"], name='CPI M to M'))
    fig.add_trace(go.Scatter(x=df.index, y=df["ppi_m_to_m"], name='PPI M to M'))
    fig.add_trace(go.Scatter(x=df.index, y=df["macro_bullish"], name='Macro Bullish', visible='legendonly'))
    fig.add_trace(go.Scatter(x=df.index, y=df["macro_bearish"], name='Macro Bearish', visible='legendonly'))

    fig.update_yaxes(tickfont=dict(color=COLORS['white']), side='right', showgrid=False)
    fig.update_xaxes(
        showgrid=False,
        rangeselector=dict(
            buttons=list([
                dict(count=1, label="1d", step="day", stepmode="backward"),
                dict(count=7, label="7d", step="day", stepmode="backward"),
                dict(count=1, label="1m", step="month", stepmode="backward"),
                dict(step="all")
            ]),
            bgcolor=COLORS['background'],  # Add your preferred color here
            activecolor=COLORS['lightgray'],  # Change color of the active button
            x=0.0,  # x position of buttons
            y=1.1,  # y position of buttons
        ),
        type="date"
    )
    fig.update_layout(
        title={
            'text': "Macro Economic",
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {
                'color': COLORS['white'],
                'size': 24
            }
        },
        yaxis_title='Value',
        plot_bgcolor=COLORS['black_chart'],
        paper_bgcolor=COLORS['background'],
        font=dict(
            color=COLORS['white'],
            size=12
        ),
        legend=dict(orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1),
        hovermode="x",
    )

    return fig


@app.callback(Output('macro_chart', 'figure'),
              [Input('interval-component', 'n_intervals')])
def update_macro(n):
    return visualize_macro()


def visualize_trade_results():
    df = pd.read_csv(TRADE_RESULT_PATH)

    # Create an empty figure
    fig = go.Figure()

    # Add a bar chart for PNL
    fig.add_trace(go.Bar(
        x=df['weighted_score_category'],
        y=(df["PNL"] / 1000),
        name='PNL(K)',
        marker=dict(color=COLORS['lightgray']),
        text=df["PNL"],
        hoverinfo='none'
    ))

    fig.add_trace(go.Bar(x=df['weighted_score_category'], y=df["long_trades"],
                         name='Long trades', marker=dict(color=COLORS['green_chart']),
                         text=df["long_trades"].map('long {}'.format),
                         hoverinfo='none'
                         ))

    fig.add_trace(go.Bar(x=df['weighted_score_category'], y=df["short_trades"],
                         name='Short trades', marker=dict(color=COLORS['red_chart']),
                         text=df["short_trades"].map('short {}'.format),
                         hoverinfo='none'
                         ))

    fig.add_trace(go.Bar(x=df['weighted_score_category'], y=df["win_trades"],
                         name='Win trades', marker=dict(color='#006700'),
                         text=df["win_trades"].map('win {}'.format),
                         hoverinfo='none'
                         ))

    fig.add_trace(go.Bar(x=df['weighted_score_category'], y=df["loss_trades"],
                         name='Loss trades', marker=dict(color='#9a0000'),
                         text=df["loss_trades"].map('loss {}'.format),
                         hoverinfo='none'
                         ))

    # Add a bar chart for number_of_trades
    # fig.add_trace(go.Bar(x=df['weighted_score_category'], y=df["total_trades"],
    #                    name='Number of Trades'))

    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=False)
    fig.update_layout(
        title={
            'text': "Trade Results",
            'y': 0.95,  # Adjust this as needed. Default is 0.9
            'x': 0.5,  # Places the title in the center
            'xanchor': 'center',  # ensures the title remains at center when resizing
            'yanchor': 'top',  # ensures the title remains at top when resizing
            'font': {
                'color': COLORS['white'],  # Change this to your desired color
                'size': 24  # Change this to your desired size
            }
        },
        xaxis_title='Model Category',
        yaxis_title='Value',
        barmode='group',
        plot_bgcolor=COLORS['black_chart'],
        paper_bgcolor=COLORS['background'],
        font=dict(
            color=COLORS['white'],  # Change this to your desired color
            size=11
        ),
        legend=dict(orientation="h",
                    yanchor="bottom",
                    y=1.02,  # put it a bit above the bottom of the plot
                    xanchor="right",
                    x=1),
        hovermode="x"  # on hover, show info for all data series for that x-value
    )

    return fig


@app.callback(Output('trade_results_chart', 'figure'),
              [Input('interval-component', 'n_intervals')])
def update_trade_result(n):
    return visualize_trade_results()


def read_gauge_chart_data():
    database = read_database()
    latest_info_saved = pd.read_csv(LATEST_INFO_SAVED).squeeze("columns")

    data_dict = {
        'trading_state': latest_info_saved.iloc[0]['latest_trading_state'],
        'macro_bullish': database['macro_bullish'][-1],
        'macro_bearish': database['macro_bearish'][-1],
        'prediction_bullish': database['prediction_bullish'][-1],
        'prediction_bearish': database['prediction_bearish'][-1],
        'technical_bullish': database['technical_bullish'][-1],
        'technical_bearish': database['technical_bearish'][-1],
        'richest_addresses_bullish': database['richest_addresses_bullish'][-1],
        'richest_addresses_bearish': database['richest_addresses_bearish'][-1],
        'google_search_bullish': database['google_search_bullish'][-1],
        'google_search_bearish': database['google_search_bearish'][-1],
        'reddit_bullish': database['reddit_bullish'][-1],
        'reddit_bearish': database['reddit_bearish'][-1],
        'youtube_bullish': database['youtube_bullish'][-1],
        'youtube_bearish': database['youtube_bearish'][-1],
        'news_bullish': database['news_bullish'][-1],
        'news_bearish': database['news_bearish'][-1],
        'weighted_score_up': latest_info_saved.iloc[0]['latest_weighted_score_up'],
        'weighted_score_down': latest_info_saved.iloc[0]['latest_weighted_score_down'],
    }

    if data_dict['trading_state'] in ['long', 'short']:
        data_dict.update({
            'order_book_bullish': latest_info_saved.iloc[0]['order_book_hit_profit'],
            'order_book_bearish': latest_info_saved.iloc[0]['order_book_hit_loss']
        })
    else:
        data_dict.update({
            'order_book_bullish': database['order_book_bullish'][-1],
            'order_book_bearish': database['order_book_bearish'][-1]
        })

    return data_dict


# noinspection PyTypeChecker
def create_gauge_charts():
    data_dict = read_gauge_chart_data()
    fig = make_subplots(rows=2, cols=5,
                        specs=[[{"type": "indicator"}] * 5] * 2,
                        subplot_titles=["Macro Sentiment", "Order Book", "Prediction", "Technical Analysis",
                                        "Richest Addresses", "Google Search Trend", "Reddit Sentiment",
                                        "YouTube Sentiment", "News Sentiment", "Combined Score"])

    fig.add_trace(create_gauge_chart(
        data_dict['macro_bullish'], data_dict['macro_bearish'], 'macro'), row=1, col=1)
    fig.add_trace(create_gauge_chart(
        data_dict['order_book_bullish'], data_dict['order_book_bearish'], 'order_book'), row=1, col=2)
    fig.add_trace(create_gauge_chart(
        data_dict['prediction_bullish'], data_dict['prediction_bearish'],
        'predicted_price'), row=1, col=3)
    fig.add_trace(create_gauge_chart(
        data_dict['technical_bullish'], data_dict['technical_bearish'],
        'technical_analysis'), row=1, col=4)
    fig.add_trace(create_gauge_chart(data_dict['richest_addresses_bullish'], data_dict['richest_addresses_bearish'],
                                     'richest_addresses'), row=1, col=5)
    fig.add_trace(create_gauge_chart(
        data_dict['google_search_bullish'], data_dict['google_search_bearish'],
        'google_search'), row=2, col=1)
    fig.add_trace(create_gauge_chart(
        data_dict['reddit_bullish'], data_dict['reddit_bearish'], 'reddit'), row=2, col=2)
    fig.add_trace(create_gauge_chart(
        data_dict['youtube_bullish'], data_dict['youtube_bearish'], 'youtube'), row=2, col=3)
    fig.add_trace(create_gauge_chart(
        data_dict['news_bullish'], data_dict['news_bearish'], 'sentiment_of_news'), row=2, col=4)
    fig.add_trace(create_gauge_chart(
        data_dict['weighted_score_up'], data_dict['weighted_score_down'],
        'weighted_score'), row=2, col=5)

    fig.update_layout(plot_bgcolor=COLORS['background'], paper_bgcolor=COLORS['background'])

    for annotation in fig['layout']['annotations']:
        if annotation['text'] == "Combined Score":
            annotation['font'] = dict(color=COLORS['white'], size=26,
                                      )  # set color, size, and boldness of the title
        else:
            annotation['font'] = dict(color=COLORS['white'], size=15)

    return fig


@app.callback(Output('live-update-graph', 'figure'),
              [Input('interval-component', 'n_intervals')])
def update_gauge_chart_live(n):
    fig = create_gauge_charts()
    return fig


def read_layout_data():
    database = read_database()
    latest_info_saved = pd.read_csv(LATEST_INFO_SAVED).squeeze("columns")
    fed_announcement, cpi_announcement, ppi_announcement = calculate_upcoming_events()

    layout_data = {
        "trading_state": f'{latest_info_saved["latest_trading_state"][0]}',
        "fed_rate_m_to_m": f'Fed rate MtM: {float(latest_info_saved["fed_rate_m_to_m"][0])}',
        "cpi_m_to_m": f'{float(latest_info_saved["cpi_m_to_m"][0])}',
        "ppi_m_to_m": f'{float(latest_info_saved["ppi_m_to_m"][0])}',
        "bid_volume": int(database['bid_volume'][-1]),
        "ask_volume": int(database['ask_volume'][-1]),
        "predicted_price": database['predicted_price'][-1],
        "current_price": get_bitcoin_price(),
        "rsi": float(latest_info_saved['latest_rsi'][0]),
        "over_200EMA": latest_info_saved['over_200EMA'][0],
        "MACD_uptrend": database['technical_potential_up_trend'][-1],
        "bb_MA_distance": latest_info_saved['bb_band_MA_distance'][0],
        "BTC_received": int(latest_info_saved['total_received_coins_in_last_24'][0]),
        "BTC_send": int(latest_info_saved['total_sent_coins_in_last_24'][0]),
        "positive_news_polarity_change": round(latest_info_saved['positive_news_polarity_change'][0], 0),
        "negative_news_polarity_change": round(latest_info_saved['negative_news_polarity_change'][0], 0),
        "fed_announcement": fed_announcement,
        "cpi_announcement": cpi_announcement,
        "ppi_announcement": ppi_announcement
    }

    return layout_data


def create_initial_layout_data():
    layout_data = read_layout_data()

    # Extracting data from layout_data dictionary
    initial_layout_data = {
        'trading_state': layout_data["trading_state"],
        'fed_rate_m_to_m': layout_data["fed_rate_m_to_m"],
        'cpi_m_to_m': layout_data["cpi_m_to_m"],
        'ppi_m_to_m': layout_data["ppi_m_to_m"],
        'bid_volume': layout_data["bid_volume"],
        'ask_volume': layout_data["ask_volume"],
        'predicted_price': layout_data["predicted_price"],
        'current_price': layout_data["current_price"],
        'rsi': layout_data["rsi"],
        'over_200EMA': layout_data["over_200EMA"],
        'MACD_uptrend': layout_data["MACD_uptrend"],
        'bb_MA_distance': layout_data["bb_MA_distance"],
        'BTC_received': layout_data["BTC_received"],
        'BTC_send': layout_data["BTC_send"],
        'positive_news_polarity_change': layout_data["positive_news_polarity_change"],
        'negative_news_polarity_change': layout_data["negative_news_polarity_change"],
        'fed_announcement': layout_data["fed_announcement"],
        'cpi_announcement': layout_data["cpi_announcement"],
        'ppi_announcement': layout_data["ppi_announcement"],
    }

    return initial_layout_data


@app.callback(
    [Output('fed-rate', 'children'),
     Output('cpi-rate', 'children'),
     Output('ppi-rate', 'children'),
     Output('fed-announcement', 'children'),
     Output('cpi-announcement', 'children'),
     Output('ppi-announcement', 'children'),
     Output('trading-state', 'children'),
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
        ppi_announcement, f'T State: {trading_state}', f'Bid vol: {bid_volume}', \
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


def generate_tooltips():
    return [
        dbc.Tooltip("Federal interest rate month to month increase", target='fed-rate', placement="bottom"),
        dbc.Tooltip("Consumer Price Index month to month increase", target='cpi-rate', placement="bottom"),
        dbc.Tooltip("Producer Price Index month to month increase", target='ppi-rate', placement="bottom"),
        dbc.Tooltip("Federal announcement details", target='fed-announcement', placement="bottom"),
        dbc.Tooltip("CPI announcement details", target='cpi-announcement', placement="bottom"),
        dbc.Tooltip("PPI announcement details", target='ppi-announcement', placement="bottom"),
        dbc.Tooltip("Trading state details", target='trading-state', placement="bottom"),
        dbc.Tooltip("Bid volume details", target='bid-volume', placement="bottom"),
        dbc.Tooltip("Ask volume details", target='ask-volume', placement="bottom"),
        dbc.Tooltip("Predicted price details", target='predicted-price', placement="bottom"),
        dbc.Tooltip("Current price details", target='current-price', placement="bottom"),
        dbc.Tooltip("Price difference details", target='price-difference', placement="bottom"),
        dbc.Tooltip("Relative Strength Index details", target='rsi', placement="bottom"),
        dbc.Tooltip("Details over 200EMA", target='over-200ema', placement="bottom"),
        dbc.Tooltip("MACD up trend details", target='macd-trend', placement="bottom"),
        dbc.Tooltip("Bollinger Bands distance details", target='bb-distance', placement="bottom"),
        dbc.Tooltip("Details of rich receiving Bitcoin", target='btc-received', placement="bottom"),
        dbc.Tooltip("Details of rich sending Bitcoin", target='btc-sent', placement="bottom"),
        dbc.Tooltip("Positive news increase details", target='positive-news', placement="bottom"),
        dbc.Tooltip("Negative news increase details", target='negative-news', placement="bottom"),
        dbc.Tooltip("Macro sentiment is a measure of the overall sentiment towards Bitcoin. "
                    "This sentiment can be influenced by a variety of factors, such as the current economic climate, "
                    "the sentiment towards cryptocurrencies in general, and news events related to Bitcoin.",
                    target='macro'),
        dbc.Tooltip("Order Book represents the interest of buyers and sellers for Bitcoin at various price levels. "
                    "A higher number of buy orders compared to sell orders can indicate bullish sentiment.",
                    target='order_book'),
        dbc.Tooltip("This is the prediction of the future price of Bitcoin based on our algorithm. "
                    "A positive number indicates a bullish prediction.",
                    target='predicted_price'),
        dbc.Tooltip(
            "Technical Analysis is a method of predicting the future price of Bitcoin based on past market data, "
            "primarily price and volume. A positive number indicates a bullish technical analysis.",
            target='technical_analysis'),
        dbc.Tooltip("This shows the actions of the richest Bitcoin addresses. If they are buying more than selling, "
                    "it could indicate bullish sentiment.",
                    target='richest_addresses'),
        dbc.Tooltip("Google Search Trend indicates the interest over time for Bitcoin on Google's search engine. "
                    "An increase in search interest may indicate bullish sentiment.",
                    target='google_search'),
        dbc.Tooltip("Reddit Sentiment represents the overall sentiment towards Bitcoin in Reddit comments. "
                    "A positive number indicates a bullish sentiment.",
                    target='reddit'),
        dbc.Tooltip("YouTube Sentiment represents the overall sentiment towards Bitcoin in YouTube comments. "
                    "A positive number indicates a bullish sentiment.",
                    target='youtube'),
        dbc.Tooltip("News Sentiment represents the overall sentiment towards Bitcoin in news articles. "
                    "A positive number indicates a bullish sentiment.",
                    target='sentiment_of_news'),
        dbc.Tooltip("Weighted Score is a composite measure that takes into account all the factors above. "
                    "A positive score indicates bullish sentiment.",
                    target='weighted_score'),
    ]


def create_popover():
    popover = dbc.Popover(
        [
            dbc.PopoverHeader("Next update time"),
            dbc.PopoverBody("This shows the next updating time"),
        ],
        id="popover",
        target="progress",
        trigger="click",
        placement="auto",
    )

    return popover


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
    popover = create_popover()
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
        children=[timer_interval_component, interval_component, popover] + html_divs,
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
