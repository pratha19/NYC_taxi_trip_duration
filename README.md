This project involves predicting the yellow taxi trip duration between any two locations X and Y within NYC. 

The project covers the following topics:
1. [EDA]()     
- Raw Data import    
- External data imports     
- Data cleaning    
- Visualizations
- Data wranging based on EDA observations
- Inferences  
- Preparing data attributes for modeling

2. [ML]()   
- Preparing data for modeling  
- Building and tuning ML models (Basic model to XGBoost)  
- Comparing the different models  
- Conclusion and future work  

This project is inspired by the [NYC taxi trip duration challenge](https://www.kaggle.com/c/nyc-taxi-trip-duration/overview) hosted on Kaggle. But instead of using the train and test data from Kaggle taxi data was queried directly from the city of NY's website. Only Yellow taxi trips were considered for this project. More information about different taxi options available in NYC can be found [here](https://www1.nyc.gov/site/tlc/vehicles/get-a-vehicle-license.page).

The motive of the project is to identify the main factors influencing the daily taxi trips of New Yorkers. The taxi trips data is taken from the NYC Taxi and Limousine Commission (TLC), and it includes pickup time, pickup and dropoff geo-coordinates, number of passengers, and several other variables. The taxi trips considered in this project are only for the year 2016 and only those trips will be considered whose exact pickup and dropoff geo-coordinates are available. 

Policy researchers at the TLC and NYC can use the project observations and ML models to observe changing trends in the industry and maked informed decisions regarding transporation planning within the city.
