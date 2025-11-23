package bigdata.kstream.demo;

import java.util.Arrays;
import java.util.Properties;
import org.apache.kafka.streams.*;
import org.apache.kafka.streams.kstream.*;

public class ComplexPipe {
    public static void main(String[] args) {
        // 1. create streams properties.
        final Properties p = Util.getStreamsProperties("ComplexPipe", "localhost:9092");

        // 2. define stream processing topology.
        final StreamsBuilder builder = new StreamsBuilder();

        // Create source stream from "bigdata" and "ebusiness" topics
        KStream<String, String> source = builder.stream(Arrays.asList("bigdata", "ebusiness"));

        // Apply conditional transformation: toUpperCase if length > 20, toLowerCase otherwise
        KStream<String, String> process = source.mapValues((key, value) -> {
            if (value == null) {
                return null;
            }
            if (value.length() > 20) {
                return value.toUpperCase();
            } else {
                return value.toLowerCase();
            }
        }, Named.as("conditional-transformation"));

        // 3. Route all messages to "archive" topic
        process.to("archive");

        // 4. Conditionally route to "analytics" topic (only uppercase messages)
        Predicate<String, String> isUpper = (key, value) -> {
            return value != null && value.equals(value.toUpperCase());
        };
        process.filter(isUpper, Named.as("filter-for-analytics")).to("analytics");

        // Build topology and create KafkaStreams
        final KafkaStreams streams = new KafkaStreams(builder.build(), p);

        try {
            streams.start();

            // Register shutdown hook for graceful termination
            Runtime.getRuntime().addShutdownHook(new Thread("ComplexPipe-ShutdownHook") {
                @Override
                public void run() {
                    streams.close();
                }
            });

            System.out.print("Hit ENTER to finish: ");
            new java.util.Scanner(System.in).nextLine();
        } catch (Exception e) {
            e.printStackTrace();
        } finally {
            streams.close();
        }
    }
}

