from plotly.subplots import make_subplots
import plotly.graph_objects as go
from datetime import timedelta
from dash import dash_table

from m_visualization_side import last_and_next_update
from z_handy_modules import COLORS
from z_read_write_csv import read_database, read_trading_details,  read_trading_results
from m_visualization_side import read_gauge_chart_data


APP_UPDATE_TIME = 50
LONG_THRESHOLD = 0.68
SHORT_THRESHOLD = 0.30


def create_figure(trace_list, title_text, yaxis_title='Value'):

    df = read_database()
    latest_date = df.index.max()  # get the latest date in your data
    days_ago = latest_date - timedelta(days=1)

    fig = make_subplots(shared_xaxes=True, vertical_spacing=0.02)
    for trace in trace_list:
        fig.add_trace(trace)

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
            bgcolor=COLORS['background'],
            activecolor=COLORS['lightgray'],
            x=0.0,
            y=1.1,
        ),
        type="date"
    )
    fig.update_layout(
        xaxis_range=[days_ago, latest_date],
        title={
            'text': title_text,
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {
                'color': COLORS['white'],
                'size': 24
            }
        },
        yaxis_title=yaxis_title,
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


def visualize_trade_details():
    df = read_trading_details()

    # Select only the required columns
    df = df[["weighted_score", "position_opening_time", "position_closing_time", "opening_price",
             "close_price", "position_type", "PNL"]]

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


def visualized_combined():
    df = read_database()

    trace_list = [
        go.Scatter(x=df.index, y=df["weighted_score_up"],
                   name='Combined score bullish', line=dict(color=COLORS['green_chart'])),
        go.Scatter(x=df.index, y=df["weighted_score_down"],
                   name='Combined score bearish', line=dict(color=COLORS['red_chart'])),
    ]

    fig = create_figure(trace_list, "Combined score")
    return fig


def visualized_news():
    df = read_database()

    trace_list = [
        go.Scatter(x=df.index, y=df["news_bullish"],
                   name='News bullish', visible='legendonly'),
        go.Scatter(x=df.index, y=df["news_bearish"],
                   name='News bearish', visible='legendonly'),
        go.Scatter(x=df.index, y=df["news_positive_polarity"],
                   name='Positive Polarity'),
        go.Scatter(x=df.index, y=df["news_negative_polarity"],
                   name='Negative polarity'),
        go.Scatter(x=df.index, y=df["news_positive_count"],
                   name='Positive Count', visible='legendonly'),
        go.Scatter(x=df.index, y=df["news_negative_count"],
                   name='Negative count', visible='legendonly'),
    ]

    fig = create_figure(trace_list, "News")
    return fig


def visualized_youtube():
    df = read_database()

    trace_list = [
        go.Scatter(x=df.index, y=df["youtube_bullish"],
                   name='YouTube bullish', visible='legendonly'),
        go.Scatter(x=df.index, y=df["youtube_bearish"],
                   name='YouTube bearish', visible='legendonly'),
        go.Scatter(x=df.index, y=df["last_24_youtube"],
                   name='Number of Video in 24h')
    ]

    fig = create_figure(trace_list, "Youtube")
    return fig


def visualized_reddit():
    df = read_database()

    trace_list = [
        go.Scatter(x=df.index, y=df["reddit_bullish"],
                   name='Reddit bullish', visible='legendonly'),
        go.Scatter(x=df.index, y=df["reddit_bearish"],
                   name='Reddit bearish', visible='legendonly'),
        go.Scatter(x=df.index, y=df["reddit_count_bitcoin_posts_24h"],
                   name='Count bitcoin posts 24h', visible='legendonly'),
        go.Scatter(x=df.index, y=df["reddit_activity_24h"],
                   name='Reddit activity')
    ]

    fig = create_figure(trace_list, "Reddit")
    return fig


def visualized_google():
    df = read_database()

    trace_list = [
        go.Scatter(x=df.index, y=df["hourly_google_search"], name='Hourly Google Search'),
        go.Scatter(x=df.index, y=df["google_search_bullish"], name='Google Bullish', visible='legendonly'),
        go.Scatter(x=df.index, y=df["google_search_bearish"], name='Google Bearish', visible='legendonly')
    ]

    fig = create_figure(trace_list, "Google search")
    return fig


def visualized_richest():
    df = read_database()

    trace_list = [
        go.Scatter(x=df.index, y=df["richest_addresses_bullish"], name='Richest bullish', visible='legendonly'),
        go.Scatter(x=df.index, y=df["richest_addresses_bearish"], name='Richest bearish', visible='legendonly'),
        go.Scatter(x=df.index, y=df["richest_addresses_total_received"], name='Sent in last 24H'),
        go.Scatter(x=df.index, y=df["richest_addresses_total_sent"], name='Received in last 24H')
    ]

    fig = create_figure(trace_list, "Richest Addresses", 'Value')
    return fig


def visualize_macro():
    df = read_database()

    trace_list = [
        go.Scatter(x=df.index, y=df['fed_rate_m_to_m'], name='Interest Rate M to M'),
        go.Scatter(x=df.index, y=df["cpi_m_to_m"], name='CPI M to M'),
        go.Scatter(x=df.index, y=df["ppi_m_to_m"], name='PPI M to M'),
        go.Scatter(x=df.index, y=df["macro_bullish"], name='Macro Bullish', visible='legendonly'),
        go.Scatter(x=df.index, y=df["macro_bearish"], name='Macro Bearish', visible='legendonly')
    ]

    fig = create_figure(trace_list, "Macro Economic", 'Value')
    return fig


def visualize_prediction():
    df = read_database()
    trace_list = [
        go.Scatter(x=df.index, y=df["predicted_price"], name='Predicted price'),
        go.Scatter(x=df.index, y=df["bitcoin_price"].shift(-12), name='Actual price'),
        go.Scatter(x=df.index, y=df["prediction_bullish"], name='Prediction bullish', visible='legendonly'),
        go.Scatter(x=df.index, y=df["prediction_bearish"], name='Prediction bearish', visible='legendonly')
    ]

    fig = create_figure(trace_list, "Prediction", 'Value')
    return fig


def visualize_trade_results():
    df = read_trading_results()

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


def create_single_gauge_chart(bullish, bearish, factor):
    last_update_time_str, next_update_str = last_and_next_update(factor)

    if bullish == 0 and bearish == 0:
        value = 0
        gauge_steps = [
            {"range": [0, 1], "color": COLORS['lightgray']},
        ]
        bar_thickness = 0
        mode_str = "gauge"
        number = {}
        gauge_dict = {
            "axis": {"range": [0, 1], "showticklabels": False},
            "bar": {"color": COLORS['green_chart'], "thickness": bar_thickness},
            "steps": gauge_steps,
            "bgcolor": COLORS['black'],
        }

    else:
        value = round(((bullish / (bullish + bearish)) * 1), 2)
        gauge_steps = [
            {"range": [0, 1], "color": COLORS['red_chart']}
        ]
        bar_thickness = 1
        mode_str = "gauge+number"
        gauge_dict = {
            "axis": {"range": [0, 1], "showticklabels": False,
                     "tickfont": {"size": 10,  "color": COLORS['white']},
                     },
            "bar": {"color": COLORS['green_chart'], "thickness": bar_thickness},
            "steps": gauge_steps,
            "bgcolor": COLORS['black'],
        }
        if factor == 'weighted_score':
            gauge_dict["axis"]["tickvals"] = [SHORT_THRESHOLD, LONG_THRESHOLD]  # Add ticks
            gauge_dict["axis"]["ticktext"] = [f"short {SHORT_THRESHOLD}", f"long {LONG_THRESHOLD}"]  # Add tick labels
            gauge_dict["axis"]["showticklabels"] = True

            if value >= LONG_THRESHOLD:
                number = {"font": {"size": 26, "color": COLORS['green_chart']}}
            elif value <= SHORT_THRESHOLD:
                number = {"font": {"size": 26, "color": COLORS['red_chart']}}
            else:
                number = {"font": {"size": 26, "color": COLORS['white']}}
        else:
            number = {"font": {"size": 12, "color": COLORS['white']}}
    return go.Indicator(
        mode=mode_str,
        value=value,
        title={
            "text": f"L: {last_update_time_str}   N: {next_update_str}",
            "font": {"size": 12, "color": COLORS['lightgray']}
        },
        domain={"x": [0, 1], "y": [0, 1]},
        gauge=gauge_dict,
        number=number,
    )


# noinspection PyTypeChecker
def create_gauge_charts():
    data_dict = read_gauge_chart_data()
    fig = make_subplots(rows=2, cols=5,
                        specs=[[{"type": "indicator"}] * 5] * 2,
                        subplot_titles=["Macro Sentiment", "Order Book", "Prediction", "Technical Analysis",
                                        "Richest Addresses", "Google Search Trend", "Reddit Sentiment",
                                        "YouTube Sentiment", "News Sentiment", "Combined Score"])

    fig.add_trace(create_single_gauge_chart(
        data_dict['macro_bullish'], data_dict['macro_bearish'], 'macro'), row=1, col=1)
    fig.add_trace(create_single_gauge_chart(
        data_dict['order_book_bullish'], data_dict['order_book_bearish'], 'order_book'), row=1, col=2)
    fig.add_trace(create_single_gauge_chart(
        data_dict['prediction_bullish'], data_dict['prediction_bearish'],
        'predicted_price'), row=1, col=3)
    fig.add_trace(create_single_gauge_chart(
        data_dict['technical_bullish'], data_dict['technical_bearish'],
        'technical_analysis'), row=1, col=4)
    fig.add_trace(create_single_gauge_chart(data_dict['richest_addresses_bullish'],
                                            data_dict['richest_addresses_bearish'],
                                            'richest_addresses'), row=1, col=5)
    fig.add_trace(create_single_gauge_chart(
        data_dict['google_search_bullish'], data_dict['google_search_bearish'],
        'google_search'), row=2, col=1)
    fig.add_trace(create_single_gauge_chart(
        data_dict['reddit_bullish'], data_dict['reddit_bearish'], 'reddit'), row=2, col=2)
    fig.add_trace(create_single_gauge_chart(
        data_dict['youtube_bullish'], data_dict['youtube_bearish'], 'youtube'), row=2, col=3)
    fig.add_trace(create_single_gauge_chart(
        data_dict['news_bullish'], data_dict['news_bearish'], 'sentiment_of_news'), row=2, col=4)
    fig.add_trace(create_single_gauge_chart(
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
