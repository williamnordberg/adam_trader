from z_read_write_csv import read_database
import bisect
from typing import Tuple
import plotly.graph_objects as go



RANGES_PREDICTION = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, float('inf'))]
VALUES_PREDICTION_GREATER = [0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
VALUES_PREDICTION_LESSER = [0.5, 0.4, 0.3, 0.2, 0.1, 0.0]


def compare(data, ranges, values):
    # Extract the right side of each range for comparison
    right_ranges = [r[1] for r in ranges]
    index = bisect.bisect_right(right_ranges, data)
    return values[index]


def compare_predicted_price(predicted_price: int, current_price: int) -> Tuple[float, float]:
    if predicted_price > current_price:
        price_difference_percentage = (predicted_price - current_price) / current_price * 100
        prediction_bullish = compare(
            price_difference_percentage, RANGES_PREDICTION, VALUES_PREDICTION_GREATER)
        return prediction_bullish, price_difference_percentage
    elif current_price > predicted_price:
        price_difference_percentage = (current_price - predicted_price) / predicted_price * 100
        prediction_bullish = compare(
            price_difference_percentage, RANGES_PREDICTION, VALUES_PREDICTION_LESSER)
        return prediction_bullish, price_difference_percentage
    else:
        return 0.5, 0.0


def evaluate_prediction():
    df = read_database()

    # Create a list to store the results of the comparison
    results = []
    price_diff_list = []

    for predicted_price, actual_price, index, predicted in (
            zip(df["predicted_price"], df["bitcoin_price"],
                df.index, df['prediction_bullish'])):
        result, price_difference_percentage = compare_predicted_price(predicted_price, actual_price)
        # if result != 0.5:
        #     print('result', result)
        #    print(index)
        #    print('predicted:', predicted)
        price_diff_list.append(price_difference_percentage)
        results.append(result)

    prev_price = None
    prev_diff = None
    for diff, price, date in zip(price_diff_list, df['bitcoin_price'], df.index):
        if prev_price is not None:
            percent_diff = ((price - prev_price) / prev_price) * 100
            print('percent_diff', percent_diff)
            if abs(percent_diff) >= 1:
                print(f'diff: {prev_diff}, price: {price}, before price {prev_price},'
                      f' price difference price: {percent_diff}% ,'
                      f'  date: {date}')
        prev_price = price
        prev_diff = diff


def evaluate_technical():
    df = read_database()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['technical_bullish'], mode='lines', name='Technical Bullish'))
    fig.update_layout(title='Technical Indicators')
    fig.show()


if __name__ == '__main__':
    evaluate_technical()
