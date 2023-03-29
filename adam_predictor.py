from sklearn.tree import DecisionTreeRegressor
import pandas as pd
from datetime import datetime, timedelta
from old_update_dataset_internal_factors import update_internal_factors
from update_dataset_yahoo import update_yahoo_data
from update_dataset_macro import update_macro_economic
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


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
    decision_model = DecisionTreeRegressor(random_state=0)
    decision_model.fit(X_train, y_train)
    predictions_tree = decision_model.predict(X_test).reshape(-1, 1)
    return predictions_tree


if __name__ == "__main__":
    predicted_price = decision_tree_predictor()
    logging.info(f"The predicted price is: {predicted_price}")
