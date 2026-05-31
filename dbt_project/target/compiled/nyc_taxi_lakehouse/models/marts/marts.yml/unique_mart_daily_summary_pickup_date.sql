
    
    

select
    pickup_date as unique_field,
    count(*) as n_records

from "nyc_taxi"."main_marts"."mart_daily_summary"
where pickup_date is not null
group by pickup_date
having count(*) > 1


