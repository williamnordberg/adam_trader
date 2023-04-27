from coinmetrics.api_client import CoinMetricsClient
import pandas as pd
import logging
from datetime import datetime, timedelta
import warnings
from handy_modules import retry_on_error_with_fallback

warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=RuntimeWarning)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
DATASET_PATH = 'data/main_dataset.csv'


class UpdateInternalFactorsError(Exception):
    """Raised when there is an issue with updating internal factors."""
    pass


def get_date_string(date_obj):
    return date_obj.strftime("%Y-%m-%d")


@retry_on_error_with_fallback(max_retries=3, delay=5)
def update_internal_factors():
    # Read the main dataset from disk
    main_dataset = pd.read_csv(DATASET_PATH, dtype={146: str})

    # Get the latest date in the main dataset
    latest_date = main_dataset.loc[main_dataset['DiffLast'].last_valid_index(), 'Date']

    # Initialize CoinMetricsClient
    client = CoinMetricsClient()

    # Get the latest available data
    end_date = get_date_string(datetime.now() - timedelta(days=1))
    start_date = get_date_string(pd.to_datetime(latest_date) + timedelta(days=1))

    # Check if the start_date is later than the end_date
    if pd.to_datetime(start_date) > pd.to_datetime(end_date):
        logging.info("Dataset is already up to date.")
        return

    try:
        # Request the required metrics for Bitcoin
        metric_ids = "DiffLast,DiffMean,CapAct1yrUSD,HashRate"
        asset_id = "btc"
        response = client.get_asset_metrics(
            assets=asset_id,
            metrics=metric_ids,
            start_time=start_date,
            end_time=end_date,
            frequency="1d",
        )
    except Exception as e:
        logging.error(f"Error: {e}")
        raise Exception("Failed to update dataset internal factors.")

    # Extract the data from the response and convert it to a DataFrame
    new_data = response.to_dataframe()

    # Format the DataFrame
    new_data = new_data.rename(columns={'time': 'Date'})
    new_data['Date'] = pd.to_datetime(new_data['Date'], unit='s').dt.strftime('%Y-%m-%d')

    for column in new_data.columns:
        if new_data.at[new_data.index[-1], column] == 'btc':
            new_data = new_data.drop(columns=[column])
            break

    # Check if there is new data to append
    if len(new_data) > 0:
        # check if new data have the same date row as the main_dataset
        if main_dataset['Date'].iloc[-1] == new_data['Date'].iloc[0]:
            # drop the last row in main dataset
            main_dataset = main_dataset.drop(main_dataset.index[-1])

        # Append the new rows to the main dataset
        main_dataset = pd.concat([main_dataset, new_data])

        # Write the updated dataset to disk
        main_dataset.to_csv(DATASET_PATH, index=False)

        logging.info(f"{len(new_data)} new rows of internal factors added.")
    else:
        logging.info("Internal factors are already up to date.")


if __name__ == "__main__":
    update_internal_factors()
