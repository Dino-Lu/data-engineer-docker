import os
import requests
from pyspark.sql import SparkSession
from pyspark.sql.functions import to_date, col, unix_timestamp, max

DATA_DIR = "data"
TRIP_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2025-11.parquet"
TRIP_FILE = f"{DATA_DIR}/yellow_tripdata_2025-11.parquet"

ZONE_URL = "https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv"
ZONE_FILE = f"{DATA_DIR}/taxi_zone_lookup.csv"


def download_file(url, path):
    """Download file if it does not exist."""
    os.makedirs(DATA_DIR, exist_ok=True)

    if not os.path.exists(path):
        print(f"Downloading {url} ...")
        r = requests.get(url, stream=True)

        with open(path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

        print("Download complete.")


def create_spark():
    """Create Spark session."""
    spark = (
        SparkSession.builder
        .master("local[*]")
        .appName("spark_batch")
        .getOrCreate()
    )
    return spark


def main():
    download_file(TRIP_URL, TRIP_FILE)
    download_file(ZONE_URL, ZONE_FILE)

    spark = create_spark()

    print("Spark version:", spark.version)

    df = spark.read.parquet(TRIP_FILE)

    # Q2
    df.repartition(4).write.mode("overwrite").parquet("yellow_2025_11_4part")

    # Q3
    trips_15 = df.filter(
        to_date(col("tpep_pickup_datetime")) == "2025-11-15"
    ).count()

    print("Trips on 2025-11-15:", trips_15)

    # Q4
    df_duration = df.withColumn(
        "trip_hours",
        (
            unix_timestamp(col("tpep_dropoff_datetime"))
            - unix_timestamp(col("tpep_pickup_datetime"))
        ) / 3600
    )

    df_duration.select(max("trip_hours")).show()

    # Q6
    zones = spark.read.option("header", True).csv(ZONE_FILE)

    zone_counts = (
        df.join(zones, df.PULocationID == zones.LocationID)
        .groupBy("Zone")
        .count()
    )

    zone_counts.orderBy("count").show(5)

    input("Press Enter to stop Spark...")
    spark.stop()


if __name__ == "__main__":
    main()