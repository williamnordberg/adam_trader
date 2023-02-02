import pandas as pd
import numpy as np
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import chi2
from sklearn import preprocessing
from sklearn.metrics import r2_score
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.svm import SVR
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from numpy import ravel


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

# Telegram has not enugh data
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
data['Rate'] = data_rate['Rate'].fillna(method='bfill')

# 1. FG and Git is not avilable before 2018 'Perp_intrest' and  'Perp_volume' after 2020-02-09
print("feature with null value\n", data.isnull().sum())


# A. Split data yearly and calculate correlation
def process_data(data_to_split, start_date, end_date, file_name):
    data_subset = data_to_split[start_date:end_date]
    data_subset = data_subset.dropna(axis=1)
    corr = data_subset.corrwith(data_subset['Close'])
    corr.nlargest(40).to_csv(file_name)
    return data_subset


data16 = process_data(data, '2016-01-01', '2017-01-01', 'corr16.csv')
data17 = process_data(data, '2017', '2018', 'corr17.csv')
data18 = process_data(data, '2018', '2019', 'corr18.csv')
data19 = process_data(data, '2019', '2020', 'corr19.csv')
data20 = process_data(data, '2020', '2021', 'corr20.csv')
data21 = process_data(data, '2021', '2022', 'corr21.csv')
data22 = process_data(data, '2022', None, 'corr22.csv')


# A1. calculate Chi_squerd on yearly dataset


def feature_select(data_feature_select, year):
    data_feature_select.dropna(axis=1, how='all')
    X = data_feature_select.iloc[:, 1:169]  # independent variable columns
    y = data_feature_select['Close']  # target variable column (price range)

    # extracting top 10 best features by applying SelectKBest class
    bestfeatures = SelectKBest(score_func=chi2, k=10)
    label_encoder = preprocessing.LabelEncoder()
    y = label_encoder.fit_transform(y)
    fit = bestfeatures.fit(X, y)
    dfscores = pd.DataFrame(fit.scores_)
    dfcolumns = pd.DataFrame(X.columns)

    # concat two dataframes
    feature_scores = pd.concat([dfcolumns, dfscores], axis=1)
    feature_scores.columns = ['Specs', 'Score']  # naming the dataframe columns
    print(f"Year {year}:")
    # print(feature_scores.nlargest(10, 'Score'))   # printing 10 best features


feature_select(data16, 16)
feature_select(data17, 17)
feature_select(data18, 18)
feature_select(data19, 19)
feature_select(data20, 20)
feature_select(data21, 21)
feature_select(data22, 22)


# A2. Regressions on yearly

def mape(Y_Predicted, Y_actual):
    mape = np.mean(np.abs((Y_actual - Y_Predicted)/Y_actual), axis=0)*100
    return float(mape)

def five_regression(data_to_regression):
    X = data_to_regression[['DiffLast', 'DiffMean', 'CapAct1yrUSD', 'HashRate', 'Open']]
    y = data_to_regression[['Close']]
    X_train, X_test, y_train, y_test = train_test_split(X, y,
                                                        test_size=0.2,
                                                        random_state=0)

    # 1.regression
    linear_model = LinearRegression()
    linear_model.fit(X_train, y_train)
    prediction = linear_model.predict(X_test)
    print('Linear_mape:', mape(prediction, y_test))

    # 2.polynomial
    polynomial = PolynomialFeatures(degree=3)
    X_polynomial = polynomial.fit_transform(X_train)
    model = LinearRegression()
    model.fit(X_polynomial, y_train)
    predictions_poly = model.predict(polynomial.transform(X_test))
    print('MAPE_polynomial:', mape(predictions_poly, y_test))

    # 3.data scaling preprocessing +SVR Model
    X_scaler = StandardScaler()
    y_scaler = StandardScaler()
    X_train_scaled = X_scaler.fit_transform(X_train)
    y_train_scaled = y_scaler.fit_transform(y_train)
    svr_model = SVR(kernel='rbf')
    svr_model.fit(X_train_scaled, y_train_scaled)
    X_test_scaled = X_scaler.transform(X_test)
    results = svr_model.predict(X_test_scaled).reshape(-1, 1)
    predictions_svr = y_scaler.inverse_transform(results)
    print('\n MAPE_svr:', mape(predictions_svr, y_test))

    # 4.regression tree
    decision_model = DecisionTreeRegressor(random_state=0)
    decision_model.fit(X_train, y_train)
    predictions_tree = decision_model.predict(X_test).reshape(-1, 1)
    print('\n MAPE_decision_tree:', mape(y_test, predictions_tree), )


five_regression(data22)
