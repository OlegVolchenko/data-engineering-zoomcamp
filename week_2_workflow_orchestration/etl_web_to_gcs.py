import argparse
from pathlib import Path
import pandas as pd
from prefect import task, flow
from prefect_gcp.cloud_storage import GcsBucket
from typing import List
import os
from prefect.blocks.notifications import SlackWebhook


@task(name='Get df', retries=3, log_prints=True)
def get_data(dataset_url: str) -> pd.DataFrame:
    """Read static file from web"""
    print(f'trying to load {dataset_url}')
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
    print(
        f"Columns dtypes after casting: {datetime_prefix}_dropoff_datetime - "
        f"{df[f'{datetime_prefix}_dropoff_datetime'].dtype}")
    print(print(f'processed {len(df)} rows of data'))
    return df


@task(name='write result to local', log_prints=True)
def write_local(df: pd.DataFrame, color: str, dataset_file) -> Path:
    """Writes DataFrame as parquet file"""
    if not os.path.isdir(f'data/{color}'):
        os.makedirs(f'data/{color}')
    path = Path(f'data/{color}/{dataset_file}.parquet')
    df.to_parquet(path, compression='gzip')
    print(f'loaded {len(df)} rows into a parquet file')
    return path


@task(name='Write result to gcs')
def write_gcs(path: Path) -> None:
    """Upload parquet file to gcs"""
    gcp_cloud_storage_bucket_block = GcsBucket.load("bootcamp-bucket-connection")
    gcp_cloud_storage_bucket_block.upload_from_path(from_path=path, to_path=path)
    slack_webhook_block = SlackWebhook.load("bootcamp-webhook")
    slack_webhook_block.notify("Web to gcs ingestion workflow")


@flow(name='Flat file to gcs', log_prints=True)
def etl_web_to_gcs(months: List[int], year: int, color: str) -> None:
    for month in months:
        dataset_file = f'{color}_tripdata_{year}-{month:02}'
        dataset_url = f'https://github.com/DataTalksClub/nyc-tlc-data/releases/download/{color}/{dataset_file}.csv.gz'
        df = get_data(dataset_url)
        df = transform(df, color)
        path = write_local(df, color, dataset_file)
        write_gcs(path)

if __name__ == '__main__':
    # Initialize parser
    parser = argparse.ArgumentParser()

    # Adding optional argument
    parser.add_argument("-m", "--Months", help="A list of months")
    parser.add_argument("-y", "--Year", help="A year")
    parser.add_argument("-c", "--Color", help="A taxi color")

    # Read arguments from command line
    args = parser.parse_args()
    etl_web_to_gcs(args.Months, args.Year, args.Color)
