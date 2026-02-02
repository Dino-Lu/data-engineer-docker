# Module 2 – Workflow Orchestration (Airflow)

This repository contains my solution for Module 2 of the Data Engineering Zoomcamp.
The goal was to extend the existing workflow to process NYC Taxi data for the year 2021
using Airflow, GCP, and Terraform.

## Technologies Used

- Apache Airflow (Docker)
- Google Cloud Platform (GCS, BigQuery)
- Terraform (Infrastructure as Code)
- Python

## Architecture

The workflow follows an ELT pattern:

1. Airflow downloads monthly NYC Taxi CSV files
2. Raw data is uploaded to Google Cloud Storage (Data lake)
3. Data is loaded from GCS into BigQuery tables (Data warehouse)
4. Backfill is used to process historical data (2020–2021)

## Authentication

This project uses keyless authentication via Application Default Credentials (ADC).

Before running anything:

```bash
gcloud auth login
gcloud auth application-default login
gcloud config set project <PROJECT_ID>
```

## Infrastructure Setup (Terraform)

Terraform provisions the required GCP resources:

- GCS bucket for raw data (data lake)
- BigQuery dataset `taxi_data` (data warehouse)

Commands:

```bash
cd terraform
terraform init
terraform apply -var="project_id=<PROJECT_ID>"
```

## DAGs

Two DAGs are created:

- taxi_to_gcs_green
- taxi_to_gcs_yellow

Each DAG:
- Runs monthly
- Is parameterized by execution date
- Downloads the corresponding NYC Taxi CSV file
- Uploads it to GCS
- Loads it into BigQuery

## Backfill

The workflow was extended to include data for 2021 (January–July).

Backfill was performed using:

```bash
docker compose exec airflow-webserver airflow dags backfill \
  -s 2021-01-01 -e 2021-07-01 taxi_to_gcs_green
docker compose exec airflow-webserver airflow dags backfill \
  -s 2021-01-01 -e 2021-07-01 taxi_to_gcs_yellow
docker compose exec airflow-webserver airflow dags backfill \
  -s 2021-03-01 -e 2021-03-01 taxi_to_gcs_yellow
```

## Question 1: 

Command used:

```bash
docker compose exec airflow-webserver bash -lc \
"gunzip -c /tmp/nyc_taxi/yellow/2020/yellow_tripdata_2020-12.csv.gz | wc -c"
```
gunzip -c -> uncompresses without creating a new file
wc -c -> counts bytes
MiB = bytes / 1024 / 1024
**Answer:** 128.27 MiB -> A

## Question 2:

Template:
filename = f"{taxi}_tripdata_{year}-{month}.csv.gz"

**Answer:** green_tripdata_2020-04.csv -> B

## Question 3:

Command used (BigQuery):

```bash
bq query --use_legacy_sql=false \
"SELECT SUM(cnt) AS total_rows
 FROM (
   SELECT COUNT(*) AS cnt FROM \`zoomcamp-airflow-486119.taxi_data.yellow_tripdata_202001\`
   UNION ALL SELECT COUNT(*) FROM \`zoomcamp-airflow-486119.taxi_data.yellow_tripdata_202002\`
   UNION ALL SELECT COUNT(*) FROM \`zoomcamp-airflow-486119.taxi_data.yellow_tripdata_202003\`
   UNION ALL SELECT COUNT(*) FROM \`zoomcamp-airflow-486119.taxi_data.yellow_tripdata_202004\`
   UNION ALL SELECT COUNT(*) FROM \`zoomcamp-airflow-486119.taxi_data.yellow_tripdata_202005\`
   UNION ALL SELECT COUNT(*) FROM \`zoomcamp-airflow-486119.taxi_data.yellow_tripdata_202006\`
   UNION ALL SELECT COUNT(*) FROM \`zoomcamp-airflow-486119.taxi_data.yellow_tripdata_202007\`
   UNION ALL SELECT COUNT(*) FROM \`zoomcamp-airflow-486119.taxi_data.yellow_tripdata_202008\`
   UNION ALL SELECT COUNT(*) FROM \`zoomcamp-airflow-486119.taxi_data.yellow_tripdata_202009\`
   UNION ALL SELECT COUNT(*) FROM \`zoomcamp-airflow-486119.taxi_data.yellow_tripdata_202010\`
   UNION ALL SELECT COUNT(*) FROM \`zoomcamp-airflow-486119.taxi_data.yellow_tripdata_202011\`
   UNION ALL SELECT COUNT(*) FROM \`zoomcamp-airflow-486119.taxi_data.yellow_tripdata_202012\`
 )"
 ```

 **Answer:** 24,648,499 -> B

 ## Question 4:

 Command used (BigQuery):

```bash
bq query --use_legacy_sql=false \
"SELECT SUM(cnt) AS total_rows
 FROM (
   SELECT COUNT(*) AS cnt FROM \`zoomcamp-airflow-486119.taxi_data.green_tripdata_202001\`
   UNION ALL SELECT COUNT(*) FROM \`zoomcamp-airflow-486119.taxi_data.green_tripdata_202002\`
   UNION ALL SELECT COUNT(*) FROM \`zoomcamp-airflow-486119.taxi_data.green_tripdata_202003\`
   UNION ALL SELECT COUNT(*) FROM \`zoomcamp-airflow-486119.taxi_data.green_tripdata_202004\`
   UNION ALL SELECT COUNT(*) FROM \`zoomcamp-airflow-486119.taxi_data.green_tripdata_202005\`
   UNION ALL SELECT COUNT(*) FROM \`zoomcamp-airflow-486119.taxi_data.green_tripdata_202006\`
   UNION ALL SELECT COUNT(*) FROM \`zoomcamp-airflow-486119.taxi_data.green_tripdata_202007\`
   UNION ALL SELECT COUNT(*) FROM \`zoomcamp-airflow-486119.taxi_data.green_tripdata_202008\`
   UNION ALL SELECT COUNT(*) FROM \`zoomcamp-airflow-486119.taxi_data.green_tripdata_202009\`
   UNION ALL SELECT COUNT(*) FROM \`zoomcamp-airflow-486119.taxi_data.green_tripdata_202010\`
   UNION ALL SELECT COUNT(*) FROM \`zoomcamp-airflow-486119.taxi_data.green_tripdata_202011\`
   UNION ALL SELECT COUNT(*) FROM \`zoomcamp-airflow-486119.taxi_data.green_tripdata_202012\`
 )"
 ```

 **Answer:** 1,734,051 -> C

 ## Question 5:

 Command used (BigQuery):

```bash
bq query --use_legacy_sql=false \
"SELECT COUNT(*) AS cnt
 FROM \`zoomcamp-airflow-486119.taxi_data.yellow_tripdata_202103\`"
 ```

 **Answer:** 1,925,152 -> C

 ## Question 6:

 Schedulers use IANA timezone names; New York is America/New_York.

 **Answer:** B