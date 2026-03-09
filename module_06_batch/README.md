# Module 6 – Batch Processing (Apache Spark)

This repository contains my solution for Module 6 of the Data Engineering Zoomcamp.

The goal of this module is to practice working with:

- Apache Spark
- PySpark DataFrames
- Batch processing
- Partitioning and distributed computation
- Basic aggregations and joins

---

## Architecture

```text
NYC Yellow Taxi Dataset (Nov 2025 Parquet)
        ↓
Python Script (PySpark)
        ↓
Local Spark Session
        ↓
Data Transformations
        ↓
Partitioned Parquet Output
        ↓
Aggregations & Analysis
```

---

## Environment

Python environment managed with **uv**.

Key libraries:

- pyspark
- requests

Spark version used:

Spark 4.1.1

---

## Step 1 – Download Dataset

The script automatically downloads the required datasets if they are not present locally.

Taxi trip dataset:
https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2025-11.parquet

Taxi zone lookup:
https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv

Both files are stored locally inside:

```text
data/
```

---

## Step 2 – Start Spark Session

A local Spark session is created using PySpark:

```python
spark = SparkSession.builder \
    .master("local[*]") \
    .appName("spark_batch") \
    .getOrCreate()
```

---

## Step 3 - Repartition Dataset

The November 2025 taxi dataset is loaded into a Spark DataFrame and repartitioned into 4 partitions.

```python
df = spark.read.parquet(file_name)
df.repartition(4).write.mode("overwrite").parquet("yellow_2025_11_4part")
```

Spark creates four parquet files:

```text
yellow_2025_11_4part/
  ├── part-00000.parquet
  ├── part-00001.parquet
  ├── part-00002.parquet
  └── part-00003.parquet
```

---

## Running the script

From the project directory:

```bash
uv run python spark_batch.py
```

The script will:

1. Download datasets (if missing)
2. Start a local Spark session
3. Repartition the dataset into 4 parquet partitions
4. Compute answers for the homework questions

Spark UI is available at:

```text
http://localhost:4040
```

---

## Homework Answers

**Q1: Install Spark and PySpark**

Spark version:

4.1.1

---

**Q2: Average size of parquet files**

After repartitioning to 4 partitions:

Running:

```bash
ls -lh yellow_2025_11_4part/*.parquet
```

Each file size was approximately:

24 MB

Closest answer:

25MB

---

**Q3: Number of taxi trips on 2025-11-15**

162,604

---

**Q4: Longest trip duration**

90.6 hours

---

**Q5: Spark UI port**

4040

---

**Q6: Least frequent pickup zone**

Governor's Island/Ellis Island/Liberty Island
Arden Heights