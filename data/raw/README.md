
File descriptions
nyc_2016_raw_sql.csv > Raw data. Contains around 4.2M trips within New York City (NYC) taken in 2016. 

-- The data includes the first 6 months of the year 2016 only because the exact pickup and dropoff  
   locations were available for the first 6 months only. It was pulled from the new york city's 
   website using a query. 


Data fields:

vendor_id - a code indicating the provider associated with the trip record

pickup_datetime - date and time when the meter was engaged

dropoff_datetime - date and time when the meter was disengaged

passenger_count - the number of passengers in the vehicle (driver entered value)

pickup_longitude - the longitude where the meter was engaged

pickup_latitude - the latitude where the meter was engaged

dropoff_longitude - the longitude where the meter was disengaged

dropoff_latitude - the latitude where the meter was disengaged

store_and_fwd_flag - This flag indicates whether the trip record was held in vehicle memory before  
                     sending to the vendor because the vehicle did not have a connection to the server   
					 - Y=store and forward; N=not a store and forward trip

trip_distance - distance of the trip recorded in miles (to be removed because this field won't be  
                available for unseen trips/test data)