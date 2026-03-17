# Module 7 – Streaming (Kafka / Redpanda & PyFlink)

This repository contains my solution for Module 7 of the Data Engineering Zoomcamp.

The goal of this module is to practice working with:

- Streaming data pipelines
- Kafka (Redpanda)
- Producers and Consumers
- PyFlink (stream processing)
- Window functions (Tumbling & Session)
- Writing streaming results to PostgreSQL

---

## Architecture

Green Taxi Dataset (Oct 2025 Parquet)  
        ↓  
Python Producer (Kafka)  
        ↓  
Redpanda (Kafka Broker)  
        ↓  
PyFlink Streaming Jobs  
        ↓  
PostgreSQL (Results Storage)  

---

## Infrastructure Setup

All services are run using Docker:

```bash
cd workshop
docker compose down -v
docker compose build
docker compose up -d
```

This starts:

- Redpanda (Kafka) → localhost:9092
- Flink Job Manager → http://localhost:8081
- Flink Task Manager
- PostgreSQL → localhost:5432

---

## Step 1 – Create Kafka Topic

```bash
docker exec -it workshop-redpanda-1 rpk topic create green-trips
```

---

## Step 2 – Producer (Send Data)

A Python producer reads the parquet dataset and sends records to Kafka.

Key steps:

* Load parquet file with pandas
* Select relevant columns
* Convert datetime fields to string
* Send JSON messages to green-trips topic

```bash
uv run python src/producers/producer_green.py
```

---

## Step 3 - Consumer (Read Data)

A Kafka consumer reads all messages and counts trips where:

```text
trip_distance > 5
```

Run:

```bash
uv run python src/consumers/consumer_green.py
```

---

## Step 4 - PyFlink Jobs

Flink jobs are placed in:

```text
src/job/
```

Submit jobs using:

```bash
docker exec -it workshop-jobmanager-1 flink run -py /opt/src/job/<job_file>.py
```

---

## Windowing Concepts

### Tumbling Window

* Fixed-size, non-overlapping windows
* Example: every 5 minutes or 1 hour

### Session Window

* Dynamic windows based on inactivity gap
* Example: new session starts if no events for 5 minutes

---

## PostgreSQL Access

```bash
docker compose exec postgres psql -U postgres -d postgres
```

---

## Homework Answers

**Q1: Redpanda version**

```text
v25.3.9
```

Explanation:

The command rpk version is executed inside the Redpanda container to verify the running broker version.

---

**Q2: Time to send data**

```text
3.06 seconds → closest answer: 10 seconds
```

Explanation:

The producer reads the parquet dataset and sends each row as a JSON message to Kafka.
The total time includes serialization + network + broker write time.
Since 3.06 seconds is closest to 10 seconds, that is the correct option.

---

**Q3: Trips with distance > 5 km**

```text
8506
```

Explanation:

A Kafka consumer reads all messages from the topic (auto_offset_reset='earliest') and counts rows where:

```text
trip_distance > 5
```

* Note: Kafka topics persist data, so duplicates can occur if data is produced multiple times

---

**Q4: Most trips in a 5-minute window (by pickup location)**

```text
74
```

Explanation:

A 5-minute tumbling window is used:

* Group by PULocationID
* Count trips in each 5-minute window

This identifies the pickup location with the highest activity within any 5-minute interval.

---

**Q5: Longest session (number of trips)**

```text
81
```

Explanation:

A session window (5-minute gap) is used:

- Events are grouped into sessions if they occur within 5 minutes of each other
- Sessions are calculated per PULocationID

* Note: PARTITION BY PULocationID is required, otherwise sessions are computed globally and results become incorrect

---

**Q6: Hour with highest total tip amount**

```text
2025-10-16 18:00:00
```

Explanation:

A 1-hour tumbling window is used:
* Aggregate SUM(tip_amount) per hour
* Identify the hour with the highest total tips

This shows how streaming systems can compute time-based business metrics.

---

## Summary

This module demonstrates a complete streaming pipeline:

- Data is produced from a parquet dataset into Kafka (Redpanda)
- Consumers validate and process streaming data
- PyFlink performs real-time windowed aggregations
- Results are written into PostgreSQL for querying

This architecture reflects real-world streaming systems used in production environments.
