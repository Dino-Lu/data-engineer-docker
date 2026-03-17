# Data Engineering Projects

This repository demonstrates practical implementations of core data engineering concepts, including batch processing, data warehousing, and real-time streaming systems.

The projects focus on building end-to-end data pipelines using modern tools and distributed processing frameworks.

---

## Tech Stack

- Python
- Docker & Docker Compose
- Apache Spark (PySpark)
- dbt
- Kafka (Redpanda)
- PyFlink
- PostgreSQL
- Google BigQuery
- Google Cloud Storage (GCS)

---

## Project Overview

### Batch Processing (Apache Spark)

- Processed large-scale NYC taxi datasets using PySpark
- Applied partitioning strategies for efficient storage and computation
- Performed aggregations on distributed data

📁 [module_06_batch](./module_06_batch)

---

### Data Warehousing (BigQuery)

- Built external and native tables in BigQuery
- Implemented partitioning and clustering for query optimization
- Analyzed query performance and data scanning behavior

📁 [module_03_data_warehouse](./module_03_data_warehouse)

---

### Streaming Pipelines (Kafka + PyFlink)

- Built a real-time data pipeline using Redpanda (Kafka-compatible broker)
- Implemented producers and consumers for streaming ingestion
- Designed streaming jobs using PyFlink:
  - Tumbling windows (time-based aggregation)
  - Session windows (event-driven grouping)
- Stored processed results in PostgreSQL

📁 [module_07_streaming](./module_07_streaming)

---

## Additional Modules

- **Docker & Environment Setup** – containerized development environment
- **Workflow Orchestration** – pipeline execution concepts
- **Analytics Engineering** – data transformation and modeling

---

## Concepts Demonstrated

- Batch vs streaming processing
- Distributed computation with Spark
- Event-driven architectures with Kafka
- Stateful stream processing with Flink
- Windowing strategies:
  - Tumbling windows
  - Session windows
- Data modeling and query optimization

---

## Final Project

A separate repository contains a production-style data pipeline that integrates batch and streaming components.