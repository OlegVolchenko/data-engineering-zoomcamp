{{ config(materialized='view') }}

select
    cast(index as integer) as index,
    dispatching_base_num,
    cast(pulocationid as integer) as  pickup_locationid,
    cast(dolocationid as integer) as dropoff_locationid,

    -- timestamps
    cast(pickup_datetime as TIMESTAMP) as pickup_datetime,
    cast(dropOff_datetime as TIMESTAMP) as dropoff_datetime,
    SR_Flag,
    Affiliated_base_number

from {{ source('staging','fhv_tripdata_table') }}


-- dbt build --m <model.sql> --var 'is_test_run: false'
{% if var('is_test_run', default=false) %}

  limit 100

{% endif %}
