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
        tip_amount DOUBLE,
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
    CREATE TABLE q6_sink (
        window_start TIMESTAMP(3),
        total_tip DOUBLE,
        PRIMARY KEY (window_start) NOT ENFORCED
    ) WITH (
        'connector' = 'jdbc',
        'url' = 'jdbc:postgresql://postgres:5432/postgres',
        'table-name' = 'q6_results',
        'username' = 'postgres',
        'password' = 'postgres',
        'driver' = 'org.postgresql.Driver'
    )
    """

    t_env.execute_sql(source_ddl)
    t_env.execute_sql(sink_ddl)

    result = t_env.execute_sql("""
    INSERT INTO q6_sink
    SELECT
        window_start,
        SUM(tip_amount) AS total_tip
    FROM TABLE(
        TUMBLE(TABLE green_trips, DESCRIPTOR(event_timestamp), INTERVAL '1' HOUR)
    )
    GROUP BY window_start
    """)

    result.wait()


if __name__ == "__main__":
    main()