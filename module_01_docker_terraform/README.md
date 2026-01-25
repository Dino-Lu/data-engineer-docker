# Module 1 Homework: Docker & SQL

## Question 1: Understanding Docker images

Command used:

```bash
docker run -it --rm --entrypoint=bash python:3.13
pip --version
```

Answer: 25.3


## Question 2: Understanding Docker networking

Answer:
db:5432

Explanation:
Docker Compose creates a shared network for services.
Containers communicate with each other using the service name as the hostname
and the internal container port.
pgAdmin connects to PostgreSQL using the docker-compose service name which is db
and the internal container port which is 5432.


## Data Preparation (for Questions 3–6)

PostgreSQL was started using Docker Compose:

```bash
docker-compose up -d
docker ps
```

The database was accessed using pgcli via the exposed port:

```bash
uv run pgcli -h localhost -p 5432 -u root -d ny_taxi #password: root
SELECT version();
```

Taxi trip data and zone lookup data were ingested into PostgreSQL using
a Jupyter Notebook with pandas and SQLAlchemy:

- Green taxi trips: green_tripdata_2025-11.parquet

- Zone lookup: taxi_zone_lookup.csv

Two tables were created:

- green_tripdata

- zones

Verification commands:

```bash
\dt #check tables
\d green_tripdata #check columns
\d zones #check columns
\q
```

## Question 3: Counting short trips

SQL query used:

```sql
SELECT COUNT(*)
FROM green_tripdata
WHERE trip_distance <= 1
  AND lpep_pickup_datetime >= '2025-11-01'
  AND lpep_pickup_datetime < '2025-12-01';
```

Answer: 8007


## Question 4: Longest trip per day

SQL query used:

```sql
SELECT
    DATE(lpep_pickup_datetime) AS pickup_day,
    MAX(trip_distance) AS max_trip_distance
FROM green_tripdata
WHERE lpep_pickup_datetime >= '2025-11-01'
  AND lpep_pickup_datetime < '2025-12-01'
  AND trip_distance < 100
GROUP BY pickup_day
ORDER BY max_trip_distance DESC
LIMIT 1;
```

Answer: 2025-11-14 88.03


## Question 5: Biggest pickup zone

SQL query used:

```sql
SELECT
    z."Zone" AS pickup_zone,
    SUM(t.total_amount) AS total_revenue
FROM green_tripdata t
JOIN zones z
  ON t."PULocationID" = z."LocationID"
WHERE t.lpep_pickup_datetime >= '2025-11-18'
  AND t.lpep_pickup_datetime < '2025-11-19'
GROUP BY z."Zone"
ORDER BY total_revenue DESC
LIMIT 1;
```

Answer: East Harlem North 9281.92


## Question 6: Largest tip

SQL query used:

```sql
SELECT
    dz."Zone" AS dropoff_zone,
    MAX(t.tip_amount) AS max_tip
FROM green_tripdata t
JOIN zones pz
  ON t."PULocationID" = pz."LocationID"
JOIN zones dz
  ON t."DOLocationID" = dz."LocationID"
WHERE pz."Zone" = 'East Harlem North'
  AND t.lpep_pickup_datetime >= '2025-11-01'
  AND t.lpep_pickup_datetime < '2025-12-01'
GROUP BY dz."Zone"
ORDER BY max_tip DESC
LIMIT 1;
```

Answer: Yorkville West 81.89 


## Question 7: Terraform Workflow

Answer:
terraform init, terraform apply -auto-approve, terraform destroy

Explanation:
- `terraform init` downloads provider plugins and initializes the backend
- `terraform apply -auto-approve` generates and applies the execution plan without manual confirmation
- `terraform destroy` removes all resources managed by Terraform
