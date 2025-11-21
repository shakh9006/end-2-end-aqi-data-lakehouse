{{
    config(
        materialized='table',
        schema='bronze',
        database='iceberg',
        tags=['bronze'],
    )
}}

select 
    city,
    country,
    population,
    slug
from {{ source('bronze', 'cities') }}