-- models/staging/stg_yellow_trips.sql
-- ------------------------------------
-- Staging: renomeia colunas para snake_case legível,
-- padroniza tipos e remove ambiguidade de nomenclatura.
--
-- Decisão: staging não filtra, não agrega, não aplica regra de negócio.
-- É uma camada de contrato entre a fonte e os modelos downstream.

with source as (

    select * from {{ source('trusted', 'yellow_tripdata_2023_01') }}

),

renamed as (

    select
        -- identifiers
        VendorID                    as vendor_id,
        RatecodeID                  as rate_code_id,
        PULocationID                as pickup_location_id,
        DOLocationID                as dropoff_location_id,
        payment_type                as payment_type_id,

        -- timestamps
        tpep_pickup_datetime        as pickup_at,
        tpep_dropoff_datetime       as dropoff_at,
        pickup_date,
        pickup_hour,

        -- métricas da corrida
        passenger_count,
        trip_distance,
        trip_duration_minutes,

        -- valores financeiros
        fare_amount,
        extra,
        mta_tax,
        tip_amount,
        tolls_amount,
        improvement_surcharge,
        total_amount,
        congestion_surcharge,
        airport_fee,

        -- flags
        store_and_fwd_flag

    from source

)

select * from renamed
