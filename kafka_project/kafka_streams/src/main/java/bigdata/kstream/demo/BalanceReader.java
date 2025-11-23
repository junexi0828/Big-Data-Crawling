package bigdata.kstream.demo;

import java.time.Duration;
import java.util.Collections;
import java.util.Properties;
import org.apache.kafka.clients.consumer.ConsumerConfig;
import org.apache.kafka.clients.consumer.ConsumerRecord;
import org.apache.kafka.clients.consumer.ConsumerRecords;
import org.apache.kafka.clients.consumer.KafkaConsumer;
import org.apache.kafka.common.serialization.FloatDeserializer;

public class BalanceReader {
    public static void main(String[] args) {
        // Use Util from kafka.demo package for consumer properties
        Properties props = bigdata.kafka.demo.Util.getConsumerProperties("localhost:9092", "BalanceReader");
        props.put(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, FloatDeserializer.class.getName());

        KafkaConsumer<String, Float> consumer = new KafkaConsumer<>(props);

        // Subscribe to the topic
        consumer.subscribe(Collections.singletonList("balance"));

        try {
            while (true) {
                // Poll for new records
                // Poll every 100ms
                ConsumerRecords<String, Float> records = consumer.poll(Duration.ofMillis(100));

                // print messages
                records.forEach(record -> {
                    System.out.printf("Received -> Key: %s, Value: %.2f (Partition: %d, Offset: %d)%n",
                        record.key(), record.value(), record.partition(), record.offset());
                });
            }
        } catch (Exception e) {
            e.printStackTrace();
        } finally {
            // Close the consumer gracefully
            consumer.close();
        }
    }
}

