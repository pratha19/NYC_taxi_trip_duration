# here we'll write all the functions to be used in the NYC_ML notebook including the error metric calculations, data preprocessing, ML model fitting and testing. 

from nyc_ml_err_plots import *
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

def add_fourier_terms(df, week_k = 3, day_k = 3):
    """
    We add fourier terms to deal with the periodical terms like hour of the day, weekdays, months, etc. This function can be used to 
    deal with these terms especially in the linear regression scenarios. For example, if we pass the hours as 0 to 23, the linear
    regression won't know that 0th hour actually next to the 23rd hour. So, putting the hour values as sine and cosine functions
    makes them continuous.
    df: dataframe to add the fourier terms to 
    week_k: the number of Fourier terms the weekly period should have. Thus the model will be fit on 2*week_k terms \
            (1 term for sine and 1 for cosine)
    day_k:same as week_k but for daily periods
    """

    for k in range(1, week_k+1):
        
        # week has a period of 7
        df['week_sin'+str(k)] = np.sin(2 *k* np.pi * df.pickup_weekday/7)
        df['week_cos'+str(k)] = np.cos(2 *k* np.pi * df.pickup_weekday/7)


    for k in range(1, day_k+1):
        
        # day has period of 24
        df['hour_sin'+str(k)] = np.sin(2 *k* np.pi * df.pickup_hour/24)
        df['hour_cos'+str(k)] = np.cos(2 *k* np.pi * df.pickup_hour/24)
        
    #df = df.drop(['pickup_weekday', 'pickup_hour'], axis = 1)
    return df
    
def prep_train_test(raw_df, test_size = 0.3, fourier = False, scale = False):
    """
    Function to split the data into train and test sets. 
    raw_df: dataframe to split into train and test sets
    test_size: portion of the raw_df to be used for testing
    fourier: if true, the hour and weekday terms will be transformed into continuous variables using fouier transformation.
    """
    #df = raw_df[cols_to_use]
    df = raw_df.copy()
    #df['pickup_weekday'] = raw_df.pickup_datetime.dt.dayofweek
    if fourier:
        df = add_fourier_terms(df, week_k = 3, day_k = 3)
    
    X = df.drop(['trip_duration'], axis = 1)
    y = df.trip_duration
    X_train, X_test, y_train, y_test = train_test_split(X, 
                                                    y, test_size = test_size, 
                                                    random_state = 42)
    
    if fourier:
        X_train.drop(['pickup_weekday', 'pickup_hour'], axis = 1, inplace = True)
        X_test.drop(['pickup_weekday', 'pickup_hour'], axis = 1, inplace = True)
        
    if scale:
        scaler = StandardScaler()
        X_train = scaler.fit_transform(X_train)
        X_test = scaler.transform(X_test)

    
    return(X_train, X_test, y_train, y_test)