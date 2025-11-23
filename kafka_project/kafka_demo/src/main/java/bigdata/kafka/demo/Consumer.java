package bigdata.kafka.demo;

import java.time.Duration;
import java.util.Properties;
import org.apache.kafka.clients.consumer.ConsumerRecord;
import org.apache.kafka.clients.consumer.ConsumerRecords;
import org.apache.kafka.clients.consumer.KafkaConsumer;

public class Consumer {
    public static void main(String[] args) {
        String bootstrapServer = "localhost:9092";
        String topic = "bigdata";
        String group = "undergraduages";
        // "graduates";

        Properties prop = Util.getConsumerProperties(bootstrapServer, group); // 1. create a consumer properties.
        KafkaConsumer<String, String> consumer = new KafkaConsumer<String, String>(prop); // 2. create a consumer.
        consumer.subscribe(java.util.Arrays.asList(topic)); // 3. subscribe to topics.

        try {
            int messageCount = 0;
            final int MAX_MESSAGES = 100; // 최대 메시지 수 제한 (개선사항)

            while (true) {
                // 4. poll data from the topic.
                ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(50));
                for (ConsumerRecord<String, String> r : records) {
                    String data = String.format("KEY=%s, Msg=%s, Tp=%s, Pt=%s, Oft=%s", r.key(), r.value(), r.topic(), r.partition(), r.offset());
                    System.out.println("[Consumer] " + data);
                    messageCount++;
                    if (messageCount >= MAX_MESSAGES) {
                        System.out.println("[Consumer] Reached maximum message count. Exiting...");
                        return; // 정상 종료
                    }
                }
            }
        } catch (Exception e) {
            System.err.println("[Consumer] Error: " + e.getMessage());
            e.printStackTrace();
        } finally {
            // 4. close (강의 슬라이드 구조 유지 + 개선사항)
            if (consumer != null) {
                consumer.close();
                System.out.println("[Consumer] Closed");
            }
        }
    }
}

