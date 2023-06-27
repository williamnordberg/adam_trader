import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash
from dash import dcc
from dash import html
import logging
from dash.dependencies import Input, Output


log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
TRADE_RESULT_PATH = 'data/trades_results.csv'
DATABASE_PATH = 'data/database.csv'


def visualize_database_ten_rows():
    df = pd.read_csv(DATABASE_PATH)

    # Convert the 'date' column to datetime objects
    df['date'] = pd.to_datetime(df['date'])

    # Convert boolean columns to integers
    bool_columns = ["technical_potential_up_reversal_bullish",
                    "technical_potential_down_reversal_bearish", "technical_potential_up_trend"]
    df[bool_columns] = df[bool_columns].astype(int)

    # Normalize the data
    normalized_df = (df - df.min()) / (df.max() - df.min())

    # Set the 'date' column as the index
    df.set_index('date', inplace=True)

    # Create a 10-row subplot layout
    fig = make_subplots(rows=10, cols=1, shared_xaxes=True, vertical_spacing=0.02)

    # Chart 1
    fig.add_trace(go.Scatter(x=df.index, y=normalized_df["interest_rate"],
                             mode='lines', name='Interest Rate'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=normalized_df["cpi_m_to_m"],
                             mode='lines', name='cpi_m_to_m'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=normalized_df["ppi_m_to_m"],
                             mode='lines', name='ppi_m_to_m'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=normalized_df["macro_bullish"],
                             mode='lines', name='macro_bullish'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=normalized_df["macro_bearish"],
                             mode='lines', name='macro_bearish'), row=1, col=1)

    # Chart 2
    fig.add_trace(go.Scatter(x=df.index, y=normalized_df["bid_volume"],
                             mode='lines', name='Bid Volume'), row=2, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=normalized_df["ask_volume"],
                             mode='lines', name='Ask Volume'), row=2, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=normalized_df["order_book_bullish"],
                             mode='lines', name='Order Book Bullish'), row=2, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=normalized_df["order_book_bearish"],
                             mode='lines', name='Order Book Bearish'), row=2, col=1)

    # Chart 3
    fig.add_trace(go.Scatter(x=df.index, y=normalized_df["predicted_price"],
                             mode='lines', name='Predicted Price'), row=3, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=normalized_df["prediction_bullish"],
                             mode='lines', name='Prediction Bullish'), row=3, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=normalized_df["prediction_bearish"],
                             mode='lines', name='Prediction Bearish'), row=3, col=1)

    # Chart 4
    fig.add_trace(go.Scatter(x=df.index, y=normalized_df["technical_potential_up_reversal_bullish"],
                             mode='lines', name='Technical Up Reversal Bullish'), row=4, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=normalized_df["technical_potential_down_reversal_bearish"],
                             mode='lines', name='Technical Down Reversal Bearish'), row=4, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=normalized_df["technical_potential_up_trend"],
                             mode='lines', name='Technical Up Trend'), row=4, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=normalized_df["technical_bullish"],
                             mode='lines', name='Technical Bullish'), row=4, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=normalized_df["technical_bearish"],
                             mode='lines', name='technical_bearish'), row=4, col=1)

    # Chart 5
    fig.add_trace(go.Scatter(x=df.index, y=normalized_df["richest_addresses_total_received"],
                             mode='lines', name='Richest Addresses Total Received'), row=5, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=normalized_df["richest_addresses_total_sent"],
                             mode='lines', name='Richest Addresses Total Sent'), row=5, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=normalized_df["richest_addresses_bullish"],
                             mode='lines', name='Richest Addresses Bullish'), row=5, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=normalized_df["richest_addresses_bearish"],
                             mode='lines', name='Richest Addresses Bearish'), row=5, col=1)

    # Chart 6
    fig.add_trace(go.Scatter(x=df.index, y=normalized_df["hourly_google_search"],
                             mode='lines', name='Hourly Google Search'), row=6, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=normalized_df["google_search_bullish"],
                             mode='lines', name='Google Search Bullish'), row=6, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=normalized_df["google_search_bearish"],
                             mode='lines', name='Google Search Bearish'), row=6, col=1)

    # Chart 7
    fig.add_trace(go.Scatter(x=df.index, y=normalized_df["reddit_count_bitcoin_posts_24h"],
                             mode='lines', name='Reddit Count Bitcoin Posts 24h'), row=7, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=normalized_df["reddit_activity_24h"],
                             mode='lines', name='Reddit Activity 24h'), row=7, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=normalized_df["reddit_bullish"],
                             mode='lines', name='Reddit Bullish'), row=7, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=normalized_df["reddit_bearish"],
                             mode='lines', name='Reddit Bearish'), row=7, col=1)

    # Chart 8
    fig.add_trace(go.Scatter(x=df.index, y=normalized_df["last_24_youtube"],
                             mode='lines', name='Last 24 YouTube'), row=8, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=normalized_df["youtube_bullish"],
                             mode='lines', name='YouTube Bullish'), row=8, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=normalized_df["youtube_bearish"],
                             mode='lines', name='YouTube Bearish'), row=8, col=1)

    # Chart 9
    fig.add_trace(go.Scatter(x=df.index, y=normalized_df["news_positive_polarity"],
                             mode='lines', name='News Positive Polarity'), row=9, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=normalized_df["news_negative_polarity"],
                             mode='lines', name='News Negative Polarity'), row=9, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=normalized_df["news_positive_count"],
                             mode='lines', name='News Positive Count'), row=9, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=normalized_df["news_negative_count"],
                             mode='lines', name='News Negative Count'), row=9, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=normalized_df["news_bullish"],
                             mode='lines', name='News Bullish'), row=9, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=normalized_df["news_bearish"],
                             mode='lines', name='News Bearish'), row=9, col=1)

    # Chart 10
    fig.add_trace(go.Scatter(x=df.index, y=normalized_df["weighted_score_up"],
                             mode='lines', name='weighted_score_up'), row=10, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=normalized_df["weighted_score_down"],
                             mode='lines', name='weighted_score_down'), row=10, col=1)

    fig.show()


def visualize_database_two_rows():
    df = pd.read_csv(DATABASE_PATH)

    # Convert the 'date' column to datetime objects
    df['date'] = pd.to_datetime(df['date'])

    # Convert boolean columns to integers
    bool_columns = ["technical_potential_up_reversal_bullish",
                    "technical_potential_down_reversal_bearish", "technical_potential_up_trend"]
    df[bool_columns] = df[bool_columns].astype(int)

    # Normalize the data
    normalized_df = (df - df.min()) / (df.max() - df.min())

    # Set the 'date' column as the index
    df.set_index('date', inplace=True)

    # Create a 10-row subplot layout
    fig = make_subplots(rows=2, cols=5, shared_xaxes=True, vertical_spacing=0.02)

    # Chart 1
    fig.add_trace(go.Scatter(x=df.index, y=normalized_df["interest_rate"],
                             mode='lines', name='Interest Rate'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=normalized_df["cpi_m_to_m"],
                             mode='lines', name='cpi_m_to_m'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=normalized_df["ppi_m_to_m"],
                             mode='lines', name='ppi_m_to_m'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=normalized_df["macro_bullish"],
                             mode='lines', name='macro_bullish'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=normalized_df["macro_bearish"],
                             mode='lines', name='macro_bearish'), row=1, col=1)

    # Chart 2
    fig.add_trace(go.Scatter(x=df.index, y=normalized_df["bid_volume"],
                             mode='lines', name='Bid Volume'), row=1, col=2)
    fig.add_trace(go.Scatter(x=df.index, y=normalized_df["ask_volume"],
                             mode='lines', name='Ask Volume'), row=1, col=2)
    fig.add_trace(go.Scatter(x=df.index, y=normalized_df["order_book_bullish"],
                             mode='lines', name='Order Book Bullish'), row=1, col=2)
    fig.add_trace(go.Scatter(x=df.index, y=normalized_df["order_book_bearish"],
                             mode='lines', name='Order Book Bearish'), row=1, col=2)

    # Chart 3
    fig.add_trace(go.Scatter(x=df.index, y=normalized_df["predicted_price"],
                             mode='lines', name='Predicted Price'), row=1, col=3)
    fig.add_trace(go.Scatter(x=df.index, y=normalized_df["prediction_bullish"],
                             mode='lines', name='Prediction Bullish'), row=1, col=3)
    fig.add_trace(go.Scatter(x=df.index, y=normalized_df["prediction_bearish"],
                             mode='lines', name='Prediction Bearish'), row=1, col=3)

    # Chart 4
    fig.add_trace(go.Scatter(x=df.index, y=normalized_df["technical_potential_up_reversal_bullish"],
                             mode='lines', name='Technical Up Reversal Bullish'), row=1, col=4)
    fig.add_trace(go.Scatter(x=df.index, y=normalized_df["technical_potential_down_reversal_bearish"],
                             mode='lines', name='Technical Down Reversal Bearish'), row=1, col=4)
    fig.add_trace(go.Scatter(x=df.index, y=normalized_df["technical_potential_up_trend"],
                             mode='lines', name='Technical Up Trend'), row=1, col=4)
    fig.add_trace(go.Scatter(x=df.index, y=normalized_df["technical_bullish"],
                             mode='lines', name='Technical Bullish'), row=1, col=4)
    fig.add_trace(go.Scatter(x=df.index, y=normalized_df["technical_bearish"],
                             mode='lines', name='technical_bearish'), row=1, col=4)

    # Chart 5
    fig.add_trace(go.Scatter(x=df.index, y=normalized_df["richest_addresses_total_received"],
                             mode='lines', name='Richest Addresses Total Received'), row=1, col=5)
    fig.add_trace(go.Scatter(x=df.index, y=normalized_df["richest_addresses_total_sent"],
                             mode='lines', name='Richest Addresses Total Sent'), row=1, col=5)
    fig.add_trace(go.Scatter(x=df.index, y=normalized_df["richest_addresses_bullish"],
                             mode='lines', name='Richest Addresses Bullish'), row=1, col=5)
    fig.add_trace(go.Scatter(x=df.index, y=normalized_df["richest_addresses_bearish"],
                             mode='lines', name='Richest Addresses Bearish'), row=1, col=5)

    # Chart 6
    fig.add_trace(go.Scatter(x=df.index, y=normalized_df["hourly_google_search"],
                             mode='lines', name='Hourly Google Search'), row=2, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=normalized_df["google_search_bullish"],
                             mode='lines', name='Google Search Bullish'), row=2, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=normalized_df["google_search_bearish"],
                             mode='lines', name='Google Search Bearish'), row=2, col=1)

    # Chart 7
    fig.add_trace(go.Scatter(x=df.index, y=normalized_df["reddit_count_bitcoin_posts_24h"],
                             mode='lines', name='Reddit Count Bitcoin Posts 24h'), row=2, col=2)
    fig.add_trace(go.Scatter(x=df.index, y=normalized_df["reddit_activity_24h"],
                             mode='lines', name='Reddit Activity 24h'), row=2, col=2)
    fig.add_trace(go.Scatter(x=df.index, y=normalized_df["reddit_bullish"],
                             mode='lines', name='Reddit Bullish'), row=2, col=2)
    fig.add_trace(go.Scatter(x=df.index, y=normalized_df["reddit_bearish"],
                             mode='lines', name='Reddit Bearish'), row=2, col=2)

    # Chart 8
    fig.add_trace(go.Scatter(x=df.index, y=normalized_df["last_24_youtube"],
                             mode='lines', name='Last 24 YouTube'), row=2, col=3)
    fig.add_trace(go.Scatter(x=df.index, y=normalized_df["youtube_bullish"],
                             mode='lines', name='YouTube Bullish'), row=2, col=3)
    fig.add_trace(go.Scatter(x=df.index, y=normalized_df["youtube_bearish"],
                             mode='lines', name='YouTube Bearish'), row=2, col=3)

    # Chart 9
    fig.add_trace(go.Scatter(x=df.index, y=normalized_df["news_positive_polarity"],
                             mode='lines', name='News Positive Polarity'), row=2, col=4)
    fig.add_trace(go.Scatter(x=df.index, y=normalized_df["news_negative_polarity"],
                             mode='lines', name='News Negative Polarity'), row=2, col=4)
    fig.add_trace(go.Scatter(x=df.index, y=normalized_df["news_positive_count"],
                             mode='lines', name='News Positive Count'), row=2, col=4)
    fig.add_trace(go.Scatter(x=df.index, y=normalized_df["news_negative_count"],
                             mode='lines', name='News Negative Count'), row=2, col=4)
    fig.add_trace(go.Scatter(x=df.index, y=normalized_df["news_bullish"],
                             mode='lines', name='News Bullish'), row=2, col=4)
    fig.add_trace(go.Scatter(x=df.index, y=normalized_df["news_bearish"],
                             mode='lines', name='News Bearish'), row=2, col=4)

    # Chart 10
    fig.add_trace(go.Scatter(x=df.index, y=normalized_df["weighted_score_up"],
                             mode='lines', name='weighted_score_up'), row=2, col=5)
    fig.add_trace(go.Scatter(x=df.index, y=normalized_df["weighted_score_down"],
                             mode='lines', name='weighted_score_down'), row=2, col=5)

    fig.show()


def normalize_columns(df):
    normalized_df = df.copy()

    for column in df.columns:
        if column == 'date' or column == "technical_potential_up_reversal_bullish" \
                or column == "technical_potential_down_reversal_bearish" or column == "technical_potential_up_trend":
            continue
        if pd.api.types.is_numeric_dtype(df[column]) and df[column].max() > 1:
            normalized_df[column] = (df[column] - df[column].min()) / (df[column].max() - df[column].min())

    return normalized_df


def visualize_database_one_chart(run_dash=True):
    df = pd.read_csv(DATABASE_PATH)

    # Convert boolean columns to integers
    bool_columns = ["technical_potential_up_reversal_bullish",
                    "technical_potential_down_reversal_bearish", "technical_potential_up_trend"]
    df[bool_columns] = df[bool_columns].astype(int)

    # Normalize only the columns with values bigger than 1
    normalized_df = normalize_columns(df)

    # Convert the 'date' column to a datetime object
    normalized_df['date'] = pd.to_datetime(normalized_df['date'])

    # Set the 'date' column as the index
    normalized_df.set_index('date', inplace=True)

    # Create an empty figure
    fig = go.Figure()

    # Chart 1
    fig.add_trace(go.Scatter(x=normalized_df.index, y=normalized_df["interest_rate"],
                             mode='lines', name='Interest Rate'))
    fig.add_trace(go.Scatter(x=normalized_df.index, y=normalized_df["cpi_m_to_m"],
                             mode='lines', name='cpi_m_to_m'))
    fig.add_trace(go.Scatter(x=normalized_df.index, y=normalized_df["ppi_m_to_m"],
                             mode='lines', name='ppi_m_to_m'))
    fig.add_trace(go.Scatter(x=normalized_df.index, y=normalized_df["macro_bullish"],
                             mode='lines', name='macro_bullish'))
    fig.add_trace(go.Scatter(x=normalized_df.index, y=normalized_df["macro_bearish"],
                             mode='lines', name='macro_bearish'))

    # Chart 2
    fig.add_trace(go.Scatter(x=normalized_df.index, y=normalized_df["bid_volume"],
                             mode='lines', name='Bid Volume'))
    fig.add_trace(go.Scatter(x=normalized_df.index, y=normalized_df["ask_volume"],
                             mode='lines', name='Ask Volume'))
    fig.add_trace(go.Scatter(x=normalized_df.index, y=normalized_df["order_book_bullish"],
                             mode='lines', name='Order Book Bullish'))
    fig.add_trace(go.Scatter(x=normalized_df.index, y=normalized_df["order_book_bearish"],
                             mode='lines', name='Order Book Bearish'))

    # Chart 3
    fig.add_trace(go.Scatter(x=normalized_df.index, y=normalized_df["predicted_price"],
                             mode='lines', name='Predicted Price'))
    fig.add_trace(go.Scatter(x=normalized_df.index, y=normalized_df["prediction_bullish"],
                             mode='lines', name='Prediction Bullish'))
    fig.add_trace(go.Scatter(x=normalized_df.index, y=normalized_df["prediction_bearish"],
                             mode='lines', name='Prediction Bearish'))

    # Chart 4
    fig.add_trace(go.Scatter(x=normalized_df.index, y=normalized_df["technical_bullish"],
                             mode='lines', name='Technical Bullish'))
    fig.add_trace(go.Scatter(x=normalized_df.index, y=normalized_df["technical_bearish"],
                             mode='lines', name='technical_bearish'))

    # Chart 5
    fig.add_trace(go.Scatter(x=normalized_df.index, y=normalized_df["richest_addresses_total_received"],
                             mode='lines', name='Richest Addresses Total Received'))
    fig.add_trace(go.Scatter(x=normalized_df.index, y=normalized_df["richest_addresses_total_sent"],
                             mode='lines', name='Richest Addresses Total Sent'))
    fig.add_trace(go.Scatter(x=normalized_df.index, y=normalized_df["richest_addresses_bullish"],
                             mode='lines', name='Richest Addresses Bullish'))
    fig.add_trace(go.Scatter(x=normalized_df.index, y=normalized_df["richest_addresses_bearish"],
                             mode='lines', name='Richest Addresses Bearish'))

    # Chart 6
    fig.add_trace(go.Scatter(x=normalized_df.index, y=normalized_df["hourly_google_search"],
                             mode='lines', name='Hourly Google Search'))
    fig.add_trace(go.Scatter(x=normalized_df.index, y=normalized_df["google_search_bullish"],
                             mode='lines', name='Google Search Bullish'))
    fig.add_trace(go.Scatter(x=normalized_df.index, y=normalized_df["google_search_bearish"],
                             mode='lines', name='Google Search Bearish'))

    # Chart 7

    fig.add_trace(go.Scatter(x=normalized_df.index, y=normalized_df["reddit_activity_24h"],
                             mode='lines', name='Reddit Activity 24h'))
    fig.add_trace(go.Scatter(x=normalized_df.index, y=normalized_df["reddit_bullish"],
                             mode='lines', name='Reddit Bullish'))
    fig.add_trace(go.Scatter(x=normalized_df.index, y=normalized_df["reddit_bearish"],
                             mode='lines', name='Reddit Bearish'))

    # Chart 8
    fig.add_trace(go.Scatter(x=normalized_df.index, y=normalized_df["youtube_bullish"],
                             mode='lines', name='YouTube Bullish'))
    fig.add_trace(go.Scatter(x=normalized_df.index, y=normalized_df["youtube_bearish"],
                             mode='lines', name='YouTube Bearish'))

    # Chart 9
    fig.add_trace(go.Scatter(x=normalized_df.index, y=normalized_df["news_bullish"],
                             mode='lines', name='News Bullish'))
    fig.add_trace(go.Scatter(x=normalized_df.index, y=normalized_df["news_bearish"],
                             mode='lines', name='News Bearish'))

    # Chart 10
    fig.add_trace(go.Scatter(x=normalized_df.index, y=df["weighted_score_up"],
                             mode='lines', name='weighted_score_up'))
    fig.add_trace(go.Scatter(x=normalized_df.index, y=df["weighted_score_down"],
                             mode='lines', name='weighted_score_down'))

    # Update the layout and show the plot
    fig.update_layout(title='',
                      xaxis_title='Date',
                      yaxis_title='Normalized Value')

    if run_dash:
        app = dash.Dash(__name__)

        app.layout = html.Div([
            dcc.Graph(id='example-chart', figure=fig, style={'width': '100%', 'height': '100vh'}),
        ])
        app.run_server(host='0.0.0.0', port=8050, debug=False)


def visualize_trade_results():
    df = pd.read_csv(TRADE_RESULT_PATH)

    # Create an empty figure
    fig = go.Figure()

    # Add a bar chart for PNL
    fig.add_trace(go.Bar(x=df['weighted_score_category'], y=(df["PNL"]/1000),
                         name='PNL(K)'))

    # Add a bar chart for number_of_long
    fig.add_trace(go.Bar(x=df['weighted_score_category'], y=df["long_trades"],
                         name='long trades Number'))

    # Add a bar chart for number_of_short
    fig.add_trace(go.Bar(x=df['weighted_score_category'], y=df["short_trades"],
                         name='short trades Number'))
    # Add a bar chart for number_of_trades
    fig.add_trace(go.Bar(x=df['weighted_score_category'], y=df["win_trades"],
                         name='win trades'))

    # Add a bar chart for number_of_trades
    fig.add_trace(go.Bar(x=df['weighted_score_category'], y=df["loss_trades"],
                         name='loss trades'))

    # Add a bar chart for number_of_trades
    fig.add_trace(go.Bar(x=df['weighted_score_category'], y=df["total_trades"],
                         name='Number of Trades'))

    # Update the layout and show the plot
    fig.update_layout(title='Trade Results',
                      xaxis_title='Model Name',
                      yaxis_title='Value',
                      barmode='group')

    app = dash.Dash(__name__)

    app.layout = html.Div([
        dcc.Graph(id='trade-results-chart', style={'width': '100%', 'height': '100vh'}),
        dcc.Interval(
            id='interval-component',
            interval=5 * 60 * 1000,  # in milliseconds (10 minutes)
            n_intervals=0
        ),
    ])

    @app.callback(Output('trade-results-chart', 'figure'),
                  [Input('interval-component', 'n_intervals')])
    def update_graph_live(n):
        # Read the updated data
        df_inner = pd.read_csv(TRADE_RESULT_PATH)

        # Create an empty figure
        fig_inner = go.Figure()

        # Add a bar chart for PNL
        fig_inner.add_trace(go.Bar(x=df_inner['weighted_score_category'], y=(df_inner["PNL"] / 1000),
                                   name='PNL(K)'))

        # Add a bar chart for number_of_long
        fig_inner.add_trace(go.Bar(x=df_inner['weighted_score_category'], y=df_inner["long_trades"],
                                   name='long trades Number'))

        # Add a bar chart for number_of_short
        fig_inner.add_trace(go.Bar(x=df_inner['weighted_score_category'], y=df_inner["short_trades"],
                                   name='short trades Number'))

        # Add a bar chart for number_of_trades
        fig_inner.add_trace(go.Bar(x=df_inner['weighted_score_category'], y=df_inner["win_trades"],
                                   name='win trades'))

        # Add a bar chart for number_of_trades
        fig_inner.add_trace(go.Bar(x=df_inner['weighted_score_category'], y=df_inner["loss_trades"],
                                   name='loss trades'))

        # Add a bar chart for number_of_trades
        fig_inner.add_trace(go.Bar(x=df_inner['weighted_score_category'], y=df_inner["total_trades"],
                                   name='Number of Trades'))

        # Update the layout and show the plot
        fig_inner.update_layout(title='Trade Results',
                                xaxis_title='Model Name',
                                yaxis_title='Value',
                                barmode='group')

        return fig_inner
    app.run_server(host='0.0.0.0', port=8052, debug=False)


if __name__ == "__main__":
    # visualize_database_ten_rows()
    # visualize_database_two_rows()
    visualize_database_one_chart()
