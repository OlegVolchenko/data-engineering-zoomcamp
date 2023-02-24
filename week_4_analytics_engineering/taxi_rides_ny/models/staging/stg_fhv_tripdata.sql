{{ config(materialized='view') }}

select
    cast(index as INT64) as index,
    dispatching_base_num,
    cast(CAST(pulocationid AS FLOAT64) as INT64) as  pickup_locationid,
    cast(CAST(dolocationid AS FLOAT64)as INT64) as dropoff_locationid,

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
