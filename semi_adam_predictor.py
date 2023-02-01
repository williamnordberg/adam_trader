import pandas
import numpy
import matplotlib.pyplot as plt

data = pandas.read_csv('/content/drive/MyDrive/AdamData/datasets/BTC-to-merg.csv',
                       index_col = 'Date',
                       infer_datetime_format = True,
                       parse_dates = True 
                       )

#DXY
data_DXY = pandas.read_csv('/content/drive/MyDrive/AdamData/datasets/DXY.csv',
                       index_col = 'Date',
                       infer_datetime_format = True,
                       parse_dates = True 
                       )

data['DXY'] = data_DXY['Open']
data['DXY'] = data['DXY'].fillna(method = 'ffill')

#stock
data_stock = pandas.read_csv('/content/drive/MyDrive/AdamData/datasets/SPX-COMP.csv',
                       index_col = 'Date',
                       infer_datetime_format = True,
                       parse_dates = True 
                       )
data['SPX'] = data_stock['SPX']
data['COMP'] = data_stock['Camp']
data['SPX'] = data['DXY'].fillna(method = 'ffill')
data['COMP'] = data['DXY'].fillna(method = 'ffill')

#twitter
data_twitter = pandas.read_csv('/content/drive/MyDrive/AdamData/datasets/Twitt_bitinfochart.csv',
                       index_col = 'Date',
                       infer_datetime_format = True,
                       parse_dates = True 
                       )

data['Twitter'] = data_twitter['Value']

#F&G
data_fg = pandas.read_csv('/content/drive/MyDrive/AdamData/datasets/fear_from_2018.csv',
                       index_col = 'timestamp',
                       infer_datetime_format = True,
                       parse_dates = True 
                       )

data['FG'] = data_fg['value']

#gitHub
data_git = pandas.read_csv('/content/drive/MyDrive/AdamData/datasets/github.csv',
                            index_col = 'DateTime',
                            infer_datetime_format= True,
                            parse_dates = True
                            )
data['Git'] = data_git['Open Issues']

#Telegram has not enough data
#derivative_perpetual
data_derivative_per = pandas.read_csv('/content/drive/MyDrive/AdamData/datasets/derivative_perpetual.csv',
                            index_col = 'DateTime',
                            infer_datetime_format= True,
                            parse_dates = True
                            )
data['Perp_intrest'] = data_derivative_per['Open_in']
data['Perp_volume'] = data_derivative_per['volume']
data['Perp_intrest'] = data['Perp_intrest'].fillna(method= 'ffill')
data['Perp_volume'] = data['Perp_volume'].fillna(method= 'ffill')
#intrest rate
data_rate = pandas.read_csv('/content/drive/MyDrive/AdamData/datasets/rate.csv',
                            index_col = 'Date',
                            infer_datetime_format= True,
                            parse_dates = True
                            )
data['Rate'] = data_rate['Rate']
data['Rate'] = data['Rate'].fillna(method = 'bfill')

# 1. FG and Git is not avilable before 2018
# 2. 'Perp_intrest' and  'Perp_volume' after 2020-02-09
data.isnull().sum()

"""

```
```

# A. Split data yearly and calculate correlation"""

data16 = data['2016-01-01':'2017-01-01']
data16 = data16.dropna(axis=1)
corr16 = data16.corrwith(data16['Close'])
corr16.nlargest(40).to_csv('corr16.csv')

data17 = data['2017':'2018']
data17 = data17.dropna(axis=1)
corr17 = data17.corrwith(data17['Close'])
corr17.nlargest(40).to_csv('corr17.csv')


data18 = data['2018':'2019']
data18 = data18.dropna(axis=1)
corr18 = data18.corrwith(data18['Close'])
corr18.nlargest(40).to_csv('corr18.csv')


data19 = data['2019':'2020']
data19 = data19.dropna(axis=1)
corr19 = data19.corrwith(data19['Close'])
corr19.nlargest(40).to_csv('corr19.csv')


data20 = data['2020':'2021']
data20 = data20.dropna(axis=1)
corr20 = data20.corrwith(data20['Close'])
corr20.nlargest(40).to_csv('corr20.csv')


data21 = data['2021':'2022']
data21 = data21.dropna(axis=1)
corr21 = data21.corrwith(data21['Close'])
corr21.nlargest(40).to_csv('corr21.csv')


data22 = data['2022':]
data22 = data22.dropna(axis=1)
corr22 = data22.corrwith(data22['Close'])
corr22.nlargest(40).to_csv('corr22.csv')

corr = data.corrwith(data['Close'])

corr.nlargest(40).to_csv('corr.csv')

"""## A1. calculate Chi_squerd on yearly dataset"""

#22
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import chi2

X = data22.iloc[:,1:142]  #independent variable columns
y = data22['Close']   #target variable column (price range)
 
#extracting top 10 best features by applying SelectKBest class
bestfeatures = SelectKBest(score_func=chi2, k=10)
from sklearn import preprocessing
label_encoder = preprocessing.LabelEncoder()
y = label_encoder.fit_transform(y)
fit = bestfeatures.fit(X,y)
dfscores = pandas.DataFrame(fit.scores_)
dfcolumns = pandas.DataFrame(X.columns)
 
#concat two dataframes
featureScores = pandas.concat([dfcolumns,dfscores],axis=1)
featureScores.columns = ['Specs','Score']  #naming the dataframe columns
print(featureScores.nlargest(15,'Score'))  #printing 19 best features

#21
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import chi2

X = data21.iloc[:,1:168]  #independent variable columns
y = data21['Close']   #target variable column (price range)
 
#extracting top 10 best features by applying SelectKBest class
bestfeatures = SelectKBest(score_func=chi2, k=10)
from sklearn import preprocessing
label_encoder = preprocessing.LabelEncoder()
y = label_encoder.fit_transform(y)
fit = bestfeatures.fit(X,y)
dfscores = pandas.DataFrame(fit.scores_)
dfcolumns = pandas.DataFrame(X.columns)
 
#concat two dataframes
featureScores = pandas.concat([dfcolumns,dfscores],axis=1)
featureScores.columns = ['Specs','Score']  #naming the dataframe columns
print(featureScores.nlargest(15,'Score'))  #printing 19 best features

#20
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import chi2

data20.dropna(axis=1, how='all')
X = data20.iloc[:,1:169]  #independent variable columns
y = data20['Close']   #target variable column (price range)
 
#extracting top 10 best features by applying SelectKBest class
bestfeatures = SelectKBest(score_func=chi2, k=10)
from sklearn import preprocessing
label_encoder = preprocessing.LabelEncoder()
y = label_encoder.fit_transform(y)
fit = bestfeatures.fit(X,y)
dfscores = pandas.DataFrame(fit.scores_)
dfcolumns = pandas.DataFrame(X.columns)
 
#concat two dataframes
featureScores = pandas.concat([dfcolumns,dfscores],axis=1)
featureScores.columns = ['Specs','Score']  #naming the dataframe columns
print(featureScores.nlargest(15,'Score'))  #printing 19 best features

#19
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import chi2

data19.dropna(axis=1, how='all')
X = data19.iloc[:,1:169]  #independent variable columns
y = data19['Close']   #target variable column (price range)
 
#extracting top 10 best features by applying SelectKBest class
bestfeatures = SelectKBest(score_func=chi2, k=10)
from sklearn import preprocessing
label_encoder = preprocessing.LabelEncoder()
y = label_encoder.fit_transform(y)
fit = bestfeatures.fit(X,y)
dfscores = pandas.DataFrame(fit.scores_)
dfcolumns = pandas.DataFrame(X.columns)
 
#concat two dataframes
featureScores = pandas.concat([dfcolumns,dfscores],axis=1)
featureScores.columns = ['Specs','Score']  #naming the dataframe columns
print(featureScores.nlargest(15,'Score'))  #printing 19 best features

#16
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import chi2

data16.dropna(axis=1, how='all')
X = data16.iloc[:,1:169]  #independent variable columns
y = data16['Close']   #target variable column (price range)
 
#extracting top 10 best features by applying SelectKBest class
bestfeatures = SelectKBest(score_func=chi2, k=10)
from sklearn import preprocessing
label_encoder = preprocessing.LabelEncoder()
y = label_encoder.fit_transform(y)
fit = bestfeatures.fit(X,y)
dfscores = pandas.DataFrame(fit.scores_)
dfcolumns = pandas.DataFrame(X.columns)
 
#concat two dataframes
featureScores = pandas.concat([dfcolumns,dfscores],axis=1)
featureScores.columns = ['Specs','Score']  #naming the dataframe columns
print(featureScores.nlargest(15,'Score'))  #printing 19 best features

#all
data = data.dropna(axis=1)

from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import chi2

data.drop(data.iloc[:, 88:90], inplace=True, axis=1) #drop negative 
data.dropna(axis=1, how='all')
X = data.iloc[:,1:169]  #independent variable columns
y = data['Close']   #target variable column (price range)
 
#extracting top 10 best features by applying SelectKBest class
bestfeatures = SelectKBest(score_func=chi2, k=10)
from sklearn import preprocessing
label_encoder = preprocessing.LabelEncoder()
y = label_encoder.fit_transform(y)
fit = bestfeatures.fit(X,y)
dfscores = pandas.DataFrame(fit.scores_)
dfcolumns = pandas.DataFrame(X.columns)
 
#concat two dataframes
featureScores = pandas.concat([dfcolumns,dfscores],axis=1)
featureScores.columns = ['Specs','Score']  #naming the dataframe columns
print(featureScores.nlargest(15,'Score'))  #printing 19 best features

"""## A2. Regressions on yearly

"""

from sklearn.metrics import r2_score
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVR
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor

def MAPE(predictions, actual_y):
  error = numpy.mean(abs(1-(predictions / actual_y)))
  return float(error) * 100

#2022
X = data22[['DiffLast','DiffMean','CapAct1yrUSD']]
y = data22[['Close']]

X_train, X_test, y_train, y_test = train_test_split(X, y,
                                   test_size = 0.2,
                                   random_state = 0)
linear_model = LinearRegression()
linear_model.fit(X_train, y_train)
prediction = linear_model.predict(X_test)
print('r2:',r2_score(y_test, prediction))
print( 'MAPE:', MAPE(prediction, y_test) )
#polynomical
polynomial = PolynomialFeatures(degree = 3)
X_polynomial = polynomial.fit_transform(X_train)
model = LinearRegression()
model.fit(X_polynomial, y_train)
predictions_poly = model.predict(polynomial.transform(X_test))
print('r2_polynomial_score:', r2_score(y_test, predictions_poly))
print('MAPE_polynomial:',MAPE(predictions_poly, y_test))

# data scaling preprocessing +SVM Model
X_scaler = StandardScaler()
y_scaler = StandardScaler()
X_train_scaled = X_scaler.fit_transform(X_train)
y_train_scaled = y_scaler.fit_transform(y_train)
svr_model = SVR(kernel = 'rbf')
svr_model.fit(X_train_scaled, y_train_scaled)
X_test_scaled = X_scaler.transform(X_test)
results= svr_model.predict(X_test_scaled).reshape(-1,1)
predictions_svr = y_scaler.inverse_transform(results)
print('r2_svr_score:',r2_score(y_test, predictions_svr))
print('MAPE_svr:',MAPE(predictions_svr, y_test))

#regression tree
decision_model = DecisionTreeRegressor(random_state = 0)
decision_model.fit(X_train, y_train)
predictions_tree = decision_model.predict(X_test).reshape(-1,1)
print('r2_decision_tree:',r2_score(y_test, predictions_tree))
print( 'MAPE_decision_tree:', MAPE(y_test, predictions_tree) )

#random forest
forest_model = RandomForestRegressor(n_estimators = 3,random_state= 0)
forest_model.fit(X_train, y_train)
predictions_forest = forest_model.predict(X_train)
print('\n''r2_forest:',r2_score(y_train, predictions_forest))
print( 'MAPE_forest:', MAPE(y_test, predictions_tree),'\n' )


#plotting
prediction_series = pandas.DataFrame(prediction, index = y_test.index, columns=['prediction'])
y_test['prediction'] = prediction_series['prediction']
y_test.plot()

#2021
X = data21[['DiffLast','DiffMean','CapAct1yrUSD','SplyMiner1HopAllUSD','SplyMiner0HopAllUSD','Open']]
y = data21[['Close']]

X_train, X_test, y_train, y_test = train_test_split(X, y,
                                   test_size = 0.2,
                                   random_state = 0)
linear_model = LinearRegression()
linear_model.fit(X_train, y_train)
prediction = linear_model.predict(X_test)
print('r2:',r2_score(y_test, prediction))
print( 'MAPE:', MAPE(prediction, y_test) )
#polynomical
polynomial = PolynomialFeatures(degree = 3)
X_polynomial = polynomial.fit_transform(X_train)
model = LinearRegression()
model.fit(X_polynomial, y_train)
predictions_poly = model.predict(polynomial.transform(X_test))
print('r2_polynomial_score:', r2_score(y_test, predictions_poly))
print('MAPE_polynomial:',MAPE(predictions_poly, y_test))

# data scaling preprocessing +SVM Model
X_scaler = StandardScaler()
y_scaler = StandardScaler()
X_train_scaled = X_scaler.fit_transform(X_train)
y_train_scaled = y_scaler.fit_transform(y_train)
svr_model = SVR(kernel = 'rbf')
svr_model.fit(X_train_scaled, y_train_scaled)
X_test_scaled = X_scaler.transform(X_test)
results= svr_model.predict(X_test_scaled).reshape(-1,1)
predictions_svr = y_scaler.inverse_transform(results)
print('r2_svr_score:',r2_score(y_test, predictions_svr))
print('MAPE_svr:',MAPE(predictions_svr, y_test))

#regression tree
decision_model = DecisionTreeRegressor(random_state = 0)
decision_model.fit(X_train, y_train)
predictions_tree = decision_model.predict(X_test).reshape(-1,1)
print('r2_decision_tree:',r2_score(y_test, predictions_tree))
print( 'MAPE_decision_tree:', MAPE(y_test, predictions_tree) )

#random forest
forest_model = RandomForestRegressor(n_estimators = 3,random_state= 0)
forest_model.fit(X_train, y_train)
predictions_forest = forest_model.predict(X_train)
print('\n''r2_forest:',r2_score(y_train, predictions_forest))
print( 'MAPE_forest:', MAPE(y_test, predictions_tree),'\n' )

#plotting
prediction_series = pandas.DataFrame(prediction, index = y_test.index, columns=['prediction'])
y_test['prediction'] = prediction_series['prediction']
y_test.plot()

#2020
X = data20[['DiffLast','DiffMean','CapAct1yrUSD','BlkWghtTot','Open']]
y = data20[['Close']]


X_train, X_test, y_train, y_test = train_test_split(X, y,
                                   test_size = 0.2,
                                   random_state = 0)
linear_model = LinearRegression()
linear_model.fit(X_train, y_train)
prediction = linear_model.predict(X_test)
print('r2:',r2_score(y_test, prediction))
print( 'MAPE:', MAPE(prediction, y_test) )
#polynomical
polynomial = PolynomialFeatures(degree = 3)
X_polynomial = polynomial.fit_transform(X_train)
model = LinearRegression()
model.fit(X_polynomial, y_train)
predictions_poly = model.predict(polynomial.transform(X_test))
print('r2_polynomial_score:', r2_score(y_test, predictions_poly))
print('MAPE_polynomial:',MAPE(predictions_poly, y_test))

# data scaling preprocessing +SVM Model
X_scaler = StandardScaler()
y_scaler = StandardScaler()
X_train_scaled = X_scaler.fit_transform(X_train)
y_train_scaled = y_scaler.fit_transform(y_train)
svr_model = SVR(kernel = 'rbf')
svr_model.fit(X_train_scaled, y_train_scaled)
X_test_scaled = X_scaler.transform(X_test)
results= svr_model.predict(X_test_scaled).reshape(-1,1)
predictions_svr = y_scaler.inverse_transform(results)
print('r2_svr_score:',r2_score(y_test, predictions_svr))
print('MAPE_svr:',MAPE(predictions_svr, y_test))

#regression tree
decision_model = DecisionTreeRegressor(random_state = 0)
decision_model.fit(X_train, y_train)
predictions_tree = decision_model.predict(X_test).reshape(-1,1)
print('r2_decision_tree:',r2_score(y_test, predictions_tree))
print( 'MAPE_decision_tree:', MAPE(y_test, predictions_tree) )

#random forest
forest_model = RandomForestRegressor(n_estimators = 3,random_state= 0)
forest_model.fit(X_train, y_train)
predictions_forest = forest_model.predict(X_train)
print('\n''r2_forest:',r2_score(y_train, predictions_forest))
print( 'MAPE_forest:', MAPE(y_test, predictions_tree),'\n' )

#plotting
prediction_series = pandas.DataFrame(prediction, index = y_test.index, columns=['prediction'])
y_test['prediction'] = prediction_series['prediction']
y_test.plot()

#2019                
X = data19[['DiffLast','DiffMean','CapAct1yrUSD','SplyMiner1HopAllUSD','Open']]
y = data19[['Close']]


X_train, X_test, y_train, y_test = train_test_split(X, y,
                                   test_size = 0.2,
                                   random_state = 0)
linear_model = LinearRegression()
linear_model.fit(X_train, y_train)
prediction = linear_model.predict(X_test)
print('r2:',r2_score(y_test, prediction))
print( 'MAPE:', MAPE(prediction, y_test) )
#polynomical
polynomial = PolynomialFeatures(degree = 3)
X_polynomial = polynomial.fit_transform(X_train)
model = LinearRegression()
model.fit(X_polynomial, y_train)
predictions_poly = model.predict(polynomial.transform(X_test))
print('r2_polynomial_score:', r2_score(y_test, predictions_poly))
print('MAPE_polynomial:',MAPE(predictions_poly, y_test))

# data scaling preprocessing +SVM Model
X_scaler = StandardScaler()
y_scaler = StandardScaler()
X_train_scaled = X_scaler.fit_transform(X_train)
y_train_scaled = y_scaler.fit_transform(y_train)
svr_model = SVR(kernel = 'rbf')
svr_model.fit(X_train_scaled, y_train_scaled)
X_test_scaled = X_scaler.transform(X_test)
results= svr_model.predict(X_test_scaled).reshape(-1,1)
predictions_svr = y_scaler.inverse_transform(results)
print('r2_svr_score:',r2_score(y_test, predictions_svr))
print('MAPE_svr:',MAPE(predictions_svr, y_test))

#regression tree
decision_model = DecisionTreeRegressor(random_state = 0)
decision_model.fit(X_train, y_train)
predictions_tree = decision_model.predict(X_test).reshape(-1,1)
print('r2_decision_tree:',r2_score(y_test, predictions_tree))
print( 'MAPE_decision_tree:', MAPE(y_test, predictions_tree) )

#random forest
forest_model = RandomForestRegressor(n_estimators = 3,random_state= 0)
forest_model.fit(X_train, y_train)
predictions_forest = forest_model.predict(X_train)
print('\n''r2_forest:',r2_score(y_train, predictions_forest))
print( 'MAPE_forest:', MAPE(y_test, predictions_tree),'\n' )

#plotting
prediction_series = pandas.DataFrame(prediction, index = y_test.index, columns=['prediction'])
y_test['prediction'] = prediction_series['prediction']
y_test.plot()

#2016
X = data16[['DiffLast','DiffMean','CapAct1yrUSD','AdrBalCnt']]
y = data16[['Close']]


X_train, X_test, y_train, y_test = train_test_split(X, y,
                                   test_size = 0.2,
                                   random_state = 0)
linear_model = LinearRegression()
linear_model.fit(X_train, y_train)
prediction = linear_model.predict(X_test)
print('r2:',r2_score(y_test, prediction))
print( 'MAPE:', MAPE(prediction, y_test) )
#polynomical
polynomial = PolynomialFeatures(degree = 3)
X_polynomial = polynomial.fit_transform(X_train)
model = LinearRegression()
model.fit(X_polynomial, y_train)
predictions_poly = model.predict(polynomial.transform(X_test))
print('r2_polynomial_score:', r2_score(y_test, predictions_poly))
print('MAPE_polynomial:',MAPE(predictions_poly, y_test))

# data scaling preprocessing +SVM Model
X_scaler = StandardScaler()
y_scaler = StandardScaler()
X_train_scaled = X_scaler.fit_transform(X_train)
y_train_scaled = y_scaler.fit_transform(y_train)
svr_model = SVR(kernel = 'rbf')
svr_model.fit(X_train_scaled, y_train_scaled)
X_test_scaled = X_scaler.transform(X_test)
results= svr_model.predict(X_test_scaled).reshape(-1,1)
predictions_svr = y_scaler.inverse_transform(results)
print('r2_svr_score:',r2_score(y_test, predictions_svr))
print('MAPE_svr:',MAPE(predictions_svr, y_test))

#regression tree
decision_model = DecisionTreeRegressor(random_state = 0)
decision_model.fit(X_train, y_train)
predictions_tree = decision_model.predict(X_test).reshape(-1,1)
print('r2_decision_tree:',r2_score(y_test, predictions_tree))
print( 'MAPE_decision_tree:', MAPE(y_test, predictions_tree) )

#random forest
forest_model = RandomForestRegressor(n_estimators = 3,random_state= 0)
forest_model.fit(X_train, y_train)
predictions_forest = forest_model.predict(X_train)
print('\n''r2_forest:',r2_score(y_train, predictions_forest))
print( 'MAPE_forest:', MAPE(y_test, predictions_tree),'\n' )

#plotting
prediction_series = pandas.DataFrame(prediction, index = y_test.index, columns=['prediction'])
y_test['prediction'] = prediction_series['prediction']
y_test.plot()

#all
X = data[['DiffLast','DiffMean','CapAct1yrUSD','HashRate','Open']]
y = data[['Close']]

X_train, X_test, y_train, y_test = train_test_split(X, y,
                                   test_size = 0.2,
                                   random_state = 0)
linear_model = LinearRegression()
linear_model.fit(X_train, y_train)
prediction = linear_model.predict(X_test)
print('r2:',r2_score(y_test, prediction))
print( 'MAPE:', MAPE(prediction, y_test) )
#polynomical
polynomial = PolynomialFeatures(degree = 3)
X_polynomial = polynomial.fit_transform(X_train)
model = LinearRegression()
model.fit(X_polynomial, y_train)
predictions_poly = model.predict(polynomial.transform(X_test))
print('r2_polynomial_score:', r2_score(y_test, predictions_poly))
print('MAPE_polynomial:',MAPE(predictions_poly, y_test))

# data scaling preprocessing +SVM Model
X_scaler = StandardScaler()
y_scaler = StandardScaler()
X_train_scaled = X_scaler.fit_transform(X_train)
y_train_scaled = y_scaler.fit_transform(y_train)
svr_model = SVR(kernel = 'rbf')
svr_model.fit(X_train_scaled, y_train_scaled)
X_test_scaled = X_scaler.transform(X_test)
results= svr_model.predict(X_test_scaled).reshape(-1,1)
predictions_svr = y_scaler.inverse_transform(results)
print('r2_svr_score:',r2_score(y_test, predictions_svr))
print('MAPE_svr:',MAPE(predictions_svr, y_test))

#regression tree
decision_model = DecisionTreeRegressor(random_state = 0)
decision_model.fit(X_train, y_train)
predictions_tree = decision_model.predict(X_test).reshape(-1,1)
print('r2_decision_tree:',r2_score(y_test, predictions_tree))
print( 'MAPE_decision_tree:', MAPE(y_test, predictions_tree) )

#random forest
forest_model = RandomForestRegressor(n_estimators = 3,random_state= 0)
forest_model.fit(X_train, y_train)
predictions_forest = forest_model.predict(X_train)
print('\n''r2_forest:',r2_score(y_train, predictions_forest))
print( 'MAPE_forest:', MAPE(y_test, predictions_tree),'\n' )

#plotting
prediction_series = pandas.DataFrame(prediction, index = y_test.index, columns=['prediction'])
y_test['prediction'] = prediction_series['prediction']
y_test.plot()

def five_regression(data): 
  X = data[['DiffLast','DiffMean','CapAct1yrUSD','HashRate','Open']] 
  y = data[['Close']]
  X_train, X_test, y_train, y_test = train_test_split(X, y,
                                   test_size = 0.2,
                                   random_state = 0)
  linear_model = LinearRegression()
  linear_model.fit(X_train, y_train)
  prediction = linear_model.predict(X_test)
  #print('r2:',r2_score(y_test, prediction))
  print( 'MAPE:', MAPE(prediction, y_test) )
  #polynomical
  polynomial = PolynomialFeatures(degree = 3)
  X_polynomial = polynomial.fit_transform(X_train)
  model = LinearRegression()
  model.fit(X_polynomial, y_train)
  predictions_poly = model.predict(polynomial.transform(X_test))
  #print('\n''r2_polynomial_score:', r2_score(y_test, predictions_poly))
  print('MAPE_polynomial:',MAPE(predictions_poly, y_test),) 

  # data scaling preprocessing +SVM Model
  X_scaler = StandardScaler()
  y_scaler = StandardScaler()
  X_train_scaled = X_scaler.fit_transform(X_train)
  y_train_scaled = y_scaler.fit_transform(y_train)
  svr_model = SVR(kernel = 'rbf')
  svr_model.fit(X_train_scaled, y_train_scaled)
  X_test_scaled = X_scaler.transform(X_test)
  results= svr_model.predict(X_test_scaled).reshape(-1,1)
  predictions_svr = y_scaler.inverse_transform(results)
  #print('\n''r2_svr_score:',r2_score(y_test, predictions_svr))
  print('MAPE_svr:',MAPE(predictions_svr, y_test))
  #regression tree
  decision_model = DecisionTreeRegressor(random_state = 0)
  decision_model.fit(X_train, y_train)
  predictions_tree = decision_model.predict(X_test).reshape(-1,1)
  #print('\n''r2_decision_tree:',r2_score(y_test, predictions_tree))
  print( 'MAPE_decision_tree:', MAPE(y_test, predictions_tree), )

  #random forest
  forest_model = RandomForestRegressor(n_estimators = 3,random_state= 0)
  forest_model.fit(X_train, y_train)
  predictions_forest = forest_model.predict(X_train)
  #print('\n''r2_forest:',r2_score(y_train, predictions_forest))
  print( 'MAPE_forest:', MAPE(y_test, predictions_tree) )
  
  import math
  training_amount = 0.8
  ROWS = data.shape[0]
  index = math.floor(ROWS * training_amount)
  train_x = data[['DiffLast','DiffMean','CapAct1yrUSD','HashRate','Open']][:index].to_numpy()
  train_y = data['Close'][:index]
  
  test_x =data[['DiffLast','DiffMean','CapAct1yrUSD','HashRate','Open']][index:].to_numpy()
  test_y = data['Close'][index:]
  from sklearn.ensemble import AdaBoostRegressor
  model = AdaBoostRegressor()
  model.fit(train_x, train_y)
  predictions_ADA = model.predict(test_x)
  prediction_series = pandas.Series(predictions_ADA, index = test_y.index)
  ADA_score = r2_score(test_y, predictions_ADA)
  print('ADA_MAPE:',MAPE(test_y, predictions_ADA))

x=2015
for n in [data, data16, data17, data18, data19, data20, data21, data22]:
 five_regression(n)
 x+=1
 print('\n','***************',x,'***************','\n')



"""# B. Split data based on technical and calculate correlation"""

!curl -L http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz -O && tar xzvf ta-lib-0.4.0-src.tar.gz
!cd ta-lib && ./configure --prefix=/usr && make && make install && cd - && pip install ta-lib
!pip install vectorbt

"""## B1. Add technical to data"""

import talib
#Ema and SMA
data['sma200'] = talib.SMA(data['Close'], timeperiod = 200)
data['ema200'] = talib.EMA(data['Close'], timeperiod = 200)
data['sma50'] = talib.SMA(data['Close'], timeperiod = 50)
data['ema50'] = talib.EMA(data['Close'], timeperiod = 50)
data['sma20'] = talib.SMA(data['Close'], timeperiod = 20)
data['ema20'] = talib.EMA(data['Close'], timeperiod = 20)

#bolliger bands
data['upper_band'], data['middle_band'], data['lower_band'] = talib.BBANDS(data['Close'],
                                                                          timeperiod = 10)
#RSI
data['RSI'] = talib.RSI(data['Close'], timeperiod = 10)

#MACD
data['MACD'], data['MACD signal'], data['MACD histogram'] = talib.MACD(
            data['Close'], fastperiod=12, slowperiod=26, signalperiod=9)

"""## B2. spilit data base on position in 4 different technical

EMA 1(20>50>200) 2(50>20>200) 3(200>50>20) 4(20>200>50) 5(200>20>50) 6(50>200>20)

BB 1(p>up b) 2(up b< P >M b) 3(M band < P>L b) 4(P< l ba)

RSI 1(P>70) 2(P < 30) 3( 70< P >30 )

MACD 1 (MACD > signal) 2 ( MACD < signal)
"""

# 0 0 0 0
data_0000 = data.loc[((data['ema20'] > data['ema50']) & (data['ema50'] > data['ema200'])) 
    & (data['upper_band'] < data['Close'])
    & (data['RSI'] > 70) 
    & (data['MACD'] > data['MACD signal'])
    ]
print('data_0000',data_0000.shape)

# 0 3 0 0
data_0300 = data.loc[((data['ema20'] > data['ema50']) & (data['ema50'] > data['ema200']))
    & (data['lower_band'] < data['Close'])
    & (data['RSI'] > 70) 
    & (data['MACD'] > data['MACD signal'])
    ]
print('data_0300',data_0300.shape)

# 0 3 2 0
data_0320 = data.loc[((data['ema20'] > data['ema50']) & (data['ema50'] > data['ema200']))
    & (data['lower_band'] < data['Close'])
    & ((data['RSI'] > 30) & (data['RSI'] < 70))
    & (data['MACD'] > data['MACD signal'])
    ]
print('data_0320',data_0320.shape)

# 0 3 2 1
data_0321 = data.loc[((data['ema20'] > data['ema50']) & (data['ema50'] > data['ema200']))
    & (data['lower_band'] < data['Close'])
    & ((data['RSI'] > 30) & (data['RSI'] < 70)) 
    & (data['MACD'] < data['MACD signal'])
    ]
print('data_0321',data_0321.shape)

# 1 3 1 1
data_1311 = data.loc[((data['ema50'] > data['ema20']) & (data['ema20'] > data['ema200']))
    & (data['lower_band'] < data['Close'])
    & (data['RSI'] < 30)  
    & (data['MACD'] < data['MACD signal'])
    ]
print('data_1311',data_1311.shape)

# 1 3 2 0
data_1320 = data.loc[((data['ema50'] > data['ema20']) & (data['ema20'] > data['ema200']))
    & (data['lower_band'] < data['Close'])
    & ((data['RSI'] > 30) & (data['RSI'] < 70))
    & (data['MACD'] > data['MACD signal'])
    ]
print('data_1320',data_1320.shape)

# 1 3 2 1
data_1321 = data.loc[((data['ema50'] > data['ema20']) & (data['ema20'] > data['ema200']))
    & (data['lower_band'] < data['Close'])
    & ((data['RSI'] > 30) & (data['RSI'] < 70)) 
    & (data['MACD'] < data['MACD signal'])
    ]
print('data_1321',data_1321.shape)

##################################################### 2 x x x####################################3



# 2 0 2 0
data_2020 = data.loc[((data['ema200'] > data['ema50']) & (data['ema50'] > data['ema20']))
    & (data['upper_band'] < data['Close'])
    & ((data['RSI'] > 30) & (data['RSI'] < 70)) 
    & (data['MACD'] > data['MACD signal'])
    ]
print('data_2020',data_2020.shape)

# 2 3 0 0
data_2300 = data.loc[((data['ema200'] > data['ema50']) & (data['ema50'] > data['ema20']))
    & (data['lower_band'] < data['Close'])
    & (data['RSI'] > 70) 
    & (data['MACD'] > data['MACD signal'])
    ]
print('data_2300',data_2300.shape)



# 2 3 1 0
data_2310 = data.loc[((data['ema200'] > data['ema50']) & (data['ema50'] > data['ema20']))
    & (data['lower_band'] < data['Close'])
    & (data['RSI'] < 30)  
    & (data['MACD'] > data['MACD signal'])
    ]
print('data_2310',data_2310.shape)

# 2 3 1 1
data_2311 = data.loc[((data['ema200'] > data['ema50']) & (data['ema50'] > data['ema20']))
    & (data['lower_band'] < data['Close'])
    & (data['RSI'] < 30)  
    & (data['MACD'] < data['MACD signal'])
    ]
print('data_2311',data_2311.shape)

# 2 3 2 0
data_2320 = data.loc[((data['ema200'] > data['ema50']) & (data['ema50'] > data['ema20']))
    & (data['lower_band'] < data['Close'])
    & ((data['RSI'] > 30) & (data['RSI'] < 70))
    & (data['MACD'] > data['MACD signal'])
    ]
print('data_2320',data_2320.shape)

# 2 3 2 1
data_2321 = data.loc[((data['ema200'] > data['ema50']) & (data['ema50'] > data['ema20']))
    & (data['lower_band'] < data['Close'])
    & ((data['RSI'] > 30) & (data['RSI'] < 70)) 
    & (data['MACD'] < data['MACD signal'])
    ]
print('data_2321',data_2321.shape)


# 3 3 0 0
data_3300 = data.loc[((data['ema20'] > data['ema200']) & (data['ema200'] > data['ema50'])) 
    & (data['lower_band'] < data['Close'])
    & (data['RSI'] > 70) 
    & (data['MACD'] > data['MACD signal'])
    ]
print('data_3300',data_3300.shape)


# 3 3 2 0
data_3320 = data.loc[((data['ema20'] > data['ema200']) & (data['ema200'] > data['ema50'])) 
    & (data['lower_band'] < data['Close'])
    & ((data['RSI'] > 30) & (data['RSI'] < 70))
    & (data['MACD'] > data['MACD signal'])
    ]
print('data_3320',data_3320.shape)

# 3 3 2 1
data_3321 = data.loc[((data['ema20'] > data['ema200']) & (data['ema200'] > data['ema50'])) 
    & (data['lower_band'] < data['Close'])
    & ((data['RSI'] > 30) & (data['RSI'] < 70)) 
    & (data['MACD'] < data['MACD signal'])
    ]
print('data_3321',data_3321.shape)


# 4 3 0 0
data_4300 = data.loc[((data['ema200'] > data['ema20']) & (data['ema20'] > data['ema50'])) 
    & (data['lower_band'] < data['Close'])
    & (data['RSI'] > 70) 
    & (data['MACD'] > data['MACD signal'])
    ]
print('data_4300',data_4300.shape)


# 4 3 2 0
data_4320 = data.loc[((data['ema200'] > data['ema20']) & (data['ema20'] > data['ema50']))
    & (data['lower_band'] < data['Close'])
    & ((data['RSI'] > 30) & (data['RSI'] < 70))
    & (data['MACD'] > data['MACD signal'])
    ]
print('data_4320',data_4320.shape)

# 4 3 2 1
data_4321 = data.loc[((data['ema200'] > data['ema20']) & (data['ema20'] > data['ema50'])) 
    & (data['lower_band'] < data['Close'])
    & ((data['RSI'] > 30) & (data['RSI'] < 70)) 
    & (data['MACD'] < data['MACD signal'])
    ]
print('data_4321',data_4321.shape)

# 5 3 1 1
data_5311 = data.loc[((data['ema50'] > data['ema200']) & (data['ema200'] > data['ema20'])) 
    & (data['lower_band'] < data['Close'])
    & (data['RSI'] < 30)  
    & (data['MACD'] < data['MACD signal'])
    ]
print('data_5311',data_5311.shape)

# 5 3 2 0
data_5320 = data.loc[((data['ema50'] > data['ema200']) & (data['ema200'] > data['ema20'])) 
    & (data['lower_band'] < data['Close'])
    & ((data['RSI'] > 30) & (data['RSI'] < 70))
    & (data['MACD'] > data['MACD signal'])
    ]
print('data_5320',data_5320.shape)

"""## chi_squred and linear regression

### data_0300
"""

data_0300 = data_0300.dropna(axis=1)
data_0300[data_0300 < 0] = 0

X = data_0300.iloc[:,1:129]  #independent variable columns
y = data_0300['Close']   #target variable column (price range)
 
#extracting top 10 best features by applying SelectKBest class
bestfeatures = SelectKBest(score_func=chi2, k=10)
label_encoder = preprocessing.LabelEncoder()
y = label_encoder.fit_transform(y)
fit = bestfeatures.fit(X,y)
dfscores = pandas.DataFrame(fit.scores_)
dfcolumns = pandas.DataFrame(X.columns)
 
#concat two dataframes
featureScores = pandas.concat([dfcolumns,dfscores],axis=1)
featureScores.columns = ['Specs','Score']  #naming the dataframe columns
print(featureScores.nlargest(15,'Score'))  #printing 19 best features

X = data_0300[['DiffLast','DiffMean','CapAct1yrUSD','SplyMiner1HopAllUSD','SplyMiner0HopAllUSD','Open']]
y = data_0300[['Close']]

X_train, X_test, y_train, y_test = train_test_split(X, y,
                                   test_size = 0.2,
                                   random_state = 0)
linear_model = LinearRegression()
linear_model.fit(X_train, y_train)
prediction = linear_model.predict(X_test)
print( 'MAPE:', MAPE(prediction, y_test) )
print(r2_score(y_test, prediction))
prediction_series = pandas.DataFrame(prediction, index = y_test.index, columns=['prediction'])
y_test['prediction'] = prediction_series['prediction']
y_test.plot(figsize=(20,10))

"""### data_1311 """

data_1311 = data_1311.dropna(axis=1)
data_1311[data_1311 < 0] = 0

X = data_1311.iloc[:,1:129]  #independent variable columns
y = data_1311['Close']   #target variable column (price range)
 
#extracting top 10 best features by applying SelectKBest class
bestfeatures = SelectKBest(score_func=chi2, k=10)
label_encoder = preprocessing.LabelEncoder()
y = label_encoder.fit_transform(y)
fit = bestfeatures.fit(X,y)
dfscores = pandas.DataFrame(fit.scores_)
dfcolumns = pandas.DataFrame(X.columns)
 
#concat two dataframes
featureScores = pandas.concat([dfcolumns,dfscores],axis=1)
featureScores.columns = ['Specs','Score']  #naming the dataframe columns
print(featureScores.nlargest(15,'Score'))  #printing 19 best features

X = data_1311[['DiffLast','DiffMean','CapAct1yrUSD','SplyMiner1HopAllUSD','SplyMiner0HopAllUSD','Open']]
y = data_1311[['Close']]

X_train, X_test, y_train, y_test = train_test_split(X, y,
                                   test_size = 0.2,
                                   random_state = 0)
linear_model = LinearRegression()
linear_model.fit(X_train, y_train)
prediction = linear_model.predict(X_test)
print( 'MAPE:', MAPE(prediction, y_test) )
print(r2_score(y_test, prediction))
prediction_series = pandas.DataFrame(prediction, index = y_test.index, columns=['prediction'])
y_test['prediction'] = prediction_series['prediction']
y_test.plot(figsize=(20,10))

X_test.info()

y_test.info()

"""# C. Test other regression model

## polynomical regression
"""

from sklearn.preprocessing import PolynomialFeatures

X = data22[['DiffLast','DiffMean','CapAct1yrUSD','SplyMiner1HopAllUSD','SplyMiner0HopAllUSD','Open']]
y = data22[['Close']]

X_train, X_test, y_train, y_test = train_test_split(X, y,
                                   test_size = 0.2,
                                   random_state = 0)

polynomial = PolynomialFeatures(degree = 3)
X_polynomial = polynomial.fit_transform(X_train)
model = LinearRegression()
model.fit(X_polynomial, y_train)
predictions_poly = model.predict(polynomial.transform(X_test))
print('r2_polynomial_score:', r2_score(y_test, predictions_poly))
print('MAPE_polynomial:',MAPE(predictions_poly, y_test))

"""## x"""

