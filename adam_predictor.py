import pandas as pd
import logging
from sklearn.tree import DecisionTreeRegressor
from sklearn.impute import SimpleImputer
from typing import Tuple

from database import save_value_to_database, read_database
from update_dataset_yahoo import update_yahoo_data, UpdateYahooData
from update_dataset_macro import update_macro_economic
from update_dataset_internal_factors import update_internal_factors, UpdateInternalFactorsError
from handy_modules import compare_predicted_price, get_bitcoin_price, should_update, save_update_time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

MAIN_DATASET_FILE = 'main_dataset.csv'


def load_dataset() -> pd.DataFrame:
    """Load the main dataset, set index, and fill missing values."""
    main_dataset = pd.read_csv(MAIN_DATASET_FILE)
    main_dataset = main_dataset.set_index(main_dataset['Date'])
    main_dataset.fillna(method='ffill', limit=1, inplace=True)

    return main_dataset


def update_dataset():
    try:
        update_internal_factors()
        update_yahoo_data()
        update_macro_economic()
        logging.info('dataset has been updated')
        save_update_time('dataset')
    except UpdateInternalFactorsError as e:
        logging.error(f"Failed to update internal factors: {e}")


def train_and_predict(dataset: pd.DataFrame) -> int:
    """Train a DecisionTreeRegressor model and make predictions."""
    # SimpleImputer to fill missing values
    imputer = SimpleImputer(strategy='mean')
    dataset[['DiffLast', 'DiffMean', 'CapAct1yrUSD', 'HashRate', 'Open', 'Rate']] = imputer.fit_transform(
        dataset[['DiffLast', 'DiffMean', 'CapAct1yrUSD', 'HashRate', 'Open', 'Rate']])

    X_train = dataset.iloc[:-1][['DiffLast', 'DiffMean', 'CapAct1yrUSD', 'HashRate', 'Open', 'Rate']]
    y_train = dataset.iloc[:-1][['Close']]

    X_test = dataset.tail(1)[['DiffLast', 'DiffMean', 'CapAct1yrUSD', 'HashRate', 'Open', 'Rate']]
    X_test['Open'] = get_bitcoin_price()

    decision_model = DecisionTreeRegressor(random_state=0)
    decision_model.fit(X_train, y_train)
    predictions_tree = int(decision_model.predict(X_test).reshape(-1, 1))

    # Save to database
    save_value_to_database('predicted_price', predictions_tree)

    return predictions_tree


def decision_tree_predictor_wrapper() -> Tuple[float, float]:
    """Main function to check if dataset update is needed, load dataset, train model, and make predictions."""
    if should_update('dataset'):
        update_dataset()

    dataset = load_dataset()
    prediction = train_and_predict(dataset)

    prediction_bullish, prediction_bearish = compare_predicted_price(prediction, get_bitcoin_price())

    # Save to database
    save_value_to_database('prediction_bullish', prediction_bullish)
    save_value_to_database('prediction_bearish', prediction_bearish)

    # Save latest update time
    save_update_time('predicted_price')

    return prediction_bullish, prediction_bearish


def decision_tree_predictor() -> Tuple[float, float]:
    if should_update('predicted_price'):
        return decision_tree_predictor_wrapper()
    else:
        database = read_database()
        prediction_bullish = database['prediction_bullish'][-1]
        prediction_bearish = database['prediction_bearish'][-1]
        return prediction_bullish, prediction_bearish


if __name__ == "__main__":
    prediction_bullish_outer, prediction_bearish_outer = decision_tree_predictor()
    logging.info(f"predicted bullish: {prediction_bullish_outer}")
    logging.info(f"predicted bearish: {prediction_bearish_outer}")
