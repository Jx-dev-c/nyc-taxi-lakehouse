
  
    
    

    create  table
      "nyc_taxi"."main_marts"."mart_daily_summary__dbt_tmp"
  
    as (
      -- models/marts/mart_daily_summary.sql
-- -------------------------------------
-- Mart analítico: agrega corridas por dia.
-- Alimenta dashboards e queries de tendência temporal.
--
-- Decisão: mart separado da fct_trips evita que queries de dashboard
-- façam full scan na fact table a cada execução.
-- Trade-off: dado duplicado vs performance de leitura.

with trips as (

    select * from "nyc_taxi"."main_marts"."fct_trips"

),

daily as (

    select
        pickup_date,

        -- volume
        count(*)                                    as total_trips,
        sum(passenger_count)                        as total_passengers,

        -- distância
        round(sum(trip_distance), 2)                as total_distance_miles,
        round(avg(trip_distance), 2)                as avg_distance_miles,

        -- duração
        round(avg(trip_duration_minutes), 2)        as avg_duration_minutes,

        -- financeiro
        round(sum(total_amount), 2)                 as total_revenue,
        round(avg(total_amount), 2)                 as avg_fare,
        round(sum(tip_amount), 2)                   as total_tips,
        round(avg(tip_percentage), 2)               as avg_tip_percentage,

        -- pagamento
        count(*) filter (where payment_type = 'credit_card')    as trips_credit_card,
        count(*) filter (where payment_type = 'cash')           as trips_cash,

        -- período do dia
        count(*) filter (where time_of_day = 'morning')         as trips_morning,
        count(*) filter (where time_of_day = 'afternoon')       as trips_afternoon,
        count(*) filter (where time_of_day = 'evening')         as trips_evening,
        count(*) filter (where time_of_day = 'late_night')      as trips_late_night

    from trips
    group by pickup_date

)

select * from daily
order by pickup_date
    );
  
  