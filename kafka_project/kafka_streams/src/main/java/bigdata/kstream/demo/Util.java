package bigdata.kstream.demo;

import java.util.Properties;
import org.apache.kafka.clients.consumer.ConsumerConfig;
import org.apache.kafka.common.serialization.Serdes;
import org.apache.kafka.streams.StreamsConfig;

public class Util {
    public static Properties getStreamsProperties(String appID, String bootStrapServers) {
        Properties p = new Properties();

        // Mandatory StreamsConfig properties
        p.put(StreamsConfig.APPLICATION_ID_CONFIG, appID);
        p.put(StreamsConfig.BOOTSTRAP_SERVERS_CONFIG, bootStrapServers);
        p.put(StreamsConfig.DEFAULT_KEY_SERDE_CLASS_CONFIG, Serdes.StringSerde.class);
        p.put(StreamsConfig.DEFAULT_VALUE_SERDE_CLASS_CONFIG, Serdes.StringSerde.class);

        // ConsumerConfig property
        p.put(ConsumerConfig.AUTO_OFFSET_RESET_CONFIG, "earliest");

        return p;
    }
}

