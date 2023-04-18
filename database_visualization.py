import pandas as pd
import matplotlib.pyplot as plt


def visualize_database():
    df = pd.read_csv('database.csv')

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

    # Create a 5x2 grid of subplots
    fig, axes = plt.subplots(5, 2, figsize=(15, 25))
    axes = axes.flatten()

    # Chart 1
    normalized_df[["interest_rate", "cpi_m_to_m", "ppi_m_to_m", "macro_bullish", "macro_bearish"]].plot(ax=axes[0])

    # Chart 2
    normalized_df[["bid_volume", "ask_volume", "order_book_bullish", "order_book_bearish"]].plot(ax=axes[1])

    # Chart 3
    normalized_df[["predicted_price", "prediction_bullish", "prediction_bearish"]].plot(ax=axes[2])

    # Chart 4
    normalized_df[["technical_potential_up_reversal_bullish", "technical_potential_down_reversal_bearish", "technical_potential_up_trend", "technical_bullish", "technical_bearish"]].plot(ax=axes[3])

    # Chart 5
    normalized_df[["richest_addresses_total_received", "richest_addresses_total_sent", "richest_addresses_bullish", "richest_addresses_bearish"]].plot(ax=axes[4])

    # Chart 6
    normalized_df[["hourly_google_search", "google_search_bullish", "google_search_bearish"]].plot(ax=axes[5])

    # Chart 7
    normalized_df[["reddit_count_bitcoin_posts_24h", "reddit_activity_24h", "reddit_bullish", "reddit_bearish"]].plot(ax=axes[6])

    # Chart 8
    normalized_df[["last_24_youtube", "youtube_bullish", "youtube_bearish"]].plot(ax=axes[7])

    # Chart 9
    normalized_df[["news_positive_polarity", "news_negative_polarity", "news_positive_count", "news_negative_count", "news_bullish", "news_bearish"]].plot(ax=axes[8])

    # Chart 10
    normalized_df[["weighted_score_up", "weighted_score_down"]].plot(ax=axes[9])

    # Adjust the layout and show the plot
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    visualize_database()