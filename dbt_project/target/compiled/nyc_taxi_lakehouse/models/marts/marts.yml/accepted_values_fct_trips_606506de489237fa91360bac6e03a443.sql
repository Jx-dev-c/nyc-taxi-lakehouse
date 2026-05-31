
    
    

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


