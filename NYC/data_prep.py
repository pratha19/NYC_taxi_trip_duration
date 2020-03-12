# Function for preparing the data
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pandas.tseries.holiday import USFederalHolidayCalendar as calendar
import io
import requests
import json
from lxml import html
import math
"""
This module contains user defined functions for importing and cleaning the data and also for adding new features.
"""

def extract_url(raw_url, query, months, limit):
    """
    This function takes the raw_url, query (SQL), months and limit to define the html query to request data from the city of 
    new york's site.
    """
    url_content = []
    for month in months:
        url = raw_url+query+" AND date_extract_m(tpep_pickup_datetime) = "+str(month)+" LIMIT "+str(limit)
        r = requests.get(url)  #total rows = 131165043
        url_content.append(r.content)
    return url_content

def generate_df(raw_url, query, months, limit = 100, date_cols = ['tpep_pickup_datetime', 'tpep_dropoff_datetime'], 
                cols_to_use = 'default'):
    
    """
    This function creates the raw dataframe by extracting 'limit' number of rides randomly from each month in months and outputs
    a single dataframe with the NYC rides data.
    raw_url: the base URL where the data resides
    query: the SQL type query to append to the raw_url
    limit: the number of rides that should be extracted randomly from each month. Note: the Socrata API ensures that the limit is 
           executed randomly. Check https://dev.socrata.com/foundry/data.cityofnewyork.us/uacg-pexx for more details.
    date_cols: list of datetime columns
    cols_to_use: only these columns will be imported from the combined URL
    """
    
    if cols_to_use == 'default':
        cols = ['vendorid', 'tpep_pickup_datetime', 'tpep_dropoff_datetime',
               'passenger_count', 'trip_distance', 'pickup_longitude',
               'pickup_latitude', 'store_and_fwd_flag',
               'dropoff_longitude', 'dropoff_latitude', 'pulocationid', 'dolocationid']
    else:
        cols = cols_to_use
        
    df_dict = {}
    url_content = extract_url(raw_url, query, months, limit = limit)
    for i,j in enumerate(url_content):
        df_dict['month_'+str(i+1)] = pd.read_csv(io.StringIO(url_content[i].decode('utf-8')), 
                usecols = cols, parse_dates = date_cols)
    df = pd.concat(df_dict, axis='rows', ignore_index=True)
    df = df.rename(columns={'tpep_pickup_datetime': "pickup_datetime", 
                                          'tpep_dropoff_datetime': "dropoff_datetime"})
    return df

def haversine(coord1, coord2):
    """
    Calculates the haversine distance between pairs of (lat, lon) points using the haversine distance formula
    Refer to https://janakiev.com/blog/gps-points-distance-python/.
    For more accurate distance we should use the geopy.geodesic distance which calculates the shortest distance between two 
    points on the earth's surface taking into account the ellipsoid nature of the earth's shape. But the geopy.geodesic calculations
    take time and for a small area like NYC where maximum of the taxi trip durations are below 30 miles we can use the haversine
    function to save considerable amount of time and not lose much of the accuracy. I compared the values from both the functions
    and 99.8% of the times the difference in those values is less than 0.37 miles. So, using haversine here.
    
    If you want to use the more accurate geopy.geodesic function then simply import the function as, 
    -- from geopy.distance import geodesic
    and use it in the prepare_dataframe function below instead of the haversine function.
    """
    R = 6372800  # Earth radius in meters
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    
    phi1, phi2 = math.radians(lat1), math.radians(lat2) 
    dphi       = math.radians(lat2 - lat1)
    dlambda    = math.radians(lon2 - lon1)
    
    a = math.sin(dphi/2)**2 + \
        math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    # returning distance in miles (so converting meters to miles)
    return 0.000621371*2*R*math.atan2(math.sqrt(a), math.sqrt(1 - a))

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
    
    # Check for NULL values
    if df.isnull().sum().sum() !=0:
        print("There are NULL values in the dataset. You'll have take of the null values separately, this function doesn't deal \
              with Null value")
    # Adding extra datetime columns 
    df['pickup_date'] = pd.to_datetime(df.pickup_datetime.dt.date)
    df['pickup_month'] = df.pickup_datetime.dt.month
    df['pickup_day'] = df.pickup_datetime.dt.day  
    df['pickup_hour'] = df.pickup_datetime.dt.hour
    df['pickup_weekday'] = df.pickup_datetime.dt.weekday_name
    df["vendorid"] = df["vendorid"].astype('category')
    
    #cats = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    #cat_dtype = pd.api.types.CategoricalDtype(categories = cats, ordered=True)
    #df['pickup_weekday'] = df['pickup_weekday'].astype(cat_dtype)
    df['pickup_weekday'] = pd.Categorical(df['pickup_weekday'], 
                                           categories= ['Monday','Tuesday','Wednesday','Thursday',
                                                        'Friday','Saturday', 'Sunday'], ordered=True)   
    #Adding holidays column to indicate whether a day was a holiday as per the US calendar or not
    cal = calendar()
    holidays = cal.holidays(start =  df.pickup_datetime.dt.date.min(), end =  df.pickup_datetime.dt.date.max())
    df['holiday'] = 1*pd.to_datetime(df.pickup_datetime.dt.date).isin(holidays) 

    # ADD haversine distance
    df['distance_hav'] = df.apply(lambda x: haversine((x['pickup_latitude'], x['pickup_longitude']), 
                                   (x['dropoff_latitude'], x['dropoff_longitude'])), axis = 1)
    
    # REMOVING OUTLIERS
    
    # Since passenger count cannot be 0, assume the most common value (which is 1 for the NYC taxi dataset)
    df.loc[df.passenger_count == 0, 'passenger_count'] = df.passenger_count.value_counts().idxmax()
    df = df[(df.trip_duration > 60) & (df.trip_duration <= np.percentile(df.trip_duration, 99.8))
                   & (df.pickup_longitude.between(nyc_long_limits[0], nyc_long_limits[1]))
                   & (df.dropoff_longitude.between(nyc_long_limits[0], nyc_long_limits[1]))
                   & (df.pickup_latitude.between(nyc_lat_limits[0], nyc_lat_limits[1]))
                   & (df.dropoff_latitude.between(nyc_lat_limits[0], nyc_lat_limits[1]))
                   & (df.distance_hav > 0)
                   & (df.distance_hav <= np.percentile(df.distance_hav, 99.8))]
    
    return(df)

def bearing(coordinates):
    """
    This function calculates the direction of the trip from the pickup point towards the dropoff point. 
    Input:
    coordinates: the coordinates in a list such as [pickup_lat, pickup_lon, dropoff_lat, dropoff_lon]
    Output:
    compass_bearing: the radial direction such that N is 0, E is 90, S is 180 and N after a complete circle is 360. 
    """
    lat_p = np.radians(coordinates[0])
    lat_d = np.radians(coordinates[2])
    
    long_diff = np.radians(coordinates[1] - coordinates[3])
    x = np.sin(long_diff) * np.cos(lat_d)
    y = np.cos(lat_p) * np.sin(lat_d) - (np.sin(lat_p)* np.cos(lat_d) * np.cos(long_diff))

    initial_bearing = np.arctan2(x, y)
    initial_bearing = np.degrees(initial_bearing)
    compass_bearing = (-initial_bearing - 360)%360
    
    return compass_bearing
    