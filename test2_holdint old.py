import plotly.graph_objects as go
from plotly.subplots import make_subplots


def create_gauge_chart(bullish, bearish, show_number=True):
    if bullish == 0 and bearish == 0:
        value = 50
        gauge_steps = [
            {"range": [0, 100], "color": "lightgray"},
        ]
        title = ""
        bar_thickness = 0
    else:
        value = (bullish / (bullish + bearish)) * 100
        gauge_steps = [
            {"range": [0, 100], "color": "lightcoral"}
        ]
        title = "Bull" if bullish > bearish else "Bear"
        bar_thickness = 1

    return go.Indicator(
        mode="gauge+number+delta" if show_number and title == "" else "gauge",
        value=value,
        title={"text": title, "font": {"size": 13, "color": "green" if title == "Bull" else "Red"}},
        domain={"x": [0, 1], "y": [0, 1]},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": "green", "thickness": bar_thickness},
            "steps": gauge_steps,
        },
        number={"suffix": "%" if show_number and title == "" else "", "font": {"size": 20}},
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

    fig.add_trace(create_gauge_chart(macro_bullish, macro_bearish, show_number=False), row=1, col=1)
    fig.add_trace(create_gauge_chart(order_book_bullish, order_book_bearish, show_number=False), row=1, col=2)
    fig.add_trace(create_gauge_chart(prediction_bullish, prediction_bearish, show_number=False), row=1, col=3)
    fig.add_trace(create_gauge_chart(technical_bullish, technical_bearish, show_number=False), row=1, col=4)
    fig.add_trace(create_gauge_chart(richest_addresses_bullish, richest_addresses_bearish,
                                     show_number=False), row=1, col=5)
    fig.add_trace(create_gauge_chart(google_search_bullish, google_search_bearish, show_number=False), row=2, col=1)
    fig.add_trace(create_gauge_chart(reddit_bullish, reddit_bearish, show_number=False), row=2, col=2)
    fig.add_trace(create_gauge_chart(youtube_bullish, youtube_bearish, show_number=False), row=2, col=3)
    fig.add_trace(create_gauge_chart(news_bullish, news_bearish, show_number=False), row=2, col=4)
    fig.add_trace(create_gauge_chart(weighted_score_up, weighted_score_down, show_number=True), row=2, col=5)

    fig.update_layout(
        font=dict(size=10)
    )

    fig.show()


if __name__ == "__main__":
    visualize_charts(0.4, 0.6,
                     0.6, 0.4,
                     0, 0,
                     0, 0,
                     0.4, 0.6,
                     0.7, 0.3,
                     0.2, 0.8,
                     0.4, 0.6,
                     0.1, 0.9,
                     0.6, 0.4)
