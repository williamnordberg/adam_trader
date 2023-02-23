import lightgbm as lgb
import math
import numpy as np
import pandas as pd
from numpy import ravel
from sklearn import preprocessing
from sklearn.ensemble import RandomForestRegressor
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import chi2
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import PolynomialFeatures, StandardScaler
from sklearn.svm import SVR
from sklearn.tree import DecisionTreeRegressor
from xgboost import XGBRegressor
from sklearn.ensemble import AdaBoostRegressor

# region load datasets
data = pd.read_csv('C:/will/Python_project/adam_trader/datasets/BTC-to-merg.csv',
                   index_col='Date',
                   infer_datetime_format=True,
                   parse_dates=True
                   )

# DXY
data_DXY = pd.read_csv('C:/will/Python_project/adam_trader/datasets/DXY.csv',
                       index_col='Date',
                       infer_datetime_format=True,
                       parse_dates=True
                       )

data['DXY'] = data_DXY['Open']
data['DXY'] = data['DXY'].fillna(method='ffill')

# stock
data_stock = pd.read_csv('C:/will/Python_project/adam_trader/datasets/SPX-COMP.csv',
                         index_col='Date',
                         infer_datetime_format=True,
                         parse_dates=True
                         )
data['SPX'] = data_stock['SPX'].fillna(method='ffill')
data['COMP'] = data_stock['Camp'].fillna(method='ffill')

# twitter
data_twitter = pd.read_csv('C:/will/Python_project/adam_trader/datasets/Twitt_bitinfochart.csv',
                           index_col='Date',
                           infer_datetime_format=True,
                           parse_dates=True
                           )

data['Twitter'] = data_twitter['Value']

# F&G
data_fg = pd.read_csv('C:/will/Python_project/adam_trader/datasets/fear_from_2018.csv',
                      index_col='timestamp',
                      infer_datetime_format=True,
                      parse_dates=True
                      )

data['FG'] = data_fg['value']

# gitHub
data_git = pd.read_csv('C:/will/Python_project/adam_trader/datasets/github.csv',
                       index_col='DateTime',
                       infer_datetime_format=True,
                       parse_dates=True
                       )
data['Git'] = data_git['Open Issues']

# Telegram has not enough data
# derivative_perpetual
data_derivative_per = pd.read_csv('C:/will/Python_project/adam_trader/datasets/derivative_perpetual.csv',
                                  index_col='DateTime',
                                  infer_datetime_format=True,
                                  parse_dates=True
                                  )
data['Perp_intrest'] = data_derivative_per['Open_in'].fillna(method='ffill')
data['Perp_volume'] = data_derivative_per['volume'].fillna(method='ffill')

# interest rate
data_rate = pd.read_csv('C:/will/Python_project/adam_trader/datasets/rate.csv',
                        index_col='Date',
                        infer_datetime_format=True,
                        parse_dates=True
                        )
data['Rate'] = data_rate['Rate']

# Forward fill missing values with the last non-null value
data['Rate'] = data['Rate'].fillna(method='ffill')

# Backward fill missing values with the next non-null value, but only up to the next value change
data['Rate'] = data['Rate'].fillna(method='bfill', limit=1)
print(data['Rate'])



# 1. FG and Git is not available before 2018 'Perp_intrest' and  'Perp_volume' after 2020-02-09
print("feature with null value", data.isnull().sum())

print('data shape1 ', data.shape)

# endregion

# region  A. Split data yearly and calculate correlation


def process_data(data_to_split, start_date, end_date, file_name):
    data_subset = data_to_split[start_date:end_date]
    data_subset = data_subset.dropna(axis=1)
    corr = data_subset.corrwith(data_subset['Close'])
    # corr.nlargest(40).to_csv(file_name)
    return data_subset


data16 = process_data(data, '2016-01-01', '2017-01-01', 'corr16.csv')
data17 = process_data(data, '2017', '2018', 'corr17.csv')
data18 = process_data(data, '2018', '2019', 'corr18.csv')
data19 = process_data(data, '2019', '2020', 'corr19.csv')
data20 = process_data(data, '2020', '2021', 'corr20.csv')
data21 = process_data(data, '2021', '2022', 'corr21.csv')
data22 = process_data(data, '2022', None, 'corr22.csv')
data22.to_csv('main_dataset.csv')
data.to_csv('data.csv')
# endregion

# region A1. calculate Chi_squerd on yearly dataset


def feature_select(data_feature_select):
    data_feature_select.dropna(axis=1, how='all')
    X = data_feature_select.iloc[:, 1:169]  # independent variable columns
    y = data_feature_select['Close']  # target variable column (price range)
    bestfeatures = SelectKBest(score_func=chi2, k=10)
    label_encoder = preprocessing.LabelEncoder()
    y = label_encoder.fit_transform(y)
    fit = bestfeatures.fit(X, y)
    dfscores = pd.DataFrame(fit.scores_)
    dfcolumns = pd.DataFrame(X.columns)
    # concat two dataframes
    feature_scores = pd.concat([dfcolumns, dfscores], axis=1)
    feature_scores.columns = ['Specs', 'Score']  # naming the dataframe columns
    # print(feature_scores.nlargest(10, 'Score'))   # printing 10 best features


feature_select(data16)
feature_select(data17)
feature_select(data18)
feature_select(data19)
feature_select(data20)
feature_select(data21)
feature_select(data22)
# endregion

# region A2. Regressions on yearly


def mean_absolute_percentage_error(y_true, y_prediction):
    y_true, y_prediction = np.array(y_true), np.array(y_prediction)
    return np.mean(np.abs((y_true - y_prediction) / y_true)) * 100


def seven_regression(data_to_regression1):
    X = data_to_regression1[['DiffLast', 'DiffMean', 'CapAct1yrUSD', 'HashRate', 'Open']]
    y = data_to_regression1[['Close']]
    X_train, X_test, y_train, y_test = train_test_split(X, y,
                                                        test_size=0.2,
                                                        random_state=0)

    # 1.regression
    linear_model = LinearRegression()
    linear_model.fit(X_train, y_train)
    prediction = linear_model.predict(X_test)
    print('MAPE_linear:', mean_absolute_percentage_error(prediction, y_test))

    # 2.polynomial
    polynomial = PolynomialFeatures(degree=3)
    X_polynomial = polynomial.fit_transform(X_train)
    model = LinearRegression()
    model.fit(X_polynomial, y_train)
    predictions_poly = model.predict(polynomial.transform(X_test))
    print('MAPE_polynomial:', mean_absolute_percentage_error(predictions_poly, y_test))

    # 3.data scaling preprocessing +SVR Model
    X_scaler = StandardScaler()
    y_scaler = StandardScaler()
    X_train_scaled = X_scaler.fit_transform(X_train)
    y_train_scaled = y_scaler.fit_transform(y_train)
    svr_model = SVR(kernel='rbf')
    svr_model.fit(X_train_scaled, ravel(y_train_scaled))
    X_test_scaled = X_scaler.transform(X_test)
    results = svr_model.predict(X_test_scaled).reshape(-1, 1)
    predictions_svr = y_scaler.inverse_transform(results)
    print('MAPE_svr:', mean_absolute_percentage_error(predictions_svr, y_test))

    # 4.regression tree
    decision_model = DecisionTreeRegressor(random_state=0)
    decision_model.fit(X_train, y_train)
    predictions_tree = decision_model.predict(X_test).reshape(-1, 1)
    print('MAPE_decision_tree:', mean_absolute_percentage_error(y_test, predictions_tree))

    # 5.random forest
    forest_model = RandomForestRegressor(n_estimators=3, random_state=0)
    forest_model.fit(X_train, ravel(y_train))
    predictions_forest = forest_model.predict(X_train)
    # print('\n''r2_forest:',r2_score(y_train, predictions_forest))
    print('MAPE_forest:', mean_absolute_percentage_error(y_test, predictions_forest))

    # 6.ADA booster
    training_amount = 0.8
    ROWS = data.shape[0]
    index = math.floor(ROWS * training_amount)
    train_x = data[['DiffLast', 'DiffMean', 'CapAct1yrUSD', 'HashRate', 'Open']][:index].to_numpy()
    train_y = data['Close'][:index]

    test_x = data[['DiffLast', 'DiffMean', 'CapAct1yrUSD', 'HashRate', 'Open']][index:].to_numpy()
    test_y = data['Close'][index:]

    model = AdaBoostRegressor()
    model.fit(train_x, train_y)
    predictions_ADA = model.predict(test_x)
    pd.Series(predictions_ADA, index=test_y.index)
    r2_score(test_y, predictions_ADA)
    print('MAPE_ADA:', mean_absolute_percentage_error(test_y, predictions_ADA))

    # 7. XGBoost
    xgb_model = XGBRegressor(n_estimators=100, learning_rate=0.05, random_state=0)
    xgb_model.fit(X_train, y_train)
    xgb_predictions = xgb_model.predict(X_test)
    xgb_mape = mean_absolute_percentage_error(y_test, xgb_predictions)
    print("MAPE for XGBoost:", xgb_mape)

    # 8. LightGBM
    lgb_model = lgb.LGBMRegressor(boosting_type='gbdt', n_estimators=100, learning_rate=0.05, random_state=0)
    lgb_model.fit(X_train, y_train)
    lgb_predictions = lgb_model.predict(X_test)
    lgb_mape = mean_absolute_percentage_error(y_test, lgb_predictions)
    print("MAPE for LightGBM:", lgb_mape)


data_to_regression = data
years = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023]
for year, data_to_regression in zip(years, [data, data16, data17, data18, data19, data20, data21, data22]):
    seven_regression(data_to_regression)
    print('\n', '***************', year, '***************', '\n')

# endregion

# region B. Add technical data to dataset

def exponential_moving_average(data_in_function, window):
    weights = np.exp(np.linspace(-1., 0., window))
    weights /= weights.sum()
    a = np.convolve(data_in_function, weights, mode='full')[:len(data_in_function)]
    a[:window] = a[window]
    return a


def bollinger_bands(data_to_bb, window, num_std_dev):
    moving_average = exponential_moving_average(data_to_bb, window)
    std_dev = np.std(data_to_bb)
    upper_band = moving_average + num_std_dev * std_dev
    lower_band = moving_average - num_std_dev * std_dev
    return upper_band, moving_average, lower_band


def relative_strength_index(data_rsi, window):
    delta = data_rsi - np.roll(data_rsi, 1)
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)
    avg_gain = exponential_moving_average(gain, window)
    avg_loss = exponential_moving_average(loss, window)
    rs = avg_gain / avg_loss
    rsi = 100.0 - (100.0 / (1.0 + rs))
    return rsi


def macd(data_macd, fast_window=12, slow_window=26, signal_window=9):
    fast_ema = exponential_moving_average(data_macd, fast_window)
    slow_ema = exponential_moving_average(data_macd, slow_window)
    macd_in_func = fast_ema - slow_ema
    signal = exponential_moving_average(macd_in_func, signal_window)
    histogram = macd_in_func - signal
    return macd_in_func, signal, histogram


data['ema200'] = exponential_moving_average(data['Close'], 200)
data['ema50'] = exponential_moving_average(data['Close'], 50)
data['ema20'] = exponential_moving_average(data['Close'], 20)
data['upper_band'], data['middle_band'], data['lower_band'] = bollinger_bands(data['Close'], window=20, num_std_dev=2)
data['RSI'] = relative_strength_index(data['Close'], window=14)
data['MACD'], data['MACD signal'], data['MACD histogram'] = macd(data['Close'], fast_window=12, slow_window=26,
                                                                 signal_window=9)

# EMA 1(20>50>200) 2(50>20>200) 3(200>50>20) 4(20>200>50) 5(200>20>50) 6(50>200>20)
# BB 1(p>up b) 2(up b< P >M b) 3(M band < P>L b) 4(P< l ba)
# RSI 1(P>70) 2(P < 30) 3( 70< P >30 )
# MACD 1 (MACD > signal) 2 ( MACD < signal)

# 0 3 0 0
data_0300 = data.loc[((data['ema20'] > data['ema50']) & (data['ema50'] > data['ema200']))
                     & (data['lower_band'] < data['Close'])
                     & (data['RSI'] > 70)
                     & (data['MACD'] > data['MACD signal'])
                     ]
print('data_0300', data_0300.shape)

# 0 3 2 0
data_0320 = data.loc[((data['ema20'] > data['ema50']) & (data['ema50'] > data['ema200']))
                     & (data['lower_band'] < data['Close'])
                     & ((data['RSI'] > 30) & (data['RSI'] < 70))
                     & (data['MACD'] > data['MACD signal'])
                     ]
print('data_0320', data_0320.shape)

# 0 3 2 1
data_0321 = data.loc[((data['ema20'] > data['ema50']) & (data['ema50'] > data['ema200']))
                     & (data['lower_band'] < data['Close'])
                     & ((data['RSI'] > 30) & (data['RSI'] < 70))
                     & (data['MACD'] < data['MACD signal'])
                     ]
print('data_0321', data_0321.shape)

# 1 3 1 1
data_1311 = data.loc[((data['ema50'] > data['ema20']) & (data['ema20'] > data['ema200']))
                     & (data['lower_band'] < data['Close'])
                     & (data['RSI'] < 30)
                     & (data['MACD'] < data['MACD signal'])
                     ]
print('data_1311', data_1311.shape)

# 1 3 2 0
data_1320 = data.loc[((data['ema50'] > data['ema20']) & (data['ema20'] > data['ema200']))
                     & (data['lower_band'] < data['Close'])
                     & ((data['RSI'] > 30) & (data['RSI'] < 70))
                     & (data['MACD'] > data['MACD signal'])
                     ]
print('data_1320', data_1320.shape)

# 1 3 2 1
data_1321 = data.loc[((data['ema50'] > data['ema20']) & (data['ema20'] > data['ema200']))
                     & (data['lower_band'] < data['Close'])
                     & ((data['RSI'] > 30) & (data['RSI'] < 70))
                     & (data['MACD'] < data['MACD signal'])
                     ]
print('data_1321', data_1321.shape)

# 2 3 0 0
data_2300 = data.loc[((data['ema200'] > data['ema50']) & (data['ema50'] > data['ema20']))
                     & (data['lower_band'] < data['Close'])
                     & (data['RSI'] > 70)
                     & (data['MACD'] > data['MACD signal'])
                     ]
print('data_2300', data_2300.shape)

# 2 3 1 0
data_2310 = data.loc[((data['ema200'] > data['ema50']) & (data['ema50'] > data['ema20']))
                     & (data['lower_band'] < data['Close'])
                     & (data['RSI'] < 30)
                     & (data['MACD'] > data['MACD signal'])
                     ]
print('data_2310', data_2310.shape)

# 2 3 1 1
data_2311 = data.loc[((data['ema200'] > data['ema50']) & (data['ema50'] > data['ema20']))
                     & (data['lower_band'] < data['Close'])
                     & (data['RSI'] < 30)
                     & (data['MACD'] < data['MACD signal'])
                     ]
print('data_2311', data_2311.shape)

# 2 3 2 0
data_2320 = data.loc[((data['ema200'] > data['ema50']) & (data['ema50'] > data['ema20']))
                     & (data['lower_band'] < data['Close'])
                     & ((data['RSI'] > 30) & (data['RSI'] < 70))
                     & (data['MACD'] > data['MACD signal'])
                     ]
print('data_2320', data_2320.shape)

# 2 3 2 1
data_2321 = data.loc[((data['ema200'] > data['ema50']) & (data['ema50'] > data['ema20']))
                     & (data['lower_band'] < data['Close'])
                     & ((data['RSI'] > 30) & (data['RSI'] < 70))
                     & (data['MACD'] < data['MACD signal'])
                     ]
print('data_2321', data_2321.shape)

# 3 3 0 0
data_3300 = data.loc[((data['ema20'] > data['ema200']) & (data['ema200'] > data['ema50']))
                     & (data['lower_band'] < data['Close'])
                     & (data['RSI'] > 70)
                     & (data['MACD'] > data['MACD signal'])
                     ]
print('data_3300', data_3300.shape)

# 3 3 2 0
data_3320 = data.loc[((data['ema20'] > data['ema200']) & (data['ema200'] > data['ema50']))
                     & (data['lower_band'] < data['Close'])
                     & ((data['RSI'] > 30) & (data['RSI'] < 70))
                     & (data['MACD'] > data['MACD signal'])
                     ]
print('data_3320', data_3320.shape)

# 3 3 2 1
data_3321 = data.loc[((data['ema20'] > data['ema200']) & (data['ema200'] > data['ema50']))
                     & (data['lower_band'] < data['Close'])
                     & ((data['RSI'] > 30) & (data['RSI'] < 70))
                     & (data['MACD'] < data['MACD signal'])
                     ]
print('data_3321', data_3321.shape)

# 4 3 0 0
data_4300 = data.loc[((data['ema200'] > data['ema20']) & (data['ema20'] > data['ema50']))
                     & (data['lower_band'] < data['Close'])
                     & (data['RSI'] > 70)
                     & (data['MACD'] > data['MACD signal'])
                     ]
print('data_4300', data_4300.shape)

# 4 3 2 0
data_4320 = data.loc[((data['ema200'] > data['ema20']) & (data['ema20'] > data['ema50']))
                     & (data['lower_band'] < data['Close'])
                     & ((data['RSI'] > 30) & (data['RSI'] < 70))
                     & (data['MACD'] > data['MACD signal'])
                     ]
print('data_4320', data_4320.shape)

# 4 3 2 1
data_4321 = data.loc[((data['ema200'] > data['ema20']) & (data['ema20'] > data['ema50']))
                     & (data['lower_band'] < data['Close'])
                     & ((data['RSI'] > 30) & (data['RSI'] < 70))
                     & (data['MACD'] < data['MACD signal'])
                     ]
print('data_4321', data_4321.shape)

# 5 3 1 1
data_5311 = data.loc[((data['ema50'] > data['ema200']) & (data['ema200'] > data['ema20']))
                     & (data['lower_band'] < data['Close'])
                     & (data['RSI'] < 30)
                     & (data['MACD'] < data['MACD signal'])
                     ]
print('data_5311', data_5311.shape)

# 5 3 2 0
data_5320 = data.loc[((data['ema50'] > data['ema200']) & (data['ema200'] > data['ema20']))
                     & (data['lower_band'] < data['Close'])
                     & ((data['RSI'] > 30) & (data['RSI'] < 70))
                     & (data['MACD'] > data['MACD signal'])
                     ]
print('data_5320', data_5320.shape)

Technical_data_list = [data_0300, data_0320, data_0321, data_1311, data_1320, data_1321,
                       data_2300, data_2310, data_2311, data_2320, data_2321, data_3300, data_3320, data_3321,
                       data_4300, data_4320, data_4321, data_5311, data_5320]

for data_to_extract_features in Technical_data_list:
    var_name = [k for k, v in locals().items() if v is data_to_extract_features][0]
    print('************', var_name, '************')
    data_to_extract_features = data_to_extract_features.dropna(axis=1)
    # clip method of a DataFrame to replace all values below 0 with 0
    data_to_extract_features = data_to_extract_features.clip(lower=0)
    feature_select(data_to_extract_features)
    # consider adjusting features, might pass it from feature select
    seven_regression(data_to_extract_features)

# endregion
