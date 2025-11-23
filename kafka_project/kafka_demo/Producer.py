from kafka import KafkaProducer
from kafka import KafkaConsumer
from kafka.errors import KafkaError

def write(bootServerList, topic, message):  # Kafka Producer.
    producer = None
    try:
        producer = KafkaProducer(bootstrap_servers=bootServerList)
        future = producer.send(topic, key=b'message-key', value=message)  # send message (topic, key, value)
        record_metadata = future.get(timeout=10)  # optionally check delivery result.
        print(f"Msg '{message}' completed. Partition: {record_metadata.partition}, Offset: {record_metadata.offset}")
    except KafkaError as e:
        print(f"Message delivery failure: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        if producer is not None:
            producer.close()

# Send test message
if __name__ == "__main__":
    try:
        bootstrap_servers = ['localhost:9092']  # Kafka server address and port (single node setup)
        write(bootstrap_servers, topic='bigdata', message=b'Hello from python. Do you get it?')
        write(bootstrap_servers, topic='bigdata', message=b'You need to send bytes string for kafka topic.')
    except KeyboardInterrupt:
        print("\n[Producer.py] Interrupted by user")
    except Exception as e:
        print(f"[Producer.py] Error: {e}")

