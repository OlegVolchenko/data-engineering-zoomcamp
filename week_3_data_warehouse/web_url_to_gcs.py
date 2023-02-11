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
def transform(df: pd.DataFrame) -> pd.DataFrame:
    """Fix dtype issues"""
    print(print(f'processed {len(df)} rows of data'))
    return df


@task(name='write result to local', log_prints=True)
def write_local(df: pd.DataFrame, dataset_file) -> Path:
    """Writes DataFrame as parquet file"""
    if not os.path.isdir(f'data/dwh'):
        os.makedirs(f'data/dwh')
    path = Path(f'data/dwh/{dataset_file}.csv.gz')
    df.to_csv(path, compression='gzip')
    print(f'loaded {len(df)} rows into a parquet file')
    return path


@task(name='Write result to gcs')
def write_gcs(path: Path) -> None:
    """Upload parquet file to gcs"""
    gcp_cloud_storage_bucket_block = GcsBucket.load("gcp-bucket-w3")
    gcp_cloud_storage_bucket_block.upload_from_path(from_path=path, to_path=path)

@flow(name='DWH', log_prints=True)
def dwh_web_to_gcs(months: List[int], year: int) -> None:
    for month in months:
        dataset_file = f'fhv_tripdata_{year}-{month:02}'

        dataset_url = f'https://github.com/DataTalksClub/nyc-tlc-data/releases/download/fhv/{dataset_file}.csv.gz'
        df = get_data(dataset_url)
        df = transform(df)
        path = write_local(df, dataset_file)
        write_gcs(path)

if __name__ == '__main__':
    # Initialize parser
    parser = argparse.ArgumentParser()

    dwh_web_to_gcs([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], 2019)