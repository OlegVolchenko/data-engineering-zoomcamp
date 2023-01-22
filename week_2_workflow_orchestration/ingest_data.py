#!/usr/bin/env python
# coding: utf-8

import os

from datetime import timedelta
from prefect_sqlalchemy import SqlAlchemyConnector

import pandas as pd
from prefect import flow, task
from prefect.tasks import task_input_hash


@task(log_prints=True, retries=3, name='get data', cache_key_fn=task_input_hash, cache_expiration=timedelta(days=1))
def get_data(url: str) -> pd.DataFrame:
    """Get csv data and transform to pd.DataFrame"""
    print("Reading a csv file")
    df = pd.read_csv(url)
    print(f"{len(df)} rows were loaded into a dataframe")
    return df


@task(log_prints=True, name='transform data')
def transform_data(df: pd.DataFrame) -> pd.DataFrame:
    """Cleans and prepare a datframe"""
    # remove line with missing VendorId
    print('transforming a df')
    print(f'Cleaning missing vendor rows, amount of affected rows: {len(df[df["VendorID"].isnull()])}')
    df = df[~df["VendorID"].isnull()]
    print(f'Cleaning invalid passenger count, amount of affected rows: {len(df[df["passenger_count"] <= 0])}')
    # remove lines with invalid passenger count
    df = df[df["passenger_count"] > 0]
    print('Converting columns to datetime dtype')
    if 'lpep_pickup_datetime' in df.columns:
        df.lpep_pickup_datetime = pd.to_datetime(df.lpep_pickup_datetime)
        df.lpep_dropoff_datetime = pd.to_datetime(df.lpep_dropoff_datetime)
    return df


@task(log_prints=True, name='ingest date to sql')
def load(df, table_name: str) -> None:
    with SqlAlchemyConnector.load("postgres-taxi-db").get_connection(begin=False) as engine:
        print('Ingesting df to postgres')
        df.to_sql(name=table_name, con=engine, if_exists='append')
        print('ingestion is complete')


@flow(log_prints=True, name='ingest flow')
def ingest_data(url: str, table_name: str = 'yellow_taxi_trips') -> None:
    df = get_data(url)
    df = transform_data(df)
    load(df, table_name)


if __name__ == '__main__':
    ingest_data('https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_2021-01.csv.gz')
