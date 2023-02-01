import argparse
from pathlib import Path
import pandas as pd
from prefect import flow, task
from prefect_gcp.cloud_storage import GcsBucket
from prefect_gcp import GcpCredentials
from typing import List


@task(name='Extract from gcs', retries=3)
def extract_from_gcs(color: str, year: int, month: 1) -> Path:
    """Download data from gcs"""
    gcs_path = f'data/{color}/{color}_tripdata_{year}-{month:02}.parquet'
    gcs_block = GcsBucket.load("bootcamp-bucket-connection")
    gcs_block.get_directory(from_path=gcs_path, local_path=f"../data/")
    return Path(f"../data/{gcs_path}")


@task(name='Transform df', log_prints=True)
def transform(path: Path, color: str) -> pd.DataFrame:
    """Fix dtype issues"""
    df = pd.read_parquet(path)
    print(f'applying adjustment for {color} taxi data')
    if color == 'yellow':
        datetime_prefix = 'tpep'
    else:
        datetime_prefix = 'lpep'
    print(f"Columns dtypes : {datetime_prefix}_dropoff_datetime - {df[f'{datetime_prefix}_dropoff_datetime'].dtype}")
    df[f'{datetime_prefix}_dropoff_datetime'] = pd.to_datetime(df[f'{datetime_prefix}_dropoff_datetime'])
    df[f'{datetime_prefix}_pickup_datetime'] = pd.to_datetime(df[f'{datetime_prefix}_pickup_datetime'])
    print('transforming df, changing dtypes to datetime where needed')
    print(f"Columns dtypes after casting: {datetime_prefix}_dropoff_datetime - {df[f'{datetime_prefix}_dropoff_datetime'].dtype}")
    return df


@task(name='Load to bq', log_prints=True)
def load_to_bq(df: pd.DataFrame, color: str) -> None:
    """Load DataFrame to bq"""

    gcp_cred_block = GcpCredentials.load('bootcamp-gcp-account')
    df.to_gbq(
        destination_table=f'prefect_taxi_data.trips_{color}',
        project_id='zoomcamp-olvol3',
        credentials=gcp_cred_block.get_credentials_from_service_account(),
        chunksize=500000,
        if_exists='append'
    )
    print('DataFrame has been ingested to bq table ')


@flow(name='Ingest data to bg', log_prints=True)
def etl_gcs_to_bq(months: List[int], year: int, color: str,) -> None:
    """Main etl flow to load data into bq"""
    for month in months:
        path = extract_from_gcs(color, year, month)
        df = transform(path, color)
        load_to_bq(df, color)
        print(f"flow has processed {len(df)} rows of data for {year}, {month}")


if __name__ == '__main__':
    # Initialize parser
    parser = argparse.ArgumentParser()

    # Adding optional argument
    parser.add_argument("-m", "--Months", help="A list of months")
    parser.add_argument("-y", "--Year", help="A year")
    parser.add_argument("-c", "--Color", help="A taxi color")

    # Read arguments from command line
    args = parser.parse_args()

    etl_gcs_to_bq([2, 3], 2019, 'yellow')
