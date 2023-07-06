import dash_bootstrap_components as dbc
import pandas.errors
from typing import Tuple
from datetime import datetime, timedelta
from dash import html
from dash import dcc


from z_read_write_csv import read_database, read_latest_data, update_intervals
from a_macro import calculate_upcoming_events
from z_handy_modules import get_bitcoin_price, retry_on_error

APP_UPDATE_TIME = 60
TIMER_PROGRESS_UPDATE_TIME = 10


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


def read_gauge_chart_data():
    database = read_database()

    data_dict = {
        'trading_state': read_latest_data('latest_trading_state', str),
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
        'weighted_score_up': database['weighted_score_up'][-1],
        'weighted_score_down': database['weighted_score_down'][-1],
    }

    if data_dict['trading_state'] in ['long', 'short']:
        data_dict.update({
            'order_book_bullish': read_latest_data('order_book_hit_profit', float),
            'order_book_bearish': read_latest_data('order_book_hit_loss', float)
        })
    else:
        data_dict.update({
            'order_book_bullish': database['order_book_bullish'][-1],
            'order_book_bearish': database['order_book_bearish'][-1]
        })

    return data_dict


def read_layout_data():
    database = read_database()
    fed_announcement, cpi_announcement, ppi_announcement = calculate_upcoming_events()
    read_latest_data('latest_trading_state', str)
    layout_data = {
        "trading_state": f'{read_latest_data("latest_trading_state", str)}',
        "fed_rate_m_to_m": f'Fed rate MtM: {read_latest_data("fed_rate_m_to_m", float)}',
        "cpi_m_to_m": f'{read_latest_data("cpi_m_to_m",float)}',
        "ppi_m_to_m": f'{read_latest_data("ppi_m_to_m", float)}',
        "bid_volume": int(database['bid_volume'][-1]),
        "ask_volume": int(database['ask_volume'][-1]),
        "predicted_price": database['predicted_price'][-1],
        "current_price": get_bitcoin_price(),
        "rsi": read_latest_data("latest_rsi", int),
        "over_200EMA": read_latest_data("over_200EMA", str),
        "MACD_uptrend": database['technical_potential_up_trend'][-1],
        "bb_MA_distance": read_latest_data("bb_band_MA_distance", float),
        "BTC_received": int(database['richest_addresses_total_received'][-1]),
        "BTC_send": int(database['richest_addresses_total_sent'][-1]),
        "positive_news_polarity_change": read_latest_data("positive_news_polarity_change", float),
        "negative_news_polarity_change": read_latest_data("negative_news_polarity_change", float),
        "fed_announcement": fed_announcement,
        "cpi_announcement": cpi_announcement,
        "ppi_announcement": ppi_announcement
    }

    return layout_data


@retry_on_error(max_retries=3, delay=5, allowed_exceptions=(
        pandas.errors.EmptyDataError, Exception), fallback_values=('0', '0'))
def last_and_next_update(factor: str) -> Tuple[str, str]:

    last_update_time_str = read_latest_data(f'latest_{factor}_update', str)
    last_update_time = datetime.strptime(last_update_time_str, '%Y-%m-%d %H:%M:%S')

    # Calculate the time difference between now and the last update time
    time_since_last_update = datetime.now() - last_update_time

    # If the time since last update is more than 1 hour, convert it to hours
    if time_since_last_update.total_seconds() > 3600:
        time_since_last_update_str = f'{int(time_since_last_update.total_seconds() // 3600)}h'
    else:  # else, convert it to minutes
        time_since_last_update_str = f'{int(time_since_last_update.total_seconds() // 60)}m'

    if update_intervals[factor] < time_since_last_update:
        next_update = timedelta(seconds=0)  # equivalent to zero
    else:
        next_update = update_intervals[factor] - time_since_last_update

    # Similar conversion for next update
    if next_update.total_seconds() > 3600:
        next_update_str = f'{int(next_update.total_seconds() // 3600)}h'
    else:
        next_update_str = f'{int(next_update.total_seconds() // 60)}m'

    return time_since_last_update_str, next_update_str


def create_scroll_up_button():
    top_button = dbc.Button(
     children=[html.I(className="fa fa-arrow-up", style={'margin': 'auto', 'color': 'black', 'font-size': '39px'})],
     id="top-button",
     className="mr-1",
     outline=True,
     color="secondary",
     style={'position': 'fixed', 'bottom': '1%', 'right': '1%',
            'z-index': '9999', 'height': '50px', 'width': '50px',
            'opacity': '0.4', 'border-radius': '50%',
            'padding': '6px', 'display': 'flex',
            'justify-content': 'center',
            'align-items': 'center',
            'background-color': 'gray'
            }
     )
    return top_button


def create_update_intervals():
    interval_component = dcc.Interval(
        id='interval-component',
        interval=APP_UPDATE_TIME * 1000,  # in milliseconds
        n_intervals=0
    )
    timer_interval_component = dcc.Interval(
        id='timer-interval-component',
        interval=TIMER_PROGRESS_UPDATE_TIME * 1000,  # in milliseconds
        n_intervals=0
    )

    return timer_interval_component, interval_component
