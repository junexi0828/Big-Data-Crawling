package bigdata.kstream.demo;

import java.util.Properties;
import org.apache.kafka.common.serialization.Serdes;
import org.apache.kafka.common.utils.Bytes;
import org.apache.kafka.streams.*;
import org.apache.kafka.streams.kstream.*;
import org.apache.kafka.streams.state.KeyValueStore;
import org.apache.kafka.streams.state.QueryableStoreTypes;
import org.apache.kafka.streams.state.ReadOnlyKeyValueStore;
import org.apache.kafka.streams.errors.InvalidStateStoreException;

public class QueryKTable {
    public static void main(String[] args) {
        // 1. create streams properties.
        Properties props = Util.getStreamsProperties("QueryKTable", "localhost:9092");
        props.put(StreamsConfig.DEFAULT_VALUE_SERDE_CLASS_CONFIG, Serdes.Float().getClass());

        StreamsBuilder builder = new StreamsBuilder();

        // redefine topology
        KStream<String, Float> transactions = builder.stream("account");
        KTable<String, Float> accountBalances = transactions.groupByKey()
            .aggregate(
                () -> 0.0F,
                (key, newValue, aggregate) -> aggregate + newValue,
                Materialized.<String, Float, KeyValueStore<Bytes, byte[]>>as("AccountBalanceStore")
                    .withKeySerde(Serdes.String())
                    .withValueSerde(Serdes.Float())
            );

        // Create and start KafkaStreams
        KafkaStreams streams = new KafkaStreams(builder.build(), props);
        streams.start();

        // Register shutdown hook
        Runtime.getRuntime().addShutdownHook(new Thread(() -> streams.close()));

        try {
            // Wait for the store to be queryable
            ReadOnlyKeyValueStore<String, Float> balanceStore = waitStore("AccountBalanceStore", streams);

            System.out.println("--- Current Account Balances ---");

            // print states
            balanceStore.all().forEachRemaining(keyValue -> {
                System.out.printf("Account: %s, Balance: %.2f%n", keyValue.key, keyValue.value);
            });

            // Keep the application running for continuous querying
            Thread.currentThread().join();
        } catch (Throwable e) {
            e.printStackTrace();
            System.exit(0);
        }
    }

    private static <K, V> ReadOnlyKeyValueStore<K, V> waitStore(String storeName, KafkaStreams streams)
            throws InterruptedException {
        while (true) {
            try {
                if (streams.state() == KafkaStreams.State.RUNNING) {
                    ReadOnlyKeyValueStore<K, V> store = streams.store(
                        StoreQueryParameters.fromNameAndType(storeName, QueryableStoreTypes.keyValueStore())
                    );
                    System.out.println("Store '" + storeName + "' is ready for querying.");
                    return store;
                }
            } catch (InvalidStateStoreException e) {
                // Store not ready yet, wait and retry
            }
            System.out.println("Waiting for store '" + storeName + "' to be ready...");
            Thread.sleep(1000);
        }
    }
}

