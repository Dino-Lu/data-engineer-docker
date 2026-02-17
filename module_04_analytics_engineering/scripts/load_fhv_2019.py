import os
import io
import requests
from tqdm import tqdm
from google.cloud import storage, bigquery

BASE_URL = "https://github.com/DataTalksClub/nyc-tlc-data/releases/download/fhv/"
MONTHS = [f"{i:02d}" for i in range(1, 13)]
CHUNK_SIZE = 1024 * 1024  # 1 MiB


def env(name: str) -> str:
    v = os.getenv(name)
    if not v:
        raise RuntimeError(f"Missing env var: {name}")
    return v


def upload_gz_to_gcs(storage_client: storage.Client, bucket_name: str, gcs_path: str, resp: requests.Response) -> str:
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


def main():
    project_id = env("GCP_PROJECT_ID")
    bucket_name = env("GCS_BUCKET")
    gcs_prefix = env("GCS_PREFIX").rstrip("/")
    bq_dataset = env("BQ_DATASET")
    bq_table = env("BQ_TABLE")

    storage_client = storage.Client(project=project_id)
    bq_client = bigquery.Client(project=project_id)

    uris: list[str] = []

    print("Downloading + uploading 12 FHV files (2019) to GCS...")
    for m in tqdm(MONTHS):
        filename = f"fhv_tripdata_2019-{m}.csv.gz"
        url = BASE_URL + filename
        gcs_path = f"{gcs_prefix}/{filename}"

        resp = requests.get(url, stream=True, timeout=180)
        resp.raise_for_status()

        uri = upload_gz_to_gcs(storage_client, bucket_name, gcs_path, resp)
        uris.append(uri)

    print(f"Uploaded {len(uris)} files.")
    print("Loading into BigQuery...")

    table_id = f"{project_id}.{bq_dataset}.{bq_table}"

    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=1,
        autodetect=True,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
    )

    load_job = bq_client.load_table_from_uri(uris, table_id, job_config=job_config)
    load_job.result()

    print(f"Done. Loaded: {table_id}")


if __name__ == "__main__":
    main()