{{ 
    config(
        materialized='table', 
        schema='silver', 
        database='iceberg',
    ) 
}}

with src as (
    select try(date_parse(aqi_date, '%Y-%m-%d %H:%i:%s')) as ts
    from {{ ref('aqi_daily_ods') }}
),
dates as (
    select
        row_number() over (order by ts) as date_id,
        cast(ts as date) as date_value,
        extract(year    from ts) as year,
        extract(quarter from ts) as quarter,
        extract(month   from ts) as month,
        extract(day     from ts) as day,
        extract(dow     from ts) as day_of_week
    from src
    where ts is not null
)
select * from dates