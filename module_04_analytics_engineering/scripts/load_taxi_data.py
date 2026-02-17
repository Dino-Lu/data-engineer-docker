import os
import io
import requests
from tqdm import tqdm
from google.cloud import storage, bigquery

BASE = "https://github.com/DataTalksClub/nyc-tlc-data/releases/download"
TAXIS = ["green", "yellow"]
YEARS = [2019, 2020]
MONTHS = [f"{m:02d}" for m in range(1, 13)]

CHUNK_SIZE = 1024 * 1024  # 1 MiB


def env(name: str) -> str:
    v = os.getenv(name)
    if not v:
        raise RuntimeError(f"Missing env var: {name}")
    return v


def upload_gz_to_gcs(
    storage_client: storage.Client,
    bucket_name: str,
    gcs_path: str,
    resp: requests.Response,
) -> str:
    """
    Stream-download a .csv.gz and stream-upload into GCS without saving to disk.
    """
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(gcs_path)

    buf = io.BytesIO()
    for chunk in resp.iter_content(chunk_size=CHUNK_SIZE):
        if chunk:
            buf.write(chunk)
    buf.seek(0)

    blob.upload_from_file(buf, content_type="application/gzip")
    return f"gs://{bucket_name}/{gcs_path}"


def ensure_dataset(bq_client: bigquery.Client, project_id: str, dataset: str) -> None:
    ds_id = f"{project_id}.{dataset}"
    try:
        bq_client.get_dataset(ds_id)
    except Exception:
        ds = bigquery.Dataset(ds_id)
        ds.location = "US"
        bq_client.create_dataset(ds, exists_ok=True)


def load_to_landing(
    bq_client: bigquery.Client,
    project_id: str,
    dataset: str,
    landing_table: str,
    uris: list[str],
) -> str:
    """
    Load gzipped CSVs from GCS into a landing table using autodetect.
    This helps avoid schema drift issues across months.
    """
    landing_id = f"{project_id}.{dataset}.{landing_table}"

    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=1,
        autodetect=True,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
    )

    job = bq_client.load_table_from_uri(uris, landing_id, job_config=job_config)
    job.result()
    return landing_id


def create_partitioned_final(
    bq_client: bigquery.Client,
    project_id: str,
    dataset: str,
    final_table: str,
    landing_table_id: str,
    pickup_col: str,
) -> str:
    final_id = f"{project_id}.{dataset}.{final_table}"

    sql = f"""
    CREATE OR REPLACE TABLE `{final_id}`
    PARTITION BY DATE({pickup_col})
    AS
    SELECT * FROM `{landing_table_id}`;
    """

    bq_client.query(sql).result()
    return final_id


def main():
    project_id = env("GCP_PROJECT_ID")
    bucket_name = env("GCS_BUCKET")
    gcs_prefix = env("GCS_PREFIX").rstrip("/")  # e.g. nyc_taxi
    bq_dataset = env("BQ_DATASET")              # e.g. nytaxi

    storage_client = storage.Client(project=project_id)
    bq_client = bigquery.Client(project=project_id)

    ensure_dataset(bq_client, project_id, bq_dataset)

    # Collect GCS URIs per taxi type
    uris_by_taxi: dict[str, list[str]] = {"green": [], "yellow": []}

    print("Downloading + uploading taxi files (2019–2020) to GCS...")
    plan = [(taxi, year, month) for taxi in TAXIS for year in YEARS for month in MONTHS]
    for taxi, year, month in tqdm(plan):
        filename = f"{taxi}_tripdata_{year}-{month}.csv.gz"
        url = f"{BASE}/{taxi}/{filename}"
        gcs_path = f"{gcs_prefix}/{taxi}/{year}/{filename}"

        resp = requests.get(url, stream=True, timeout=180)
        resp.raise_for_status()

        uri = upload_gz_to_gcs(storage_client, bucket_name, gcs_path, resp)
        uris_by_taxi[taxi].append(uri)

    print("All files uploaded to GCS.")
    print("Loading into BigQuery (landing -> partitioned final tables)...")

    taxi_cfg = {
        "green": {
            "landing": "_landing_green_tripdata",
            "final": "green_tripdata",
            "pickup_col": "lpep_pickup_datetime",
        },
        "yellow": {
            "landing": "_landing_yellow_tripdata",
            "final": "yellow_tripdata",
            "pickup_col": "tpep_pickup_datetime",
        },
    }

    for taxi, cfg in taxi_cfg.items():
        uris = uris_by_taxi[taxi]
        if not uris:
            raise RuntimeError(f"No URIs uploaded for taxi={taxi}")

        print(f"\n[{taxi}] Loading landing table from {len(uris)} files...")
        landing_id = load_to_landing(
            bq_client=bq_client,
            project_id=project_id,
            dataset=bq_dataset,
            landing_table=cfg["landing"],
            uris=uris,
        )

        print(f"[{taxi}] Creating partitioned final table...")
        final_id = create_partitioned_final(
            bq_client=bq_client,
            project_id=project_id,
            dataset=bq_dataset,
            final_table=cfg["final"],
            landing_table_id=landing_id,
            pickup_col=cfg["pickup_col"],
        )

        print(f"[{taxi}] Done. Final table replaced: {final_id}")

    print("\n✅ Completed. These tables were replaced:")
    print(f" - {project_id}.{bq_dataset}.green_tripdata (partitioned)")
    print(f" - {project_id}.{bq_dataset}.yellow_tripdata (partitioned)")
    print("\nLanding tables kept (optional to drop):")
    print(f" - {project_id}.{bq_dataset}._landing_green_tripdata")
    print(f" - {project_id}.{bq_dataset}._landing_yellow_tripdata")


if __name__ == "__main__":
    main()