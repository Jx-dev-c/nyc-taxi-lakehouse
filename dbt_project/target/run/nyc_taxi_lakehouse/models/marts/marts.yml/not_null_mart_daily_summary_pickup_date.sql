
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select pickup_date
from "nyc_taxi"."main_marts"."mart_daily_summary"
where pickup_date is null



  
  
      
    ) dbt_internal_test