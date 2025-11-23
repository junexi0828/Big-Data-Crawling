package bigdata.kstream.demo;

import java.util.Properties;
import org.apache.kafka.common.serialization.Serdes;
import org.apache.kafka.common.utils.Bytes;
import org.apache.kafka.streams.*;
import org.apache.kafka.streams.kstream.*;
import org.apache.kafka.streams.state.KeyValueStore;

public class AccountBalanceTracker {
    public static void main(String[] args) {
        // 1. create streams properties.
        Properties props = Util.getStreamsProperties("AccountBalanceTracker", "localhost:9092");
        props.put(StreamsConfig.DEFAULT_VALUE_SERDE_CLASS_CONFIG, Serdes.Float().getClass());

        StreamsBuilder builder = new StreamsBuilder();

        // Step 1: Create KStream for input
        KStream<String, Float> transactions = builder.stream("account");

        // Step 2: Transform KStream into KTable (Build KTable)
        KTable<String, Float> accountBalances = transactions.groupByKey()
            .aggregate(
                () -> 0.0F, // initial balance for a new account
                (key, newValue, aggregate) -> aggregate + newValue, // aggregation logic
                Materialized.<String, Float, KeyValueStore<Bytes, byte[]>>as("AccountBalanceStore")
                    .withKeySerde(Serdes.String())
                    .withValueSerde(Serdes.Float())
            );

        // Step 3: Convert KTable to KStream and write to output topic (Sink Stream)
        accountBalances.toStream().to("balance", Produced.with(Serdes.String(), Serdes.Float()));

        // Create and start KafkaStreams
        KafkaStreams streams = new KafkaStreams(builder.build(), props);
        streams.start();

        // Step 4: Register shutdown hook
        Runtime.getRuntime().addShutdownHook(new Thread(streams::close));
    }
}

