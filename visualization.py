import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.font_manager as fm
from matplotlib import rc


custom_font_path = "Pacifico-Regular.ttf"
custom_font = fm.FontProperties(fname=custom_font_path)
rc('font', family=custom_font.get_name())

custom_font_path1 = "RobotoSlab.ttf"
custom_font1 = fm.FontProperties(fname=custom_font_path1)
rc('font', family=custom_font1.get_name())


def draw_gauge_chart(title, bullish, bearish, ax):
    labels = ['Bear', 'Bull']
    values = [bearish, bullish]
    colors = ['red', 'green']

    ax.barh(labels, values, color=colors)
    ax.set_xlim(0, 1)
    ax.get_xaxis().set_ticks([])  # Remove x-axis tick labels
    ax.set_title(title, fontsize=12, fontweight='bold', fontproperties=custom_font1)

    for index, value in enumerate(values):
        ax.text(value, index, f"{   round(value * 100)}%", fontsize=10, fontweight='bold', verticalalignment='center',
                fontproperties=custom_font)

    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.get_yaxis().set_ticks([])  # Remove y-axis tick labels


def visualize_charts(macro_bullish, macro_bearish, order_book_bullish, order_book_bearish, prediction_bullish,
                     prediction_bearish, technical_bullish, technical_bearish, richest_addresses_bullish,
                     richest_addresses_bearish, google_search_bullish, google_search_bearish, reddit_bullish,
                     reddit_bearish, youtube_bullish, youtube_bearish, news_bullish, news_bearish,
                     weighted_score_up, weighted_score_down):

    fig, axs = plt.subplots(2, 5, figsize=(15, 6))

    # Create custom legend
    red_patch = mpatches.Patch(color='red', label='Bearish')
    green_patch = mpatches.Patch(color='green', label='Bullish')
    plt.legend(handles=[red_patch, green_patch], loc='upper left', bbox_to_anchor=(0, 1.2), ncol=2)

    draw_gauge_chart("Macro Sentiment", macro_bullish, macro_bearish, axs[0, 0])
    draw_gauge_chart("Order Book", order_book_bullish, order_book_bearish, axs[0, 1])
    draw_gauge_chart("Prediction", prediction_bullish, prediction_bearish, axs[0, 2])
    draw_gauge_chart("Technical Analysis", technical_bullish, technical_bearish, axs[0, 3])
    draw_gauge_chart("Richest Addresses", richest_addresses_bullish, richest_addresses_bearish, axs[0, 4])
    draw_gauge_chart("Google Search Trend", google_search_bullish, google_search_bearish, axs[1, 0])
    draw_gauge_chart("Reddit Sentiment", reddit_bullish, reddit_bearish, axs[1, 1])
    draw_gauge_chart("YouTube Sentiment", youtube_bullish, youtube_bearish, axs[1, 2])
    draw_gauge_chart("News Sentiment", news_bullish, news_bearish, axs[1, 3])
    draw_gauge_chart("Weighted Score", weighted_score_up, weighted_score_down, axs[1, 4])

    plt.tight_layout()
    plt.savefig("chart.png", dpi=150)  # Save the chart as a PNG image on the server
    plt.show()


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
