{{
    config(
        materialized='table',
        schema='gold',
        database='iceberg',
        tags=['gold'],
    )
}}

with source as (
   select
    row_number() over (order by a.aqi desc) as rank,
    c.city_name as city,
    c.country,
    a.aqi,
    a.pm25,
    a.pm10,
    a.aqi_date as local_time
from {{ ref('fact_aqi_daily') }} as a
left join {{ ref('dim_cities') }} as c on a.city_id = c.city_id
where a.aqi is not null
order by a.aqi desc
)
select * from source