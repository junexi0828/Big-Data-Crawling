package bigdata.kafka.demo;

import java.util.Properties;
import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.clients.producer.ProducerRecord;
import org.apache.kafka.clients.producer.RecordMetadata;
import org.apache.kafka.clients.producer.Callback;

public class KeyedCallbackProducer implements Callback {
    public static void main(String[] args) {
        String bootstrapServer = "localhost:9092";
        String topic = "bigdata";

        java.util.Properties prop = Util.getProducerProperties(bootstrapServer); // 1. create a producer properties.
        KafkaProducer<String, String> producer = new KafkaProducer<String, String>(prop); // 2. create a producer.
        KeyedCallbackProducer handler = new KeyedCallbackProducer(); // 3. create a Callback(or handler) object.

        for (int i = 0; i < 10; i++) {
            String message = "Keyed Message from Java " + i; // message value.
            String key = "key-" + (i % 3); // key-0, key-1, key-2.
            // 4. create a ProducerRecord with a key.
            ProducerRecord<String, String> record = new ProducerRecord<String, String>(topic, key, message);
            producer.send(record, handler); // 5. send records with a callback & flush.
            producer.flush();
        }
        producer.close(); // 6. close producer.
    }

    @Override
    public void onCompletion(RecordMetadata metadata, Exception exception) {
        if (exception == null) {
            String info = String.format("Tp=%s, Pt=%s, Oft=%s", metadata.topic(), metadata.partition(), metadata.offset());
            System.out.println("[KeyedCallbackProducer.onCompleted()) " + info);
        } else {
            exception.printStackTrace();
        }
    }
}

