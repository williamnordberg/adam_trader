import requests
from sklearn.tree import DecisionTreeRegressor
import pandas as pd
from datetime import datetime, timedelta
from update_dataset_yahoo import update_yahoo_data
from update_dataset_macro import update_macro_economic
from update_dataset_internal_factors import update_internal_factors
import logging


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def compare(predicted_price, current_price):

    activity_percentage = (predicted_price - current_price) / current_price * 100
    if activity_percentage > 0:
        if activity_percentage >= 5:
            return 1, 0
        elif activity_percentage >= 4:
            return 0.9, 0.1
        elif activity_percentage >= 3:
            return 0.8, 0.2
        elif activity_percentage >= 2:
            return 0.7, 0.3
        elif activity_percentage >= 1:
            return 0.6, 0.4

    elif activity_percentage <= 0:
        if activity_percentage <= -5:
            return 0, 1
        elif activity_percentage <= -4:
            return 0.1, 0.9
        elif activity_percentage <= -3:
            return 0.2, 0.8
        elif activity_percentage <= -2:
            return 0.3, 0.7
        elif activity_percentage <= -1:
            return 0.4, 0.6

    return 0, 0


def get_bitcoin_price():
    """
    Retrieves the current Bitcoin price in USD from the CoinGecko API.

    Returns:
        float: The current Bitcoin price in USD or 0 if an error occurred.
    """
    try:
        url = 'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd'
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            current_price_local = data['bitcoin']['usd']
            return current_price_local
        else:
            logging.error("Error: Could not retrieve Bitcoin price data")
            return 0
    except requests.exceptions.RequestException as e:
        logging.error(f"Error: Could not connect to CoinGecko API:{e}")
        return 0


def decision_tree_predictor():
    # Read the last update time from disk
    latest_info_saved = pd.read_csv('latest_info_saved.csv')
    last_update_time_str = latest_info_saved['latest_dataset_update'][0]
    last_update_time = datetime.strptime(last_update_time_str, '%Y-%m-%d %H:%M:%S')

    if datetime.now() - last_update_time > timedelta(hours=8):
        update_internal_factors()
        update_yahoo_data()
        update_macro_economic()

        # Save the update time to disk
        now = datetime.now()
        now_str = now.strftime('%Y-%m-%d %H:%M:%S')
        latest_info_saved['latest_dataset_update'] = now_str

        # Save the latest info to disk
        latest_info_saved.to_csv('latest_info_saved.csv', index=False)
        logging.info(f'dataset been updated {now}')

    else:
        logging.info(f'dataset is already updated less than 8 hours ago at {last_update_time}')

    # load the main dataset and finn null value
    main_dataset = pd.read_csv('main_dataset.csv')
    main_dataset = main_dataset.set_index(main_dataset['Date'])

    # Backward fill missing values with the next non-null value
    main_dataset.fillna(method='ffill', limit=1, inplace=True)
    X_train = main_dataset.iloc[:-1][['DiffLast', 'DiffMean', 'CapAct1yrUSD', 'HashRate', 'Open', 'Rate']]
    y_train = main_dataset.iloc[:-1][['Close']]

    # use last row to predict price
    X_test = main_dataset.tail(1)[['DiffLast', 'DiffMean', 'CapAct1yrUSD', 'HashRate', 'Open', 'Rate']]
    X_test['Open'] = get_bitcoin_price()
    decision_model = DecisionTreeRegressor(random_state=0)
    decision_model.fit(X_train, y_train)
    predictions_tree = int(decision_model.predict(X_test).reshape(-1, 1))

    # compare price
    prediction_bullish, prediction_bearish = compare(predictions_tree, get_bitcoin_price())
    return prediction_bullish, prediction_bearish


if __name__ == "__main__":
    prediction_bullish_outer, prediction_bearish_outer = decision_tree_predictor()
    logging.info(f"predicted bullish: {prediction_bullish_outer}")
    logging.info(f"predicted bearish: {prediction_bearish_outer}")
