from kafka import KafkaConsumer
import json

topic = "green-trips"

consumer = KafkaConsumer(
    topic,
    bootstrap_servers=["localhost:9092"],
    auto_offset_reset="earliest",
    group_id="green-trip-group-q3-clean",
    value_deserializer=lambda x: json.loads(x.decode("utf-8")),
    consumer_timeout_ms=5000,
)

count = 0

for message in consumer:
    trip = message.value

    if float(trip["trip_distance"]) > 5:
        count += 1

print("Trips > 5km:", count)
consumer.close()