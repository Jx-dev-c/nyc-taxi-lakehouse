
    
    



select trip_duration_minutes
from read_parquet('C:/Users/joaob/Downloads/nyc_taxi_lakehouse/data/trusted/yellow_tripdata_2023-01.parquet')
where trip_duration_minutes is null


