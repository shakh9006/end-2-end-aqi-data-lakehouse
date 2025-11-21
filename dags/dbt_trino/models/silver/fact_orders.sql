{{
    config(
        materialized='incremental',
        schema='silver',
        database='nessie',
        tags=['silver', 'fact_orders'],
        unique_key='city_id || '-' || date_id'
    )
}}

with aqi as (
    select
        a.*,
        c.city_id,
        d.date_id
    from {{ ref('aqi_daily_ods')}} as a
    left join {{ ref('dim_cities')}} as c on a.slug = c.city_slug
    left join {{ ref('dim_dates')}} as d on a.aqi_date = d.date_value
)
select 
    row_number() over(order by city_id, aqi_date) as aqi_id,
    city_id,
    date_id,
    aqi,
    co,
    no2,
    o3,
    pm10,
    pm25,
    so2
from aqi
{% if is_incremental() %}
    where date_id > (select max(date_id) from {{ this }})
{% endif %}