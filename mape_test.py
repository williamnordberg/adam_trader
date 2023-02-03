def mean_absolute_percentage_error(y_true, y_pred):
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    return np.mean(np.abs((y_true - y_pred) / y_true)) * 100


def seven_regression(data_to_regression):
    X = data_to_regression[['DiffLast', 'DiffMean', 'CapAct1yrUSD', 'HashRate', 'Open']]
    y = data_to_regression[['Close']]
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
    print('MAPE_forest:', mean_absolute_percentage_error(y_test, predictions_tree))

    # 6.ADA booster
    import math
    training_amount = 0.8
    ROWS = data.shape[0]
    index = math.floor(ROWS * training_amount)
    train_x = data[['DiffLast', 'DiffMean', 'CapAct1yrUSD', 'HashRate', 'Open']][:index].to_numpy()
    train_y = data['Close'][:index]

    test_x = data[['DiffLast', 'DiffMean', 'CapAct1yrUSD', 'HashRate', 'Open']][index:].to_numpy()
    test_y = data['Close'][index:]
    from sklearn.ensemble import AdaBoostRegressor
    model = AdaBoostRegressor()
    model.fit(train_x, train_y)
    predictions_ADA = model.predict(test_x)
    prediction_series = pd.Series(predictions_ADA, index=test_y.index)
    ADA_score = r2_score(test_y, predictions_ADA)
    print('MAPE_ADA:', mean_absolute_percentage_error(test_y, predictions_ADA))

    # 7. XGBoost

    # Train XGBoost model
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


x = 2015
for n in [data, data16, data17, data18, data19, data20, data21, data22]:
    seven_regression(n)
    x += 1
    print('\n', '***************', x, '***************', '\n')