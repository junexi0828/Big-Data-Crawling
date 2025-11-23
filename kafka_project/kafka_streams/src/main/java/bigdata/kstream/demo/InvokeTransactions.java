package bigdata.kstream.demo;

import java.util.Arrays;
import java.util.List;
import java.util.Properties;
import java.util.concurrent.ThreadLocalRandom;
import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.clients.producer.ProducerConfig;
import org.apache.kafka.clients.producer.ProducerRecord;
import org.apache.kafka.common.serialization.FloatSerializer;

public class InvokeTransactions {
    public static void main(String[] args) {
        // Use Util from kafka.demo package for producer properties
        Properties p = bigdata.kafka.demo.Util.getProducerProperties("localhost:9092");
        p.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, FloatSerializer.class.getName());

        KafkaProducer<String, Float> producer = new KafkaProducer<>(p);

        // user list.
        List<String> users = Arrays.asList("bob", "alice", "john");

        try {
            // send 10 records
            for (int i = 0; i < 10; i++) {
                // pick a user
                String user = users.get(i % users.size());

                // generate amount.
                float amount = ThreadLocalRandom.current().nextFloat() * 30.0f - 10.0f; // -10.0 to 20.0

                System.out.printf("[InvokeTransaction] %s account balance changed by %.02f%n", user, amount);

                ProducerRecord<String, Float> record = new ProducerRecord<>("account", user, amount);
                producer.send(record);
                producer.flush();

                Thread.sleep(1000); // wait 1 second between transactions
            }
        } catch (Exception e) {
            e.printStackTrace();
        } finally {
            producer.close();
        }
    }
}

