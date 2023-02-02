
# 4.regression tree
decision_model = DecisionTreeRegressor(random_state=0)
decision_model.fit(X_train, y_train)
predictions_tree = decision_model.predict(X_test).reshape(-1, 1)
print('\n MAPE_decision_tree:', mape(y_test, predictions_tree), )
