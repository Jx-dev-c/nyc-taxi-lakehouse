
    
    



select tpep_dropoff_datetime
from read_parquet('C:/Users/joaob/Downloads/nyc_taxi_lakehouse/data/trusted/yellow_tripdata_2023-01.parquet')
where tpep_dropoff_datetime is null


