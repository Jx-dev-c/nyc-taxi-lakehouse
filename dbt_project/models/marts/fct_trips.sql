-- models/marts/fct_trips.sql
-- ---------------------------
-- Fact table: granularidade = 1 linha por corrida.
-- Materializada como table para performance de leitura.
--
-- Decisão de granularidade:
--     Cada linha representa uma corrida completa. Agregar aqui
--     (ex: por dia) aumentaria performance de queries simples mas
--     impossibilitaria análises ad-hoc de corrida individual.
--     Para dashboards agregados, criar marts específicos (ex: mart_daily).

with trips as (

    select * from {{ ref('int_trips_enriched') }}

)

select
    -- surrogate key (DuckDB não tem UUID nativo sem extensão, usamos rowid)
    row_number() over (order by pickup_at) as trip_id,

    -- timestamps
    pickup_at,
    dropoff_at,
    pickup_date,
    pickup_hour,
    time_of_day,

    -- location ids (foreign keys para dimensão de zona - NYC TLC Zone)
    pickup_location_id,
    dropoff_location_id,

    -- métricas da corrida
    passenger_count,
    trip_distance,
    trip_duration_minutes,
    distance_bucket,

    -- métricas financeiras
    fare_amount,
    tip_amount,
    tolls_amount,
    total_amount,
    tip_percentage,
    has_tip,

    -- dimensões degeneradas
    vendor_id,
    rate_code_id,
    payment_type,
    store_and_fwd_flag

from trips
