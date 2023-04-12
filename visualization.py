import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.font_manager as fm
from matplotlib import rc
import plotly.graph_objects as go
from plotly.subplots import make_subplots

custom_font_path = "RobotoSlab.ttf"
custom_font = fm.FontProperties(fname=custom_font_path)
rc('font', family=custom_font.get_name())

custom_font_path1 = "Pacifico-Regular.ttf"
custom_font1 = fm.FontProperties(fname=custom_font_path1)
rc('font', family=custom_font1.get_name())


def create_gauge_chart(title, bullish, bearish):
    return go.Indicator(
        mode="gauge+number",
        value=bullish * 100,
        title={"text": title},
        domain={"x": [0, 1], "y": [0, 1]},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": "darkblue"},
            "steps": [
                {"range": [0, 100], "color": "lightgray"}
            ],
            "threshold": {
                "line": {"color": "red", "width": 4},
                "thickness": 0.75,
                "value": 50}
        },
        number={"suffix": "%", "font": {"size": 14}},
    )


def visualize_charts(macro_bullish, macro_bearish, order_book_bullish, order_book_bearish, prediction_bullish,
                     prediction_bearish, technical_bullish, technical_bearish, richest_addresses_bullish,
                     richest_addresses_bearish, google_search_bullish, google_search_bearish, reddit_bullish,
                     reddit_bearish, youtube_bullish, youtube_bearish, news_bullish, news_bearish,
                     weighted_score_up, weighted_score_down):
    fig = make_subplots(rows=2, cols=5,
                        specs=[[{"type": "indicator"}] * 5] * 2,
                        subplot_titles=["Macro Sentiment", "Order Book", "Prediction", "Technical Analysis",
                                        "Richest Addresses", "Google Search Trend", "Reddit Sentiment",
                                        "YouTube Sentiment", "News Sentiment", "Weighted Score"])

    fig.add_trace(create_gauge_chart("Macro Sentiment", macro_bullish, macro_bearish), row=1, col=1)
    fig.add_trace(create_gauge_chart("Order Book", order_book_bullish, order_book_bearish), row=1, col=2)
    fig.add_trace(create_gauge_chart("Prediction", prediction_bullish, prediction_bearish), row=1, col=3)
    fig.add_trace(create_gauge_chart("Technical Analysis", technical_bullish, technical_bearish), row=1, col=4)
    fig.add_trace(create_gauge_chart("Richest Addresses", richest_addresses_bullish, richest_addresses_bearish), row=1, col=5)
    fig.add_trace(create_gauge_chart("Google Search Trend", google_search_bullish, google_search_bearish), row=2, col=1)
    fig.add_trace(create_gauge_chart("Reddit Sentiment", reddit_bullish, reddit_bearish), row=2, col=2)
    fig.add_trace(create_gauge_chart("YouTube Sentiment", youtube_bullish, youtube_bearish), row=2, col=3)
    fig.add_trace(create_gauge_chart("News Sentiment", news_bullish, news_bearish), row=2, col=4)
    fig.add_trace(create_gauge_chart("Weighted Score", weighted_score_up, weighted_score_down), row=2, col=5)

    fig.update_layout(
        title_text="Gauge Charts",
        font=dict(size=10)
    )

    fig.show()


if __name__ == "__main__":
    visualize_charts(0.4, 0.6,
                     0.6, 0.4,
                     1, 0,
                     0, 1,
                     0.4, 0.6,
                     0.7, 0.3,
                     0.2, 0.8,
                     0.4, 0.6,
                     0.1, 0.9,
                     1, 0.4)
