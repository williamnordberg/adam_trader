from plotly.subplots import make_subplots
import plotly.graph_objects as go
from datetime import timedelta
from dash import dash_table
from sklearn.preprocessing import MinMaxScaler
from dash import dcc, html

from m_visualization_side import last_and_next_update, create_progress_bar, generate_tooltips
from z_handy_modules import COLORS
from z_read_write_csv import read_database, read_trading_details
from m_visualization_side import read_gauge_chart_data
from a_config import LONG_THRESHOLD, SHORT_THRESHOLD

# Create a MinMaxScaler object
scaler = MinMaxScaler((0, 1))

APP_UPDATE_TIME = 50

LONG_THRESHOLD_GAUGE = 0.68
SHORT_THRESHOLD_GAUGE = 0.30


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

    layout_kwargs = {
        'xaxis_range': [days_ago, latest_date],
        'title': {
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
        'yaxis_title': yaxis_title,
        'plot_bgcolor': COLORS['black_chart'],
        'paper_bgcolor': COLORS['background'],
        'font': dict(
            color=COLORS['white'],
            size=12
        ),
        'legend': dict(orientation="h",
                       yanchor="bottom",
                       y=1.02,
                       xanchor="right",
                       x=1),
        'hovermode': "x"
    }

    if title_text == "Combined score":
        layout_kwargs['shapes'] = [
            dict(
                type="line",
                xref="paper", x0=0, x1=1,
                yref="y", y0=LONG_THRESHOLD, y1=LONG_THRESHOLD,
                line=dict(color=COLORS['lightgray'], width=1)
            ),
            dict(
                type="line",
                xref="paper", x0=0, x1=1,
                yref="y", y0=SHORT_THRESHOLD, y1=SHORT_THRESHOLD,
                line=dict(color=COLORS['lightgray'], width=1)
            )
        ]
        layout_kwargs['annotations'] = [
            dict(
                xref='paper', x=0.05,
                yref='y', y=LONG_THRESHOLD,
                text='Long',
                showarrow=False,
                font=dict(
                    size=10,
                    color=COLORS['white']
                )
            ),
            dict(
                xref='paper', x=0.08,
                yref='y', y=SHORT_THRESHOLD,
                text='Short',
                showarrow=False,
                font=dict(
                    size=10,
                    color=COLORS['white']
                )
            )
        ]

    fig.update_layout(**layout_kwargs)

    return fig


def visualization_log(filename, lines=1):
    with open(filename, 'r', encoding='utf-8') as f:
        last_lines = list(f)[-lines:]
        reversed_lines = last_lines[::-1]
        return ''.join(reversed_lines)


def visualized_combined():
    df = read_database()

    trace_list = [
        go.Scatter(x=df.index, y=df["weighted_score_up"],
                   name='Combined score', line=dict(color=COLORS['green_chart'])),
        go.Scatter(
            x=df.index,
            y=(df["bitcoin_price"] / 100000),
            name='Bitcoin price',
            visible='legendonly',
            text=(round(df["bitcoin_price"], 0).astype(str)),  # specify the hover text
            hoverinfo='text'  # use the text for hover
        )
    ]

    fig = create_figure(trace_list, "Combined score")
    return fig


def visualized_news():
    df = read_database()

    trace_list = [
        go.Scatter(x=df.index, y=df["news_bullish"],
                   name='News', visible='legendonly'),
        go.Scatter(x=df.index, y=df["news_positive_polarity"],
                   name='Positive Polarity'),
        go.Scatter(x=df.index, y=df["news_negative_polarity"],
                   name='Negative polarity'),
        go.Scatter(x=df.index, y=df["news_positive_count"],
                   name='Positive Count', visible='legendonly'),
        go.Scatter(x=df.index, y=df["news_negative_count"],
                   name='Negative count', visible='legendonly'),
        go.Scatter(
            x=df.index,
            y=(df["bitcoin_price"] / 100000),
            name='Bitcoin price',
            visible='legendonly',
            text=(round(df["bitcoin_price"], 0).astype(str)),  # specify the hover text
            hoverinfo='text'  # use the text for hover
        )
    ]

    fig = create_figure(trace_list, "News")
    return fig


def visualized_youtube():
    df = read_database()

    trace_list = [
        go.Scatter(x=df.index, y=df["youtube_bullish"],
                   name='YouTube', visible='legendonly'),
        go.Scatter(x=df.index, y=df["youtube_positive_polarity"],
                   name='Positive polarity', visible='legendonly'),
        go.Scatter(x=df.index, y=df["youtube_negative_polarity"],
                   name='Negative polarity', visible='legendonly'),
        go.Scatter(x=df.index, y=df["youtube_positive_count"],
                   name='Positive count', visible='legendonly'),
        go.Scatter(x=df.index, y=df["youtube_negative_count"],
                   name='Negative count', visible='legendonly'),

        go.Scatter(x=df.index, y=df["last_24_youtube"],
                   name='Number of Video in 24h'),
        go.Scatter(x=df.index, y=(df["bitcoin_price"]/100), name='Bitcoin price'),

    ]

    fig = create_figure(trace_list, "Youtube")
    return fig


def visualized_reddit():
    df = read_database()

    trace_list = [
        go.Scatter(x=df.index, y=df["reddit_bullish"],
                   name='Reddit', visible='legendonly'),
        go.Scatter(x=df.index, y=df["reddit_activity_24h"],
                   name='Reddit activity'),
        go.Scatter(x=df.index, y=df["reddit_positive_polarity"],
                   name='Positive polarity', visible='legendonly'),
        go.Scatter(x=df.index, y=df["reddit_negative_polarity"],
                   name='Negative polarity', visible='legendonly'),
        go.Scatter(x=df.index, y=df["reddit_positive_count"],
                   name='Positive count', visible='legendonly'),
        go.Scatter(x=df.index, y=df["reddit_negative_count"],
                   name='Negative count', visible='legendonly'),
        go.Scatter(x=df.index, y=df["bitcoin_price"], name='Bitcoin price',  visible='legendonly'),

    ]

    fig = create_figure(trace_list, "Reddit")
    return fig


def visualized_google():
    df = read_database()

    trace_list = [
        go.Scatter(x=df.index, y=df["hourly_google_search"], name='Hourly Google Search'),
        go.Scatter(x=df.index, y=df["google_search_bullish"], name='Google', visible='legendonly'),
        go.Scatter(x=df.index, y=(df["bitcoin_price"]/1000), name='Bitcoin price'),

    ]

    fig = create_figure(trace_list, "Google search")
    return fig


def visualized_richest():
    df = read_database()

    trace_list = [
        go.Scatter(x=df.index, y=df["richest_addresses_bullish"], name='Richest', visible='legendonly'),
        go.Scatter(x=df.index, y=df["richest_addresses_total_received"], name='Received in last 24H'),
        go.Scatter(x=df.index, y=df["richest_addresses_total_sent"], name='Sent in last 24H'),
        go.Scatter(x=df.index, y=df["bitcoin_price"], name='Bitcoin price', visible='legendonly'),

    ]

    fig = create_figure(trace_list, "Richest Addresses", 'Value')
    return fig


def visualize_macro():
    df = read_database()

    trace_list = [
        go.Scatter(x=df.index, y=df['fed_rate_m_to_m'], name='Interest Rate M to M', hovertemplate='%{y}'),
        go.Scatter(x=df.index, y=df["cpi_m_to_m"], name='CPI M to M', hovertemplate='%{y}'),
        go.Scatter(x=df.index, y=df["ppi_m_to_m"], name='PPI M to M', hovertemplate='%{y}'),
        go.Scatter(x=df.index, y=df["macro_bullish"], name='Macro', visible='legendonly', hovertemplate='%{y}'),
        go.Scatter(
            x=df.index,
            y=(df["bitcoin_price"] / 100000),
            name='Bitcoin price',
            visible='legendonly',
            text=(round(df["bitcoin_price"], 0).astype(str)),  # specify the hover text
            hoverinfo='text'  # use the text for hover
        )
    ]

    fig = create_figure(trace_list, "Macro Economic", 'Value')
    return fig


def visualize_prediction():
    df = read_database()
    trace_list = [
        go.Scatter(x=df.index, y=df["predicted_price"], name='Predicted price', visible='legendonly'),
        go.Scatter(x=df.index, y=df["bitcoin_price"].shift(-1), name='Actual price', visible='legendonly'),
        go.Scatter(x=df.index, y=df["prediction_bullish"], name='Prediction'),
    ]

    fig = create_figure(trace_list, "Prediction", 'Value')
    return fig


def visualize_trade_results():
    df = read_database()

    trace_list = [
        go.Scatter(x=df.index, y=df["weighted_score_up"], name='score'),
        go.Scatter(x=df.index, y=df["macro_bullish"], name='macro'),
        go.Scatter(x=df.index, y=df["order_book_bullish"], name='order'),
        go.Scatter(x=df.index, y=df["prediction_bullish"], name='prediction', visible='legendonly'),
        go.Scatter(x=df.index, y=df["technical_bullish"], name='technical'),
        go.Scatter(x=df.index, y=df["richest_addresses_bullish"], name='richest'),
        go.Scatter(x=df.index, y=df["google_search_bullish"], name='google'),
        go.Scatter(x=df.index, y=df["reddit_bullish"], name='reddit'),
        go.Scatter(x=df.index, y=df["youtube_bullish"], name='youtube'),
        go.Scatter(x=df.index, y=df["news_bullish"], name='news'),
        go.Scatter(x=df.index, y=(df["bitcoin_price"]/100000), name='Bitcoin price'),

    ]

    fig = create_figure(trace_list, "All factors")
    return fig


def create_single_gauge_chart(bullish, factor):
    last_update_time_str, next_update_str = last_and_next_update(factor)

    if bullish == 0.5:
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
        value = bullish
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
            gauge_dict["axis"]["tickvals"] = [SHORT_THRESHOLD_GAUGE, LONG_THRESHOLD_GAUGE]  # Add ticks
            gauge_dict["axis"]["ticktext"] = [f"short {SHORT_THRESHOLD_GAUGE}", f"long {LONG_THRESHOLD_GAUGE}"]
            gauge_dict["axis"]["showticklabels"] = True

            if value >= LONG_THRESHOLD_GAUGE:
                number = {"font": {"size": 26, "color": COLORS['green_chart']}}
            elif value <= SHORT_THRESHOLD_GAUGE:
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
        data_dict['macro_bullish'], 'macro'), row=1, col=1)
    fig.add_trace(create_single_gauge_chart(
        data_dict['order_book_bullish'], 'order_book'), row=1, col=2)
    fig.add_trace(create_single_gauge_chart(
        data_dict['prediction_bullish'], 'predicted_price'), row=1, col=3)
    fig.add_trace(create_single_gauge_chart(
        data_dict['technical_bullish'], 'technical_analysis'), row=1, col=4)
    fig.add_trace(create_single_gauge_chart(data_dict['richest_addresses_bullish'], 'richest_addresses'), row=1, col=5)
    fig.add_trace(create_single_gauge_chart(
        data_dict['google_search_bullish'], 'google_search'), row=2, col=1)
    fig.add_trace(create_single_gauge_chart(
        data_dict['reddit_bullish'], 'reddit'), row=2, col=2)
    fig.add_trace(create_single_gauge_chart(
        data_dict['youtube_bullish'], 'youtube'), row=2, col=3)
    fig.add_trace(create_single_gauge_chart(
        data_dict['news_bullish'], 'sentiment_of_news'), row=2, col=4)
    fig.add_trace(create_single_gauge_chart(
        data_dict['weighted_score_up'], 'weighted_score'), row=2, col=5)

    fig.update_layout(plot_bgcolor=COLORS['background'], paper_bgcolor=COLORS['background'])

    for annotation in fig['layout']['annotations']:
        if annotation['text'] == "Combined Score":
            annotation['font'] = dict(color=COLORS['white'], size=26,
                                      )  # set color, size, and boldness of the title
        else:
            annotation['font'] = dict(color=COLORS['white'], size=15)

    return fig


def visualize_trade_details():
    df = read_trading_details()

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


def create_trade_details_div():
    return html.Div(
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


def create_first_graph():
    fig = create_gauge_charts()

    graph = dcc.Graph(id='live-update-graph', figure=fig,
                      style={'width': '89%', 'height': '100vh', 'display': 'inline-block', 'marginTop': '-18px'})
    return graph


def create_graphs():
    fig_dict = {
        'fig': create_gauge_charts(),
        'fig_trade_result': visualize_trade_results(),
        'fig_macro': visualize_macro(),
        'fig_prediction': visualize_prediction(),
        'fig_richest': visualized_richest(),
        'fig_google': visualized_google(),
        'fig_reddit': visualized_reddit(),
        'fig_youtube': visualized_youtube(),
        'fig_news': visualized_news(),
        'fig_combined': visualized_combined(),
    }
    graph_list = []
    graph_ids = ['live-update-graph', 'trade_results_chart', 'macro_chart', 'prediction_chart',
                 'richest_chart', 'google_chart', 'reddit_chart',
                 'youtube_chart', 'news_chart', 'combined_chart']
    fig_list = [fig_dict['fig'], fig_dict['fig_trade_result'], fig_dict['fig_macro'],
                fig_dict['fig_prediction'], fig_dict['fig_richest'], fig_dict['fig_google'],
                fig_dict['fig_reddit'], fig_dict['fig_youtube'], fig_dict['fig_news'],
                fig_dict['fig_combined']]

    for i in range(len(graph_ids)):
        graph_list.append(dcc.Graph(id=graph_ids[i], figure=fig_list[i],
                                    style={'width': '100%', 'height': '100vh'}))

    return graph_list


def create_progress_div():
    progress_bar = create_progress_bar()
    return html.Div(children=[progress_bar],
                    style={'display': 'inline-block', 'width': '100%', 'height': '05vh'})


def create_loading_component():
    return dcc.Loading(
        id="loading",
        type="cube",  # you can also use "default" or "circle"
        fullscreen=True,  # Change to False if you don't want it to be full screen
        children=html.Div(id='dummy-output_cube'),
        style={'backgroundColor': COLORS['background'],
               'position': 'fixed', 'top': 0, 'left': 0, 'width': '100%', 'height': '100%'}
    )


def create_log_output():
    return html.Div(children=[
        html.H3('Terminal output', style={'textAlign': 'center'}),
        dcc.Textarea(id='log-data', style={
            'width': '90%',
            'height': '40vh',
            'backgroundColor': COLORS['black_chart'],
            'color': COLORS['white'],
            'margin': 'auto'
        })
    ],
        style={
            'display': 'flex',
            'flex-direction': 'column',
            'justifyContent': 'center',
            'alignItems': 'center',
            'width': '100%'
        }
    )


def create_figure_div():
    graphs = create_graphs()
    figure_div = html.Div(
        children=graphs[1:] + generate_tooltips(),
        style={'width': '100%', 'height': '90vh', 'display': 'inline-block', 'verticalAlign': 'top'}
    )
    return figure_div
