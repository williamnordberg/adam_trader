import pandas as pd
import logging
from sklearn.tree import DecisionTreeRegressor
from sklearn.impute import SimpleImputer
from typing import Tuple

from c_predictor_dataset import update_internal_factors, update_macro_economic
from handy_modules import get_bitcoin_price, retry_on_error
from z_compares import compare_predicted_price
from read_write_csv import save_value_to_database, \
    should_update, save_update_time, retrieve_latest_factor_values_database, load_dataset


def update_dataset():
    update_internal_factors()
    update_macro_economic()
    logging.info('dataset has been updated')
    save_update_time('dataset')


@retry_on_error(max_retries=3, delay=5, allowed_exceptions=(
        ValueError,), fallback_values=0)
def train_and_predict(dataset: pd.DataFrame) -> int:
    """
       Train a DecisionTreeRegressor model on the given data.

       Args:
        dataset (pd.DataFrame): dataset.

       Returns:
        int: The predicted value.
       """
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

    save_update_time('predicted_price')
    dataset = load_dataset()
    dataset.fillna(method='ffill', limit=1, inplace=True)

    prediction = train_and_predict(dataset)
    prediction_bullish, prediction_bearish = compare_predicted_price(prediction, get_bitcoin_price())

    save_value_to_database('prediction_bullish', prediction_bullish)
    save_value_to_database('prediction_bearish', prediction_bearish)

    return prediction_bullish, prediction_bearish


def decision_tree_predictor() -> Tuple[float, float]:
    if should_update('predicted_price'):
        return decision_tree_predictor_wrapper()
    else:
        return retrieve_latest_factor_values_database('prediction')


if __name__ == "__main__":
    prediction_bullish_outer, prediction_bearish_outer = decision_tree_predictor_wrapper()
    logging.info(f"predicted bullish: {prediction_bullish_outer}")
    logging.info(f"predicted bearish: {prediction_bearish_outer}")
