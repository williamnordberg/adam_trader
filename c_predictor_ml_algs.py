from sklearn.metrics import confusion_matrix
import numpy as np
from z_dataset_sql import load_dataset
import pandas as pd
from sklearn.model_selection import RandomizedSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report
from scipy.stats import randint
from sklearn.ensemble import AdaBoostClassifier, GradientBoostingClassifier
from skopt import BayesSearchCV
from skopt.space import Real, Integer
from imblearn.over_sampling import SMOTE
from sklearn.model_selection import GridSearchCV
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from catboost import CatBoostClassifier
from sklearn.svm import SVC
from sklearn.ensemble import VotingClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder
import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # 0 = all messages, 1 = info, 2 = warnings and errors, 3 = errors
from tensorflow.python.keras.utils.np_utils import to_categorical
from keras.layers import LSTM, Dense
from keras.models import Sequential

DATASET_PATH = 'data/dataset.db'
SPLIT_DATA_DATA = '2023-08-20'
TABLE_NAME = 'full_dataset'


def load_and_split_data(scale_data=False):
    df = load_dataset(DATASET_PATH, TABLE_NAME)
    df.set_index(df['Date'], inplace=True)

    split_date = pd.Timestamp(SPLIT_DATA_DATA)
    train = df.loc[df['Date'] < split_date]
    test = df.loc[df['Date'] >= split_date]

    # Drop the columns not used as features
    drop_columns = ['Unix', 'Date', 'High', 'Low', 'Close', 'Directional_movement',
                    'bitcoin_price', 'actual_price_12h_later', 'PPI', 'CPI']
    X_train = train.drop(drop_columns, axis=1)
    X_test = test.drop(drop_columns, axis=1)

    y_train = train['Directional_movement']
    y_test = test['Directional_movement']

    if scale_data:
        scaler = StandardScaler()
        X_train = scaler.fit_transform(X_train)
        X_test = scaler.transform(X_test)

    return X_train, y_train, X_test, y_test


def calculate_cost(y_true, y_pred, labels=None):
    if labels is None:
        labels = ['Up', 'Down', 'Neutral']

    # Calculate the confusion matrix
    cm = confusion_matrix(y_true, y_pred, labels=labels)

    # Define the cost matrix
    cost_matrix = np.array([[0, 2, 1],
                            [2, 0, 1],
                            [1, 1, 0]])

    # Calculate the total cost
    total_cost = np.sum(cm * cost_matrix)

    return total_cost


def rf(scaling=False, class_weight=True):
    X_train, y_train, X_test, y_test = load_and_split_data(scaling)

    if class_weight:
        total = len(y_train)
        class_weight = {
            'Up': total / sum(y_train == 'Up'),
            'Down': total / sum(y_train == 'Down'),
            'Neutral': total / sum(y_train == 'Neutral')
        }

    # Initialize the classifier
    clf = RandomForestClassifier(class_weight=class_weight)

    # Train the classifier
    clf.fit(X_train, y_train)

    # Make predictions
    y_pred = clf.predict(X_test)

    print(f"rf misclassification cost: {calculate_cost(y_test, y_pred) / len(y_test)}")
    print(classification_report(y_test, y_pred, zero_division=1))


def rf_feature_importance(class_weight=True):
    X_train, y_train, X_test, y_test = load_and_split_data(False)

    if class_weight:
        total = len(y_train)
        class_weight = {
            'Up': total / sum(y_train == 'Up'),
            'Down': total / sum(y_train == 'Down'),
            'Neutral': total / sum(y_train == 'Neutral')
        }

    # Initialize the classifier
    clf = RandomForestClassifier(class_weight=class_weight)

    # Train the classifier
    clf.fit(X_train, y_train)

    # Print feature importances
    feature_importances = clf.feature_importances_
    feature_names = X_train.columns
    feature_importance_dict = {name: importance for name, importance in zip(feature_names, feature_importances)}
    sorted_importances = {k: v for k, v in sorted(
        feature_importance_dict.items(), key=lambda item: item[1], reverse=True)}

    print("Feature importance:")
    print(sorted_importances)


def rf_random_search_optimization(scaling=True, class_weight=True):
    X_train, y_train, X_test, y_test = load_and_split_data(scaling)

    if class_weight:
        total = len(y_train)
        class_weight = {
            'Up': total / sum(y_train == 'Up'),
            'Down': total / sum(y_train == 'Down'),
            'Neutral': total / sum(y_train == 'Neutral')
        }

    # Hyperparameter grid
    param_dist = {
        'n_estimators': randint(10, 50),
        'max_depth': [6, 8, 10, 12, 15, 20, 25, 30],
        'max_features': ['sqrt', 'log2'],
        'class_weight': [class_weight]
    }

    # Initialize RandomizedSearchCV
    random_search = RandomizedSearchCV(
        RandomForestClassifier(), param_distributions=param_dist, n_iter=50, cv=3, n_jobs=-1)

    # Perform Randomized Search
    random_search.fit(X_train, y_train)

    # Fetch the best parameters
    best_params = random_search.best_params_
    print("Best Params random_search_optimization:", best_params)

    # Initialize the classifier with best_params
    clf = RandomForestClassifier(**best_params)

    clf.fit(X_train, y_train)
    y_pred = clf.predict(X_test)

    print(f"rf_random_search_optimization misclassification cost: {calculate_cost(y_test, y_pred) / len(y_test)}")
    print(classification_report(y_test, y_pred, zero_division=1))


def rf_gird_search_optimization(scaling=True, class_weight=True):
    X_train, y_train, X_test, y_test = load_and_split_data(scaling)

    if class_weight:
        total = len(y_train)
        class_weight = {
            'Up': total / sum(y_train == 'Up'),
            'Down': total / sum(y_train == 'Down'),
            'Neutral': total / sum(y_train == 'Neutral')
        }

    # Parameter grid for GridSearch
    param_grid = {
        'n_estimators': [10, 50, 100, 200],
        'max_depth': [None, 10, 20, 30],
        'max_features': ['sqrt', 'log2'],  # Removed 'auto'
        'class_weight': [class_weight]
    }

    # Initialize GridSearchCV
    grid_search = GridSearchCV(estimator=RandomForestClassifier(class_weight=class_weight), param_grid=param_grid, cv=5)
    grid_search.fit(X_train, y_train)
    best_params = grid_search.best_params_
    print('gird_search_optimization best_params', best_params)

    clf = RandomForestClassifier(**best_params)
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)

    print(f"rf_gird_search_optimization misclassification cost: {calculate_cost(y_test, y_pred) / len(y_test)}")
    print(classification_report(y_test, y_pred, zero_division=1))


def adaboost(scaling=True, n_estimators=50):
    X_train, y_train, X_test, y_test = load_and_split_data(scaling)

    # Initialize AdaBoost
    clf_ada = AdaBoostClassifier(n_estimators=n_estimators)

    # Train AdaBoost
    clf_ada.fit(X_train, y_train)

    # Make Predictions
    y_pred_ada = clf_ada.predict(X_test)

    print(f" adaboost misclassification cost: {calculate_cost(y_test, y_pred_ada) / len(y_test)}")
    print(classification_report(y_test, y_pred_ada, zero_division=1))


def adaboost_bayesian_optimization(scaling=True):
    X_train, y_train, X_test, y_test = load_and_split_data(scaling)

    # Specify the hyperparameter space
    param_space = {
        'n_estimators': Integer(10, 100),
        'learning_rate': Real(0.01, 1.0, 'log-uniform')
    }

    # Create a BayesSearchCV object
    opt = BayesSearchCV(
        AdaBoostClassifier(),
        param_space,
        n_iter=50,
        cv=3,
        n_jobs=-1
    )

    # Run the optimizer
    opt.fit(X_train, y_train)

    # Get the best parameters and score
    best_params = opt.best_params_
    print("Best Params:", best_params)

    # Initialize AdaBoost with best parameters
    clf_ada_best = AdaBoostClassifier(**best_params)

    # Fit and predict
    clf_ada_best.fit(X_train, y_train)
    y_pred_best = clf_ada_best.predict(X_test)

    print(f" adaboost_bayesian_opt misclassification cost: {calculate_cost(y_test, y_pred_best) / len(y_test)}")
    print(classification_report(y_test, y_pred_best, zero_division=1))


def adaboost_smooth(scaling=True, n_estimators=50, learning_rate=0.1):
    X_train, y_train, X_test, y_test = load_and_split_data(scaling)

    # Initialize SMOTE
    sm = SMOTE(random_state=42)

    # Fit and resample the imbalanced dataset
    X_train_res, y_train_res = sm.fit_resample(X_train, y_train)

    # Initialize and fit AdaBoost Classifier
    clf_ada = AdaBoostClassifier(n_estimators=n_estimators, learning_rate=learning_rate)
    clf_ada.fit(X_train_res, y_train_res)

    # Predict
    y_pred = clf_ada.predict(X_test)

    print(f"adaboost_smooth misclassification cost: {calculate_cost(y_test, y_pred) / len(y_test)}")
    print(classification_report(y_test, y_pred, zero_division=1))


def gb(scaling=True, n_estimators=50):
    X_train, y_train, X_test, y_test = load_and_split_data(scaling)

    # Initialize GradientBoosting
    clf_gb = GradientBoostingClassifier(n_estimators=n_estimators)

    # Train GradientBoosting
    clf_gb.fit(X_train, y_train)

    # Make Predictions
    y_pred_gb = clf_gb.predict(X_test)

    print(f" gb misclassification cost: {calculate_cost(y_test, y_pred_gb) / len(y_test)}")
    print(classification_report(y_test, y_pred_gb, zero_division=1))


def gb_smooth(scaling=True, n_estimators=50):
    X_train, y_train, X_test, y_test = load_and_split_data(scaling)

    # Initialize SMOTE
    sm = SMOTE(random_state=42)

    # Fit and resample the imbalanced dataset
    X_train_res, y_train_res = sm.fit_resample(X_train, y_train)

    # Initialize GradientBoosting
    clf_gb = GradientBoostingClassifier(n_estimators=n_estimators)

    # Train GradientBoosting
    clf_gb.fit(X_train_res, y_train_res)

    # Make Predictions
    y_pred_gb = clf_gb.predict(X_test)

    print(f"gb_smooth misclassification cost: {calculate_cost(y_test, y_pred_gb) / len(y_test)}")
    print(classification_report(y_test, y_pred_gb, zero_division=1))


def gb_bayesian_optimization(scaling=True):
    # Load your data
    X_train, y_train, X_test, y_test = load_and_split_data(scaling)

    # Initialize SMOTE
    sm = SMOTE(random_state=42)

    # Fit and resample the imbalanced dataset
    X_train_res, y_train_res = sm.fit_resample(X_train, y_train)

    # Reduced parameter grid
    param_grid = {
        'n_estimators': (50, 100),
        'learning_rate': [0.1, 0.2]
    }

    # Initialize BayesSearchCV with fewer iterations and folds
    bayes_search = BayesSearchCV(
        estimator=GradientBoostingClassifier(),
        search_spaces=param_grid,
        n_iter=10,
        cv=2,
        n_jobs=-1,  # Parallelization
        random_state=42
    )

    # Perform hyperparameter search
    bayes_search.fit(X_train_res, y_train_res)

    # Best params
    print("Best parameters found: ", bayes_search.best_params_)

    # Make predictions with best estimator
    y_pred = bayes_search.best_estimator_.predict(X_test)

    print(f"gb_bayesian_optimization misclassification cost: {calculate_cost(y_test, y_pred) / len(y_test)}")
    print(classification_report(y_test, y_pred, zero_division=1))


def xgboost_model(scaling=True, n_estimators=50):
    X_train, y_train, X_test, y_test = load_and_split_data(scaling)

    # Encode string labels into integers
    le = LabelEncoder()
    y_train = le.fit_transform(y_train)
    y_test = le.transform(y_test)

    clf_xgb = XGBClassifier(n_estimators=n_estimators)
    clf_xgb.fit(X_train, y_train)

    y_pred_xgb = clf_xgb.predict(X_test)

    # Transform predicted labels back to original strings for reporting
    y_pred_xgb = le.inverse_transform(y_pred_xgb)
    y_test = le.inverse_transform(y_test)

    print(f"XGBoost misclassification cost: {calculate_cost(y_test, y_pred_xgb) / len(y_test)}")
    print(classification_report(y_test, y_pred_xgb, zero_division=1))


def lightgbm_model(scaling=True, n_estimators=50):
    X_train, y_train, X_test, y_test = load_and_split_data(scaling)

    clf_lgbm = LGBMClassifier(n_estimators=n_estimators)
    clf_lgbm.fit(X_train, y_train)

    y_pred_lgbm = clf_lgbm.predict(X_test)

    print(f"LightGBM misclassification cost: {calculate_cost(y_test, y_pred_lgbm) / len(y_test)}")
    print(classification_report(y_test, y_pred_lgbm, zero_division=1))


def catboost_model(scaling=True, n_estimators=50):
    X_train, y_train, X_test, y_test = load_and_split_data(scaling)

    clf_cat = CatBoostClassifier(n_estimators=n_estimators, verbose=False)
    clf_cat.fit(X_train, y_train)

    y_pred_cat = clf_cat.predict(X_test)

    print(f"CatBoost misclassification cost: {calculate_cost(y_test, y_pred_cat) / len(y_test)}")
    print(classification_report(y_test, y_pred_cat, zero_division=1))


def lstm_model():
    X_train, y_train, X_test, y_test = load_and_split_data()

    # Reshape data
    X_train = np.reshape(X_train, (X_train.shape[0], 1, X_train.shape[1]))
    X_test = np.reshape(X_test, (X_test.shape[0], 1, X_test.shape[1]))

    # Label encoding
    le = LabelEncoder()
    y_train_encoded = le.fit_transform(y_train)

    # Convert to float32
    y_train_encoded = y_train_encoded.astype('float32')

    # One-hot encoding for y_train
    y_train_encoded = to_categorical(y_train_encoded, num_classes=3)

    # Create the LSTM model
    model = Sequential()
    model.add(LSTM(50, input_shape=(X_train.shape[1], X_train.shape[2])))
    model.add(Dense(3, activation='softmax'))
    model.compile(optimizer='adam', loss='categorical_crossentropy')

    # Fit the model
    model.fit(X_train, y_train_encoded, epochs=50, batch_size=72, verbose=1)

    # Predict
    pred = model.predict(X_test)
    pred_classes = np.argmax(pred, axis=1)

    # Label encode y_test using the same encoder
    y_test_encoded = le.transform(y_test)

    # Decode pred_classes and y_test_encoded back to original labels for comparison
    decoded_pred_classes = le.inverse_transform(pred_classes)
    decoded_y_test = le.inverse_transform(y_test_encoded)

    print(f"lstm_model misclassification cost: {calculate_cost(decoded_y_test, decoded_pred_classes) / len(y_test)}")
    print(classification_report(decoded_y_test, decoded_pred_classes, zero_division=1))


def svm_rbf():
    X_train, y_train, X_test, y_test = load_and_split_data()

    clf = SVC(kernel='rbf')
    clf.fit(X_train, y_train)
    y_pred = clf.predict(X_test)

    print(f"svm_rbf misclassification cost: {calculate_cost(y_test, y_pred) / len(y_test)}")
    print(classification_report(y_test, y_pred))


def svm_model():
    X_train, y_train, X_test, y_test = load_and_split_data()

    # Reshape data for SVM (if needed)
    X_train = np.reshape(X_train, (X_train.shape[0], -1))
    X_test = np.reshape(X_test, (X_test.shape[0], -1))

    # Label encoding
    le = LabelEncoder()
    y_train_encoded = le.fit_transform(y_train)
    y_test_encoded = le.transform(y_test)

    # Create the SVM model
    clf = SVC(kernel='rbf')
    clf.fit(X_train, y_train_encoded)

    # Predict
    pred = clf.predict(X_test)

    # Decode pred and y_test_encoded back to original labels for comparison
    decoded_pred = le.inverse_transform(pred)
    decoded_y_test = le.inverse_transform(y_test_encoded)

    print(f"SVM_model misclassification cost: {calculate_cost(decoded_y_test, decoded_pred) / len(y_test)}")
    print(classification_report(decoded_y_test, decoded_pred, zero_division=1))


def ensemble_model():
    X_train, y_train, X_test, y_test = load_and_split_data()

    model1 = LogisticRegression()
    model2 = DecisionTreeClassifier()
    ensemble = VotingClassifier(estimators=[('lr', model1), ('dt', model2)], voting='soft')

    ensemble.fit(X_train, y_train)

    y_pred = ensemble.predict(X_test)
    print(f"ensemble_model misclassification cost: {calculate_cost(y_test, y_pred) / len(y_test)}")
    print(classification_report(y_test, y_pred))


if __name__ == '__main__':
    rf_gird_search_optimization(True, True)
    rf_feature_importance(True)
    rf_random_search_optimization(True, True)
    adaboost(True, 50)
    adaboost_bayesian_optimization(True)
    adaboost_smooth(True)
    gb(True)
    gb_smooth(True)
    gb_bayesian_optimization(True)
    xgboost_model(True)
    lightgbm_model(True)
    catboost_model(True)
    lstm_model()
    svm_rbf()
    svm_model()
