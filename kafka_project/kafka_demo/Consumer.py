from kafka import KafkaProducer
from kafka import KafkaConsumer
from kafka.errors import KafkaError


def read(bootServerList, topic, group):  # Kafka Consumer.
    consumer = None
    try:
        consumer = KafkaConsumer(
            topic,
            bootstrap_servers=bootServerList,
            group_id=group,  # Consumer Group ID (mandatory)
            auto_offset_reset="earliest",  # read from the earliest message available.
            key_deserializer=lambda x: (
                x.decode("utf-8") if x else ""
            ),  # Deserialize the message key.
            value_deserializer=lambda x: (
                x.decode("utf-8") if x else ""
            ),  # Deserialize the message value.
        )
        print(f"Waiting for a message from the topic({topic})...")
        for message in consumer:
            print(
                f"Received a message (Partition: {message.partition}, Offset: {message.offset}):"
            )
            print(f" Key: {message.key}")
            print(f" Value: {message.value}")
    except KafkaError as e:
        print(f"Message receive failure: {e}")
    except KeyboardInterrupt:
        print("\n[Consumer.py] Interrupted by user")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        if consumer is not None:
            consumer.close()
            print("[Consumer.py] Closed")


if __name__ == "__main__":
    try:
        bootstrap_servers = [
            "localhost:9092"
        ]  # Kafka server address and port (single node setup)
        read(
            bootstrap_servers, topic="bigdata", group="undergraduates"
        )  # Receive messages from the topic
    except Exception as e:
        print(f"[Consumer.py] Error: {e}")
