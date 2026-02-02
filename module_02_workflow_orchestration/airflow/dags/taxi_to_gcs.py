from __future__ import annotations
from airflow.providers.google.cloud.transfers.gcs_to_bigquery import GCSToBigQueryOperator

import os
from datetime import datetime

import requests
from airflow import DAG
from airflow.models import Variable
from airflow.operators.python import PythonOperator
from google.cloud import storage


def _download_file(url: str, local_path: str) -> None:
    r = requests.get(url, stream=True, timeout=120)
    r.raise_for_status()
    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    with open(local_path, "wb") as f:
        for chunk in r.iter_content(chunk_size=1024 * 1024):
            if chunk:
                f.write(chunk)


def download_taxi_data(taxi: str, **context) -> str:
    """
    Downloads a taxi CSV.gz for the DAG run date.
    Returns the local file path so the next task can upload it.
    """
    # Airflow execution date (logical date)
    ds = context["ds"]  # 'YYYY-MM-DD'
    year = ds[:4]
    month = ds[5:7]

    filename = f"{taxi}_tripdata_{year}-{month}.csv.gz"
    url = f"https://github.com/DataTalksClub/nyc-tlc-data/releases/download/{taxi}/{filename}"

    local_path = f"/tmp/nyc_taxi/{taxi}/{year}/{filename}"

    _download_file(url, local_path)
    # Push path for downstream tasks
    context["ti"].xcom_push(key="local_path", value=local_path)
    context["ti"].xcom_push(key="gcs_blob", value=f"raw/{taxi}/{year}/{filename}")
    return local_path


def upload_to_gcs(**context) -> None:
    bucket_name = Variable.get("GCS_BUCKET")
    local_path = context["ti"].xcom_pull(key="local_path", task_ids="download")
    gcs_blob = context["ti"].xcom_pull(key="gcs_blob", task_ids="download")

    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(gcs_blob)
    blob.upload_from_filename(local_path)

    # Optional: log upload location
    print(f"Uploaded {local_path} to gs://{bucket_name}/{gcs_blob}")


def make_dag(taxi: str) -> DAG:
    """
    Creates one DAG per taxi type (green/yellow),
    scheduled monthly with catchup enabled for backfill.
    """
    with DAG(
        dag_id=f"taxi_to_gcs_{taxi}",
        start_date=datetime(2020, 1, 1),
        schedule="@monthly",
        catchup=True,
        max_active_runs=1,
        default_args={"retries": 1},
        tags=["zoomcamp", "taxi", taxi],
    ) as dag:

        project_id = Variable.get("GCP_PROJECT_ID")
        dataset = Variable.get("BQ_DATASET", default_var="taxi_data")
        bucket = Variable.get("GCS_BUCKET")

        download = PythonOperator(
            task_id="download",
            python_callable=download_taxi_data,
            op_kwargs={"taxi": taxi},
        )

        upload = PythonOperator(
            task_id="upload_to_gcs",
            python_callable=upload_to_gcs,
        )

        load_to_bq = GCSToBigQueryOperator(
            task_id="load_to_bq",
            bucket=bucket,
            source_objects=["{{ ti.xcom_pull(task_ids='download', key='gcs_blob') }}"],
            destination_project_dataset_table=(
                f"{project_id}.{dataset}.{taxi}_tripdata_{{{{ ds_nodash[:6] }}}}"
            ),
            source_format="CSV",
            compression="GZIP",
            skip_leading_rows=1,
            autodetect=True,
            write_disposition="WRITE_TRUNCATE",
            gcp_conn_id="google_cloud_default",
            allow_quoted_newlines=True,
            allow_jagged_rows=True,
            max_bad_records=1000,
        )


        download >> upload >> load_to_bq

    return dag


# Create two DAGs: one for green, one for yellow
dag_green = make_dag("green")
dag_yellow = make_dag("yellow")
