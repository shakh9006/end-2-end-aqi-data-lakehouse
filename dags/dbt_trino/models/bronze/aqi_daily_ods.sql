{{
    config(
        materialized='table',
        schema='bronze',
        database='nessie',
        tags=['bronze'],
    )
}}

select
    aqi,
    co,
    no2,
    o3,
    pm10,
    pm25,
    so2,
    slug,
    timestamp as aqi_date,
from {{ source('bronze', 'aqi_daily') }}