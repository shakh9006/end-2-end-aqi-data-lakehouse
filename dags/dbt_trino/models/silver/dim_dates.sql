{{
    config(
        materialized='incremental',
        schema='silver',
        database='nessie',
        tags=['silver', 'dim_dates'],
        unique_key='date_value || '-' || city_slug'
    )
}}

with dates as (
    select
        row_number() over (order by aqi_date) as date_id,
        aqi_date as date_value,
        extract(year    from aqi_date) as year,
        extract(quarter from aqi_date) as quarter,
        extract(month   from aqi_date) as month,
        extract(day     from aqi_date) as day,
        extract(dow     from aqi_date) as day_of_week,
    from {{ ref('aqi_daily_ods')}}
    group by aqi_date
)
select * from dates
{% if is_incremental() %}
    where date_value > (select max(date_value) from {{ this }})
{% endif %}