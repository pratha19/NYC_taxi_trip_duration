# Function for preparing the data
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pandas.tseries.holiday import USFederalHolidayCalendar as calendar


def prepare_dataframe(raw_df = None, nyc_long_limits = (-74.257159, -73.699215), nyc_lat_limits = (40.471021, 40.987326)):

    # Verifying the correct pickup and dropoff datetime columns
    if 'pickup_datetime' and 'dropoff_datetime' not in raw_df:
        raw_df = raw_df.rename(columns={'tpep_pickup_datetime': "pickup_datetime", 
                                          'tpep_dropoff_datetime': "dropoff_datetime"})
     
    # Calculating the y variable which is trip duration in seconds
    if 'trip_duration' not in raw_df:
        raw_df['trip_duration'] = (raw_df['dropoff_datetime'] - raw_df['pickup_datetime'])/np.timedelta64(1,'s')
        
    cols = ['vendorid', 'pickup_datetime', 'dropoff_datetime',
       'passenger_count', 'pickup_longitude', 'pickup_latitude', 'store_and_fwd_flag',
       'dropoff_longitude', 'dropoff_latitude', 'trip_duration']
    
    df = raw_df[cols]
    
    # Adding extra datetime columns 
    df['pickup_date'] = df.pickup_datetime.dt.date
    df['pickup_month'] = df.pickup_datetime.dt.month
    df['pickup_day'] = df.pickup_datetime.dt.day
    df['pickup_hour'] = df.pickup_datetime.dt.hour
    df['pickup_weekday'] = df.pickup_datetime.dt.weekday_name
    
    cats = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    cat_dtype = pd.api.types.CategoricalDtype(categories = cats, ordered=True)
    df['pickup_weekday'] = df['pickup_weekday'].astype(cat_dtype)
        
    #Adding holidays column to indicate whether a day was a holiday as per the US calendar or not
    cal = calendar()
    holidays = cal.holidays(start =  df.pickup_datetime.dt.date.min(), end =  df.pickup_datetime.dt.date.max())
    df['holiday'] = 1*df.pickup_datetime.dt.date.isin(holidays)

    # ADD VINDISTANCE
    

    # REMOVE OUTLIERS
    # Removing outliers
    df = df[(df.trip_duration > 60) & (df.trip_duration <= np.percentile(df.trip_duration, 99.8))
                   & (df.pickup_longitude.between(nyc_long_limits[0], nyc_long_limits[1]))
                   & (df.dropoff_longitude.between(nyc_long_limits[0], nyc_long_limits[1]))
                   & (df.pickup_latitude.between(nyc_lat_limits[0], nyc_lat_limits[1]))
                   & (df.dropoff_latitude.between(nyc_lat_limits[0], nyc_lat_limits[1]))]
    ####           & (df.vindistance > some amount and less than 99.8% of the vindistnace stats
    
    return(df)
    
    