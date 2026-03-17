from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import EnvironmentSettings, StreamTableEnvironment


def main():
    env = StreamExecutionEnvironment.get_execution_environment()
    env.set_parallelism(1)
    env.enable_checkpointing(10_000)

    settings = EnvironmentSettings.new_instance().in_streaming_mode().build()
    t_env = StreamTableEnvironment.create(
        env, environment_settings=settings
    )

    source_ddl = """
    CREATE TABLE green_trips (
        lpep_pickup_datetime VARCHAR,
        PULocationID INT,
        event_timestamp AS TO_TIMESTAMP(lpep_pickup_datetime, 'yyyy-MM-dd HH:mm:ss'),
        WATERMARK FOR event_timestamp AS event_timestamp - INTERVAL '5' SECOND
    ) WITH (
        'connector' = 'kafka',
        'topic' = 'green-trips',
        'properties.bootstrap.servers' = 'redpanda:29092',
        'scan.startup.mode' = 'earliest-offset',
        'properties.auto.offset.reset' = 'earliest',
        'format' = 'json'
    )
    """

    sink_ddl = """
    CREATE TABLE q5_sink (
        window_start TIMESTAMP(3),
        window_end TIMESTAMP(3),
        PULocationID INT,
        num_trips BIGINT,
        PRIMARY KEY (window_start, window_end, PULocationID) NOT ENFORCED
    ) WITH (
        'connector' = 'jdbc',
        'url' = 'jdbc:postgresql://postgres:5432/postgres',
        'table-name' = 'q5_results',
        'username' = 'postgres',
        'password' = 'postgres',
        'driver' = 'org.postgresql.Driver'
    )
    """

    t_env.execute_sql(source_ddl)
    t_env.execute_sql(sink_ddl)

    result = t_env.execute_sql("""
    INSERT INTO q5_sink
    SELECT
        window_start,
        window_end,
        PULocationID,
        COUNT(*) AS num_trips
    FROM TABLE(
        SESSION(
            TABLE green_trips PARTITION BY PULocationID,
            DESCRIPTOR(event_timestamp),
            INTERVAL '5' MINUTE
        )
    )
    GROUP BY window_start, window_end, PULocationID
    """)

    result.wait()


if __name__ == "__main__":
    main()