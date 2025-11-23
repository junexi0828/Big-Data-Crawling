package bigdata.kstream.demo;

import java.util.*;
import org.apache.kafka.streams.*;
import org.apache.kafka.streams.kstream.KStream;

public class SimplePipe {
    public static void main(String[] args) {
        // 1. create a streams properties.
        final Properties p = Util.getStreamsProperties("SimplePipe", "localhost:9092");

        // 2. define stream processing topology.
        final StreamsBuilder builder = new StreamsBuilder();
        KStream<String, String> source = builder.stream("bigdata"); // source stream.
        KStream<String, String> processor = source.mapValues(v -> { // apply transformation.
            String vNew = v.toUpperCase();
            System.out.println("[SimplePipe] processed: " + v + " -> " + vNew);
            return vNew;
        });
        processor.to("analytics"); // sink stream.

        // 3.1. create KafkaStreams.
        Topology t = builder.build(); // build topology.
        System.out.println(t.describe()); // print TopologyDescription.
        final KafkaStreams streams = new KafkaStreams(t, p);
        try {
            streams.start(); // 3.2. start stream processing.

            // register ShutdownHook for safe termination of this application.
            Runtime.getRuntime().addShutdownHook(new Thread("SimplePipe-ShutdownHook") {
                @Override
                public void run() {
                    streams.close();
                }
            });

            System.out.print("Hit ENTER to finish: ");
            new Scanner(System.in).nextLine();
        } catch (Exception e) {
            e.printStackTrace();
        } finally {
            streams.close(); // 4. close the stream.
        }
    }
}

