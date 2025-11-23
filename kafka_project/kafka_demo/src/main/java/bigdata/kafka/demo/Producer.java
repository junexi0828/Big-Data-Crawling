package bigdata.kafka.demo;

import java.util.Properties;
import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.clients.producer.ProducerRecord;

public class Producer {
    public static void main(String[] args) {
        String bootstrapServer = "localhost:9092";
        String topic = "bigdata";

        // 1. create a producer properties.
        Properties prop = Util.getProducerProperties(bootstrapServer);

        // 2. create a KafkaProducer and ProducerRecord.
        KafkaProducer<String, String> producer = new KafkaProducer<String, String>(prop);
        String message = "Hello, from Java: " + new java.util.Date();
        ProducerRecord<String, String> record = new ProducerRecord<String, String>(topic, message);
        producer.send(record); // 3. send the record.

        // 4. flush & close the KafkaProducer.
        producer.flush();
        producer.close();
    }
}

