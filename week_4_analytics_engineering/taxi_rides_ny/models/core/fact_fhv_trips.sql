{{ config(materialized='table') }}

select
    trips.index,
    trips.dispatching_base_num,
    pickup_zone.borough as pickup_borough,
    pickup_zone.zone as pickup_zone,
    dropoff_zone.borough as dropoff_borough,
    dropoff_zone.zone as dropoff_zone,
    trips.pickup_datetime,
    trips.dropoff_datetime,
    trips.SR_Flag,
    trips.Affiliated_base_number
from {{ ref('stg_fhv_tripdata') }} as trips
inner join dim_zones as pickup_zone
on trips_unioned.pickup_locationid = pickup_zone.locationid
inner join dim_zones as dropoff_zone
on trips_unioned.dropoff_locationid = dropoff_zone.locationid