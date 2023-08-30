from coinmetrics.api_client import CoinMetricsClient
import pandas as pd
import logging
from datetime import datetime, timedelta
from z_read_write_csv import load_dataset


def update_internal_factors():
    main_dataset = load_dataset()

    # Get the latest date in the main dataset
    latest_date = main_dataset['DiffLast'].last_valid_index()

    # Initialize CoinMetricsClient
    client = CoinMetricsClient()

    # Get the latest available data
    end_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    last_value_date = (latest_date + timedelta(days=1)).strftime("%Y-%m-%d")
    # Check if the start_date is later than the end_date
    if pd.to_datetime(last_value_date) > pd.to_datetime(end_date):
        logging.info("Dataset is already up to date.")
        return

    # Request the required metrics for Bitcoin
    metric_ids = "DiffLast,DiffMean,CapAct1yrUSD,HashRate,PriceUSD"
    asset_id = "btc"
    response = client.get_asset_metrics(
        assets=asset_id,
        metrics=metric_ids,
        start_time=last_value_date,
        end_time=end_date,
        frequency="1h",
    )

    new_data = response.to_dataframe()

    if len(new_data) > 0:
        new_data = new_data.rename(columns={'time': 'Date'})
        new_data = new_data.rename(columns={'PriceUSD': 'Close'})
        new_data['Date'] = pd.to_datetime(new_data['Date'], unit='s').dt.strftime('%Y-%m-%d')
        new_data['Open'] = new_data['Close'].shift(1)
        new_data.set_index('Date', inplace=True)

        # Convert the index to a datetime index and then to the desired date format
        new_data.index = pd.to_datetime(new_data.index).strftime('%Y-%m-%d')

        for column in new_data.columns:
            if new_data.at[new_data.index[-1], column] == 'btc':
                new_data = new_data.drop(columns=[column])
                break

        # Get last 'Close' value from main_dataset
        last_close = main_dataset['Close'].iloc[-1]

        # Set first 'Open' value in new_data
        new_data['Open'].iloc[0] = last_close

        # Remove rows where any of the required metrics have NaN values
        new_data.dropna(subset=["DiffLast", "DiffMean", "CapAct1yrUSD", "HashRate", "Close"], inplace=True)

        # Append the new rows to the main dataset
        main_dataset = pd.concat([main_dataset, new_data])

        # Fix the format of the index

        main_dataset.index = pd.to_datetime(main_dataset.index).date

        # Write the updated dataset to disk
        main_dataset.index.name = 'Date'

        print('main_dataset', main_dataset)
        # save_dataset(main_dataset)

        logging.info(f"{len(new_data)} new rows of internal factors added.")
    else:
        logging.info("Internal factors are already up to date.")


if __name__ == "__main__":
    update_internal_factors()

