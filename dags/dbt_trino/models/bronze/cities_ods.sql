{{
    config(
        materialized='table',
        schema='bronze',
        database='nessie',
        tags=['bronze'],
    )
}}

select 
    city,
    country,
    population,
    slug
from {{ source('bronze', 'cities') }}