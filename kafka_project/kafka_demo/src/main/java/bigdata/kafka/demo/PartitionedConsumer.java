package bigdata.kafka.demo;

import java.time.Duration;
import java.util.*;
import org.apache.kafka.clients.consumer.*;
import org.apache.kafka.common.PartitionInfo;
import org.apache.kafka.common.TopicPartition;

public class PartitionedConsumer {
    public static void main(String[] args) {
        String bootstrapServer = "localhost:9092";
        String topic = "bigdata";
        String group = "undergraduages";
        // "graduates";

        Properties prop = Util.getConsumerProperties(bootstrapServer, group); // 1. create a consumer properties.
        KafkaConsumer<String, String> consumer = new KafkaConsumer<String, String>(prop); // 2. create a consumer.

        try {
            // get a list of PartitionInfo.
            List<PartitionInfo> pInfos = consumer.partitionsFor(topic);
            System.out.println("Topic(" + topic + ") has " + pInfos.size() + " partitions.");

            // 3. create a list of all TopicPartition objects.
            List<TopicPartition> tps = new ArrayList<>();
            for (PartitionInfo pInfo : pInfos) {
                tps.add(new TopicPartition(pInfo.topic(), pInfo.partition()));
            }

            // 4. assign the TopicPartition list to a consumer.
            consumer.assign(tps);
            consumer.seekToEnd(tps);
            // consumer.seekToBeginning(tps);

            while (true) {
                // 5. poll data from the TopicPartition.
                ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(50));
                for (ConsumerRecord<String, String> r : records) {
                    String data = String.format("KEY=%s, Msg=%s, Tp=%s, Pt=%s, Oft=%s", r.key(), r.value(), r.topic(), r.partition(), r.offset());
                    System.out.println("[Consumer] " + data);
                }
            }
        } catch (Exception e) {
            System.err.println("[PartitionedConsumer] Error: " + e.getMessage());
            e.printStackTrace();
        } finally {
            // 6. close consumer (리소스 정리)
            if (consumer != null) {
                consumer.close();
                System.out.println("[PartitionedConsumer] Closed");
            }
        }
    }
}

