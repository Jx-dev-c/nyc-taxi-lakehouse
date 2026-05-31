
  
  create view "nyc_taxi"."main_intermediate"."int_trips_enriched__dbt_tmp" as (
    -- models/intermediate/int_trips_enriched.sql
-- -------------------------------------------
-- Intermediate: aplica dimensões de negócio e enriquece o staging.
-- Aqui entram as primeiras interpretações: categorização de horário,
-- tipo de pagamento legível, faixas de distância.
--
-- Decisão: manter intermediate como view evita duplicação de dado
-- e permite que os marts leiam sempre o estado mais recente.

with trips as (

    select * from "nyc_taxi"."main_staging"."stg_yellow_trips"

),

enriched as (

    select
        *,

        -- Categorização de período do dia (regra de negócio explícita)
        case
            when pickup_hour between 6  and 11 then 'morning'
            when pickup_hour between 12 and 17 then 'afternoon'
            when pickup_hour between 18 and 22 then 'evening'
            else 'late_night'
        end as time_of_day,

        -- Tipo de pagamento legível
        case payment_type_id
            when 1 then 'credit_card'
            when 2 then 'cash'
            when 3 then 'no_charge'
            when 4 then 'dispute'
            when 5 then 'unknown'
            when 6 then 'voided_trip'
            else 'other'
        end as payment_type,

        -- Faixa de distância
        case
            when trip_distance < 1    then 'short'
            when trip_distance < 5    then 'medium'
            when trip_distance < 15   then 'long'
            else 'very_long'
        end as distance_bucket,

        -- Flag de gorjeta (relevante para análise de comportamento)
        case when tip_amount > 0 then true else false end as has_tip,

        -- Percentual de gorjeta sobre o valor da corrida
        case
            when fare_amount > 0
            then round(tip_amount / fare_amount * 100, 2)
            else 0
        end as tip_percentage

    from trips

)

select * from enriched
  );
