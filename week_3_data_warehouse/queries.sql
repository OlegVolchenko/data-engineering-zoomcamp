--CREATE EXTERNAL TABLE
CREATE OR REPLACE EXTERNAL TABLE dwh_w3.export_2019 (
  index STRING,
  dispatching_base_num STRING,
  pickup_datetime DATETIME,
  dropOff_datetime DATETIME,
  PUlocationID STRING,
  DOlocationID STRING,
  SR_Flag STRING,
  Affiliated_base_number STRING
) OPTIONS (
    format = 'CSV',
    uris = ['gs://dwh_w3/data/dwh/*.csv.gz'],
    skip_leading_rows = 1);
--CREATE MATERIALIZED TABLE
CREATE OR REPLACE TABLE zoomcamp-olvol3.dwh_w3.export_2019_materialized AS
SELECT * FROM dwh_w3.export_2019
--- CREATE PARTITIONED TABLE
CREATE OR REPLACE TABLE
  dwh_w3.export_2019_partitioned
PARTITION BY
  DATETIME_TRUNC(pickup_datetime, DAY) AS
SELECT
 *
FROM
  zoomcamp-olvol3.dwh_w3.export_2019_materialized