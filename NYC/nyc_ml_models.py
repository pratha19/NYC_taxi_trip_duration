# here we'll write all the functions to be used in the NYC_ML notebook including the error metric calculations, data preprocessing, ML model fitting and testing. 

from nyc_ml_err_plots import *
from data_preprocess import *
import sklearn.preprocessing
from sklearn.linear_model import ElasticNet
from sklearn.ensemble import RandomForestRegressor
import xgboost as xgb
from sklearn.model_selection import RandomizedSearchCV, GridSearchCV
import time

def cv_optimize(model, parameters, X_train, y_train, n_folds = 3, scoring = 'r2'):
    """
    Cross validation. Function to hypertune the model "model" with the input parameter distribution using
    "parameters" on the training data.
    The output will be the best estimator whose average score on all folds will be best. 
    """
    reg = RandomizedSearchCV(estimator = model, param_distributions = parameters, 
                             cv = n_folds, scoring = scoring, random_state = 42, verbose = 2, n_jobs = -1)
    t0 = time.time()
    reg.fit(X_train, y_train)
    time_fit = time.time() - t0 
    print('\n\n\n=============================',type(model).__name__,'=================================\n')
    print("It takes %.3f seconds for tuning " % (time_fit))
    print("BEST PARAMS", reg.best_params_)
    best = reg.best_estimator_
    return best

def do_regression(model, parameters, df, dict_error, model_name = None, test_size = 0.3, add_zone_avg = False,
                  fourier = False):
          
    X_train, X_test, y_train, y_test = prep_train_test(df, test_size = test_size, fourier = fourier)
    
    model = cv_optimize(model, parameters, X_train, y_train)
    t0 = time.time()
    model = model.fit(X_train, y_train)
    time_fit = time.time() - t0 
    print("It takes %.3f seconds for fitting" % (time_fit))
    print("train score: ", model.score(X_train, y_train), " \ntest score: ", model.score(X_test, y_test) )
    error_metrics(model.predict(X_test), y_test,dict_error, model_name = model_name, test = True)
    #print("\nPlotting Predicted vs Observed trip duration in seconds")
    plot_predvstrue_reg(model.predict(X_test), y_test)
    #print("\nPlotting Predicted vs Residuals")
    residual_plot(model.predict(X_test), y_test)
    #print("\nPlotting feature importance")
    # checking the feature importance for the random forest model
    if type(model).__name__ == 'RandomForestRegressor':
        feat_imp = pd.DataFrame({'importance': model.feature_importances_})    
        feat_imp['feature'] = X_train.columns
        feat_imp.sort_values(by='importance', ascending=False, inplace=True)
        
        feat_imp.sort_values(by = 'importance', inplace=True)
        feat_imp = feat_imp.set_index('feature', drop=True)
        print("\nPlotting feature importance")
        _ = feat_imp.plot.barh(title = 'Random Forest feature importance', figsize = (12,7))
    elif type(model).__name__ == 'XGBRegressor':
        print("\nPlotting feature importance")
        xgb.plot_importance(model)
        plt.rcParams['figure.figsize'] = [15, 7]
        
    print("="*100)
    print("="*100)
    print("="*100)
    return model, X_train, y_train, X_test, y_test

