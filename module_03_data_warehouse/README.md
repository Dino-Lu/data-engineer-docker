# Module 3 – Data Warehousing & BigQuery

This repository contains my solution for Module 3 of the Data Engineering Zoomcamp.
The goal of this module is to practice working with:

- Google Cloud Storage (GCS)
- BigQuery (External & Native tables)
- Partitioning and Clustering
- Query cost optimization

---

## Architecture

NYC Yellow Taxi Parquet Files (Jan–Jun 2024)
        ↓
Docker-based uploader
        ↓
Google Cloud Storage (Data Lake)
        ↓
BigQuery External Table
        ↓
BigQuery Native Table
        ↓
Partitioned + Clustered Table (Optimized)

---

## Step 1 – Upload Data to GCS (Dockerized)

All uploads were executed inside a Docker container to ensure:

- Clean Linux environment
- No macOS SSL issues
- Reproducible setup

### Build Docker image & run uploader

```bash
docker compose build
docker compose run --rm uploader
```
This uploads 6 parquet files to:
```bash
gs://zoomcamp-airflow-486119-hw3-yellow-2024/yellow/2024/
```

## Step 2 – BigQuery Setup

Create Dataset: hw3

### Create External Table

```sql
CREATE OR REPLACE EXTERNAL TABLE `zoomcamp-airflow-486119.hw3.yellow_ext`
OPTIONS (
  format = 'PARQUET',
  uris = ['gs://zoomcamp-airflow-486119-hw3-yellow-2024/yellow/2024/*.parquet']
);
```

### Create Native Table

```sql
CREATE OR REPLACE TABLE `zoomcamp-airflow-486119.hw3.yellow`
AS
SELECT *
FROM `zoomcamp-airflow-486119.hw3.yellow_ext`;
```

### Create Optimized Table (Partitioned + Clustered)

```sql
CREATE OR REPLACE TABLE `zoomcamp-airflow-486119.hw3.yellow_part_clust`
PARTITION BY DATE(tpep_dropoff_datetime)
CLUSTER BY VendorID
AS
SELECT *
FROM `zoomcamp-airflow-486119.hw3.yellow`;
```


## Question 1: 

SQL query:
```sql
SELECT COUNT(*) FROM `zoomcamp-airflow-486119.hw3.yellow`;
```

**Answer:** 20,332,093

## Question 2:

For the external table, BigQuery reads only minimal metadata without loading full column data when estimating distinct values.
The native table stores data in columnar format, so scanning selected columns reads only those column storage blocks.

**Answer:** 0 MB for External Table and 155.12 MB for Materialized Table

## Question 3:

1 column -> 155.12 MB
2 columns -> 310.24 MB
When selecting one column, BigQuery scans only that column’s storage blocks.
Selecting two columns doubles the amount of column data read.

**Answer:** BigQuery is a columnar database and scans only the columns requested...

## Question 4:

SQL query:
```sql
SELECT COUNT(*)
FROM `zoomcamp-airflow-486119.hw3.yellow`
WHERE fare_amount = 0;
```

This query scans only the fare_amount column.
Because BigQuery is columnar, it does not need to scan other columns in the table.

**Answer:** 8,333

## Question 5:

Partitioning reduces scanned data when filtering by date.
Clustering improves performance when ordering or filtering by VendorID.
Together, they reduce query cost and improve performance for frequent date-based queries.

**Answer:** Partition by tpep_dropoff_datetime and Cluster by VendorID

## Question 6:

SQL query on the regular table: 
```sql
SELECT DISTINCT VendorID
FROM `zoomcamp-airflow-486119.hw3.yellow`
WHERE tpep_dropoff_datetime BETWEEN '2024-03-01' AND '2024-03-15';
```

SQL query on the partitioned + clustered table:
```sql
SELECT DISTINCT VendorID
FROM `zoomcamp-airflow-486119.hw3.yellow_part_clust`
WHERE tpep_dropoff_datetime BETWEEN '2024-03-01' AND '2024-03-15';
```

Non-partitioned -> 310.24 MB
Partitioned -> 26.84 MB
The partitioned table scans only March partitions when filtering on a March date range.
Partition pruning significantly reduces the amount of data scanned, and this directly reduces query cost.

**Answer:** 310.24 MB for non-partitioned table and 26.84 MB for the partitioned table

## Question 7:

External tables reference data stored in GCS.
BigQuery does not store the data internally for external tables.

**Answer:** GCP Bucket

## Question 8:

Clustering improves performance only when queries frequently filter or sort by the clustered columns.
Unnecessary clustering can increase maintenance overhead without performance benefit.

**Answer:** False

## Question 9

SQL query:
```sql
SELECT COUNT(*)
FROM `zoomcamp-airflow-486119.hw3.yellow`;
```

BigQuery uses storage-level metadata and block statistics to compute row counts without scanning column data, which results in 0 MB estimated bytes processed.

**Answer:** 0 MB