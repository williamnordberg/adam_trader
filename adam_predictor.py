import pandas as pd
from datetime import datetime, timedelta
import logging
from sklearn.tree import DecisionTreeRegressor

from database import save_value_to_database
from update_dataset_yahoo import update_yahoo_data
from update_dataset_macro import update_macro_economic
from update_dataset_internal_factors import update_internal_factors
from handy_modules import compare_predicted_price, get_bitcoin_price

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

DATASET_UPDATE_INTERVAL = timedelta(hours=8)
LATEST_INFO_FILE = 'latest_info_saved.csv'
MAIN_DATASET_FILE = 'main_dataset.csv'


def should_update_dataset() -> bool:
    """Check if the dataset should be updated based on the last update time."""
    latest_info_saved = pd.read_csv(LATEST_INFO_FILE)
    last_update_time_str = latest_info_saved['latest_dataset_update'][0]
    last_update_time = datetime.strptime(last_update_time_str, '%Y-%m-%d %H:%M:%S')

    return datetime.now() - last_update_time > DATASET_UPDATE_INTERVAL


def update_dataset():
    """Update the dataset by calling the update functions for different sources."""
    update_internal_factors()
    update_yahoo_data()
    update_macro_economic()

    now = datetime.now()
    now_str = now.strftime('%Y-%m-%d %H:%M:%S')
    latest_info_saved = pd.read_csv(LATEST_INFO_FILE)
    latest_info_saved['latest_dataset_update'] = now_str
    latest_info_saved.to_csv(LATEST_INFO_FILE, index=False)
    logging.info(f'dataset has been updated {now}')


def load_dataset() -> pd.DataFrame:
    """Load the main dataset, set index, and fill missing values."""
    main_dataset = pd.read_csv(MAIN_DATASET_FILE)
    main_dataset = main_dataset.set_index(main_dataset['Date'])
    main_dataset.fillna(method='ffill', limit=1, inplace=True)

    return main_dataset


def train_and_predict(dataset: pd.DataFrame) -> int:
    """Train a DecisionTreeRegressor model and make predictions."""
    X_train = dataset.iloc[:-1][['DiffLast', 'DiffMean', 'CapAct1yrUSD', 'HashRate', 'Open', 'Rate']]
    y_train = dataset.iloc[:-1][['Close']]

    X_test = dataset.tail(1)[['DiffLast', 'DiffMean', 'CapAct1yrUSD', 'HashRate', 'Open', 'Rate']]
    X_test['Open'] = get_bitcoin_price()

    decision_model = DecisionTreeRegressor(random_state=0)
    decision_model.fit(X_train, y_train)
    predictions_tree = int(decision_model.predict(X_test).reshape(-1, 1))

    # Save to database
    print(type(predictions_tree))
    save_value_to_database('predicted_price', predictions_tree)

    return predictions_tree


def decision_tree_predictor() -> tuple:
    """Main function to check if dataset update is needed, load dataset, train model, and make predictions."""
    if should_update_dataset():
        update_dataset()

    dataset = load_dataset()
    prediction = train_and_predict(dataset)

    prediction_bullish, prediction_bearish = compare_predicted_price(prediction, get_bitcoin_price())
    return prediction_bullish, prediction_bearish


if __name__ == "__main__":
    prediction_bullish_outer, prediction_bearish_outer = decision_tree_predictor()
    logging.info(f"predicted bullish: {prediction_bullish_outer}")
    logging.info(f"predicted bearish: {prediction_bearish_outer}")
