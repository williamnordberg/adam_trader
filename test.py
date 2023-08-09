def read_gauge_chart_data():
    database = read_database()

    data_dict = {
        'trading_state': read_latest_data('latest_trading_state', str),
        'order_book_bullish': database['order_book_bullish'][-1],
        'macro_bullish': database['macro_bullish'][-1],
        'prediction_bullish': database['prediction_bullish'][-1],
        'technical_bullish': database['technical_bullish'][-1],
        'richest_addresses_bullish': database['richest_addresses_bullish'][-1],
        'google_search_bullish': database['google_search_bullish'][-1],
        'reddit_bullish': database['reddit_bullish'][-1],
        'youtube_bullish': database['youtube_bullish'][-1],
        'news_bullish': database['news_bullish'][-1],
        'weighted_score_up': database['weighted_score_up'][-1],
    }

    if data_dict['trading_state'] in ['long', 'short']:
        data_dict.update({
            'order_book_bullish': read_latest_data('order_book_hit_profit', float),
            'weighted_score_up': read_latest_data('score_profit_position', float),
        })

    return data_dict