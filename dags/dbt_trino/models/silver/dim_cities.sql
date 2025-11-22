{{
    config(
        materialized='table',
        schema='silver',
        database='iceberg',
        tags=['silver', 'dim_cities'],
    )
}}

with cities as (
    select
        row_number() over (order by city) as city_id,
        city as city_name,
        country,
        population as city_population,
        slug as city_slug
    from {{ ref('cities_ods')}}
)
select * from cities