from pathlib import Path
import pandas as pd
from prefect import task, flow
from prefect_gcp.cloud_storage import GcsBucket
from prefect.tasks import task_input_hash
from datetime import timedelta

import os


@task(name='Get df', retries=3, cache_key_fn=task_input_hash, cache_expiration=timedelta(days=1), log_prints=True)
def get_data(dataset_url: str) -> pd.DataFrame:
    """Read static file from web"""
    df = pd.read_csv(dataset_url)
    print(f'csv has been extracted and loaded into a df, total amount of rows: {len(df)}')
    return df


@task(name='Transform df', log_prints=True)
def transform(df: pd.DataFrame, color: str) -> pd.DataFrame:
    """Fix dtype issues"""
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


@task(name='write result to local')
def write_local(df: pd.DataFrame, color: str, dataset_file) -> Path:
    """Writes DataFrame as parquet file"""
    if not os.path.isdir(f'data/{color}'):
        os.makedirs(f'data/{color}')
    path = Path(f'data/{color}/{dataset_file}.parquet')
    df.to_parquet(path, compression='gzip')
    return path


@task(name='Write result to gcs')
def write_gcs(path: Path) -> None:
    """Upload parquet file to gcs"""
    gcp_cloud_storage_bucket_block = GcsBucket.load("bootcamp-bucket-connection")
    gcp_cloud_storage_bucket_block.upload_from_path(from_path=path, to_path=path)


@flow(name='Flat file to gcs', log_prints=True)
def etl_web_to_gcs(year: int, month: int, color: str) -> None:
    dataset_file = f'{color}_tripdata_{year}-{month:02}'
    dataset_url = f'https://github.com/DataTalksClub/nyc-tlc-data/releases/download/{color}/{dataset_file}.csv.gz'
    df = get_data(dataset_url)
    df = transform(df, color)
    path = write_local(df, color, dataset_file)
    write_gcs(path)


@flow()
def etl_parent_flow(
        month: list[int] = [1, 2], year: int = 2021, color: str = 'yellow'
):
    for month in month:
        etl_web_to_gcs(year, month, color)


if __name__ == '__main__':
    color = 'green'
    month = [1]
    year = 2020
    etl_parent_flow(month, year, color)
