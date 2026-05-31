
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select total_trips
from "nyc_taxi"."main_marts"."mart_daily_summary"
where total_trips is null



  
  
      
    ) dbt_internal_test