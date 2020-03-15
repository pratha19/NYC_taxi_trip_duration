# here we'll write all the functions to be used in the NYC_ML notebook including the error metric calculations, data preprocessing, ML model fitting and testing. 

import pandas as pd
import numpy as np
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error, mean_squared_log_error
import matplotlib.pyplot as plt
plt.style.use('bmh')
plt.rcParams['figure.figsize'] = [10, 5]

def rmsle(y_pred, y_truth):
    """
    Defining function to calculate the root mean squared log error of the model. RMSLE penalizes underestimates more than overestimates.
    We use this metric when we don’t want large errors to be significantly more penalized than small ones, in those cases where the
    range of target value is large.
    y_pred: predicted values of y by the model
    y_truth: observed values of y
    """
    sum = 0.0
    assert len(y_pred) == len(y_truth), "Length of predicted and observed y array is not the same"
    for x in range(len(y_pred)):
        if y_pred[x]<0 or y_truth[x]<0: #check for negative values
            continue
        p = np.log(y_pred[x]+1)
        r = np.log(y_truth[x]+1)
        sum = sum + (p - r)**2
    return (sum/len(y_pred))**0.5

def error_metrics(y_pred, y_truth, dict_error, model_name = None, test = True):
    """
    Printing error metrics like RMSE (root mean square error), R2 score, 
    MAE (mean absolute error), MAPE (mean absolute % error) and . 
    
    y_pred: predicted values of y using the model model_name
    y_truth: observed values of y
    dict_error: Dictionary of error matrices to store the errors
    model_name: name of the model used for predictions
    test: if validating on test set, True; otherwise False for training set validation
    
    The function will print the RMSE, RMSLE, R2, MAE and MAPE error metrics for the model_name and also store the results along with 
    model_name in the dictionary dict_error so that we can compare all the models at the end.
    """
    if isinstance(y_pred, np.ndarray):
        y_pred = y_pred
    else:
        y_pred = y_pred.to_numpy()
        
    if isinstance(y_truth, np.ndarray):
        y_truth = y_truth
    else:
        y_truth = y_truth.to_numpy()
        
    print('\nError metrics for model {}'.format(model_name))
    
    RMSE = np.sqrt(mean_squared_error(y_truth, y_pred))
    print("RMSE or Root mean squared error: %.2f" % RMSE)
    
    RMSLE = rmsle(y_pred, y_truth)
    print("RMSLE or Root mean squared log error: %.2f" % RMSLE)
    
    # Explained variance score: 1 is perfect prediction
    R2 = r2_score(y_truth, y_pred)
    print('Variance score: %.2f' % R2 )

    MAE = mean_absolute_error(y_truth, y_pred)
    print('Mean Absolute Error: %.2f' % MAE)

    MAPE = (np.mean(np.abs((y_truth - y_pred) / y_truth)) * 100)
    print('Mean Absolute Percentage Error: %.2f %%' % MAPE)
    
    # Appending the error values along with the model_name to the dict
    if test:
        train_test = 'test'
    else:
        train_test = 'train'
    
    #df = pd.DataFrame({'model': model_name, 'RMSE':RMSE, 'R2':R2, 'MAE':MAE, 'MAPE':MAPE}, index=[0])
    name_error = ['model', 'train_test', 'RMSE', 'RMSLE', 'R2', 'MAE', 'MAPE']
    value_error = [model_name, train_test, RMSE, RMSLE, R2, MAE, MAPE]
    list_error = list(zip(name_error, value_error))
    
    for error in list_error:
        if error[0] in dict_error:
            # append the new number to the existing array at this slot
            dict_error[error[0]].append(error[1])
        else:
            # create a new array in this slot
            dict_error[error[0]] = [error[1]]
    #return(dict_error)
    
def plot_predvstrue_reg(pred, truth, model_name = None):
    """
    Plots the observed true values against the predicted values
    """
    print("\nPlotting Predicted vs Observed trip duration in seconds")
    fig, ax = plt.subplots(1,1, figsize=(8,8))
    _ = ax.scatter(truth, pred) 
    _ = plt.xlabel("Observed ")
    _ = plt.ylabel("Predicted ")
    _ = plt.title("Observed vs Predicted {}".format(model_name))
    #_ = plt.xlim(1000, 5000)
    #_ = plt.ylim(1000, 5000)
    #plotting 45 deg line to see how the prediction differs from the observed values
    x = np.linspace(*ax.get_xlim())
    _ = ax.plot(x, x)
    
# PLotting the residuals
def residual_plot(y_pred, y_truth):
    residuals = (y_truth - y_pred)
    print("\nPlotting Predicted vs Residuals")
    _ = plt.figure(figsize=(8,8))
    _ = plt.scatter(y_pred , residuals, alpha = 0.5) 
    _ = plt.xlabel("Model predictions")
    _ = plt.ylabel("Residuals")
    _ = plt.title("Predicted values versus Residuals")