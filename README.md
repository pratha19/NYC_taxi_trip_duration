This project involves predicting the yellow taxi trip duration between any two locations X and Y within NYC. 

The project covers the following topics:
1. [EDA](https://nbviewer.jupyter.org/github/pratha19/NYC_taxi_trip_duration/blob/master/notebooks/NYC_EDA.ipynb)     
- Raw Data import    
- External data imports     
- Data cleaning    
- Visualizations
- Data wranging based on EDA observations
- Inferences  
- Preparing data attributes for modeling

2. [ML](https://nbviewer.jupyter.org/github/pratha19/NYC_taxi_trip_duration/blob/master/notebooks/NYC_ML.ipynb)   
- Preparing data for modeling  
- Building and tuning ML models
- Comparing different models  
- Conclusion and future work  

__Introduction:__
This project is inspired by the [NYC taxi trip duration challenge](https://www.kaggle.com/c/nyc-taxi-trip-duration/overview) hosted on Kaggle. But instead of using the train and test data from Kaggle taxi data was queried directly from the city of NY's website. Only Yellow taxi trips were considered for this project. More information about different taxi options available in NYC can be found [here](https://www1.nyc.gov/site/tlc/vehicles/get-a-vehicle-license.page).

The motive of the project is to identify the main factors influencing the daily taxi trips of New Yorkers. The taxi trips data is taken from the NYC Taxi and Limousine Commission (TLC), and it includes pickup time, pickup and dropoff geo-coordinates, number of passengers, and several other variables. The taxi trips considered in this project are only for the year 2016 and only those trips will be considered whose exact pickup and dropoff geo-coordinates are available. 

Policy researchers at the TLC and NYC can use the project observations and ML models to observe changing trends in the industry and make informed decisions regarding transportation planning within the city.

__File descriptions:__

-- data/raw_data/nyc_2016_raw_sql.csv. Contains around 4.2M trips within New York City (NYC) taken in 2016. 
NOTE: None of the data files were uploaded in this repo because of their large size but if you run the EDA notebook by cloning this repositories all the data files will be populated in the correct sub-folders.

-- The data includes the first 6 months of the year 2016 only because the exact pickup and dropoff
locations were available for the first 6 months only. It was pulled from the new york city's website using a query.

__Data fields:__

- vendor_id - a code indicating the provider associated with the trip record

- pickup_datetime - date and time when the meter was engaged

- dropoff_datetime - date and time when the meter was disengaged

- passenger_count - the number of passengers in the vehicle (driver entered value)

- pickup_longitude - the longitude where the meter was engaged

- pickup_latitude - the latitude where the meter was engaged

- dropoff_longitude - the longitude where the meter was disengaged

- dropoff_latitude - the latitude where the meter was disengaged

- store_and_fwd_flag - This flag indicates whether the trip record was held in vehicle memory before
sending to the vendor because the vehicle did not have a connection to the server
- Y=store and forward; N=not a store and forward trip

- trip_distance - distance of the trip recorded in miles (was removed because this field won't be
available for unseen trips/test data)

__RESULTS:__

Linear regression, Random Forest and XGboost were fit on the data. For training only a small sample (500,000) of the ~4.2M trips was used but the best model was tested on the entire dataset to verify that the training sample was selected randomly and represents the entire dataset indeed.  
* XGBoost with some hyperparameter tuning gave the best result of RMSLE = 0.32. 
Note: RMSLE (root mean squared log error) was used here as the determining metric because we didn’t want large errors to be significantly more penalized than smaller ones. RMSLE penalizes underestimates more than overestimates.
* The RMSE, R2 score, MAE and MAPE for the best XGboost model were 272.96, 0.82, 178.24 and 26.38 respectively. 
* The median trip duration for the original dataset (4M rows) and the sampled dataset used for modeling is ~664 seconds. We see from the error metrics that the percentage error in predicting the trip duration is 26.38%. That is, our model predicts the trip duration as 178.24 seconds more or less than the actual on an average. This is just 3 minutes and given a busy city like NYC that's a very good performance. And we have used only the variables that were readily available to us.
* If we further analyze the errors based on the trip duration bins then we observe that the shorter duration trips (0-5, 5-10, 10-20 and 20-40) are predicted very well within a margin of +-1.65 to +- 5 minutes max whereas the longer duration trips such as 40-60 and 60-100 are predicted with a greater error margin of +-8 to +-16 minutes. Given that the 97% of the data lies below the 40 minutes trip duration, our model is perfroming very well on the majority of hte dataset. We can check the longer duration trips further to find ways to improve their performance if desired as well.  

And, the most important variables other than the distance between the pickup and dropoff locations, are:  
•	hour of the day  
•	weekday  
•	pickup and dropoff lat lons  
•	bearing (trip direction)  
•	even the day of the month and pickup and dropoff zone clusters seem to have some importance in the predictions.  

__Residual plots using the XGBoost model:__  
Note: The negative values of the residuals are over predictions and positive values are the under predicted values (residuals in minutes).   
* As can be seen from below, the trip duration of taxi rides from-and-to all the important areas including the 5 boroughs (except Staten island) and the airports were predicted within -2 to +2 minutes error by the model.
![Test image 1](https://github.com/pratha19/NYC_taxi_trip_duration/blob/master/data/processed/pickup_resid_minutes.png)
![Test image 2](https://github.com/pratha19/NYC_taxi_trip_duration/blob/master/data/processed/dropoff_resid_minutes.png)
![Test image 3](https://github.com/pratha19/NYC_taxi_trip_duration/blob/master/data/processed/resid_plot.png)

