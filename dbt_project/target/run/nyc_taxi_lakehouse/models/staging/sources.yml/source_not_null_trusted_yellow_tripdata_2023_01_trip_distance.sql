
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select trip_distance
from read_parquet('C:/Users/joaob/Downloads/nyc_taxi_lakehouse/data/trusted/yellow_tripdata_2023-01.parquet')
where trip_distance is null



  
  
      
    ) dbt_internal_test