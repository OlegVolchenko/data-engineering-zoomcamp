--get number of trips made on 15th

 SELECT COUNT(*) FROM yellow_taxi_trips WHERE CAST(lpep_pickup_datetime AS DATE)!= '2019-01-15' AND CAST(lpe
 p_dropoff_datetime AS DATE) = '2019-01-15'


--get passenger count

SELECT passenger_count, COUNT(*) FROM yellow_taxi_trips WHERE CAST(lpep_pickup_datetime AS DATE) = '2019-01
 -01' AND passenger_count BETWEEN 2 AND 3 GROUP BY 1


--get max trip distance
SELECT * FROM yellow_taxi_trips ORDER BY trip_distance DESC LIMIT 3

--get max tip
SELECT * FROM (
SELECT
	"PULocationID",
	pup_zone,
	dro_zone,
	tip_amount
FROM PUBLIC.YELLOW_TAXI_TRIPS AS A
LEFT JOIN (SELECT "LocationID", "Zone" AS pup_zone FROM PUBLIC.ZONE_LOOKUP) AS B ON A."PULocationID" = B."LocationID"
LEFT JOIN (SELECT "LocationID", "Zone" AS dro_zone FROM PUBLIC.ZONE_LOOKUP) AS BC ON A."DOLocationID" = BC."LocationID") AS D
WHERE pup_zone = 'Astoria'
ORDER BY tip_amount DESC