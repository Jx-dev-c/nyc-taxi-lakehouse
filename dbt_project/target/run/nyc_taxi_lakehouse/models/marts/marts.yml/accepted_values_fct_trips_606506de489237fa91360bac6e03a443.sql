
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

with all_values as (

    select
        distance_bucket as value_field,
        count(*) as n_records

    from "nyc_taxi"."main_marts"."fct_trips"
    group by distance_bucket

)

select *
from all_values
where value_field not in (
    'short','medium','long','very_long'
)



  
  
      
    ) dbt_internal_test