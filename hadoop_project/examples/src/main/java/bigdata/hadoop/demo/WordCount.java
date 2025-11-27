package bigdata.hadoop.demo;

import java.io.IOException;
import java.util.StringTokenizer;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.mapreduce.Reducer;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;

public class WordCount {

   public static class TokenizerMapper extends Mapper<Object, Text, Text, IntWritable> {

      private final static IntWritable one = new IntWritable(1);
      private Text word = new Text();

      public void map(Object key, Text value, Context context) throws IOException, InterruptedException {
         StringTokenizer itr = new StringTokenizer(value.toString());
         while (itr.hasMoreTokens()) {
            word.set(itr.nextToken());
            context.write(word, one);
         }
      }
   }

   public static class IntSumReducer extends Reducer<Text, IntWritable, Text, IntWritable> {
      private IntWritable result = new IntWritable();

      public void reduce(Text key, Iterable<IntWritable> values, Context context)
            throws IOException, InterruptedException {
         int sum = 0;
         for (IntWritable val : values)
            sum += val.get();
         result.set(sum);
         context.write(key, result);
      }
   }

   public static void main(String[] args) {
      Configuration conf = new Configuration();
      conf.set("fs.defaultFS", "hdfs://bigpie1:9000");
      conf.set("mapreduce.framework.name", "yarn");
      conf.set("yarn.resourcemanager.hostname", "bigpie1");
      conf.set("yarn.resourcemanager.address", "bigpie1:8032");
      conf.set("yarn.app.mapreduce.am.resource.mb", "512");
      conf.set("mapreduce.map.memory.mb", "256");
      conf.set("mapreduce.reduce.memory.mb", "256");
      conf.setLong("ipc.client.connect.timeout", 120000L);  // 120 sec.
      conf.setLong("ipc.client.rpc-timeout.ms", 300000L);  // 300 sec.

      try {
         Job job = Job.getInstance(conf, "Word Count v3");
         job.setJarByClass(WordCount.class);
         job.setMapperClass(TokenizerMapper.class);
         job.setCombinerClass(IntSumReducer.class);
         job.setReducerClass(IntSumReducer.class);
         job.setOutputKeyClass(Text.class);
         job.setOutputValueClass(IntWritable.class);
         FileInputFormat.addInputPath(job, new Path(args[0]));
         FileOutputFormat.setOutputPath(job, new Path(args[1]));

         System.exit(job.waitForCompletion(true) ? 0 : 1);
      } catch (IOException e) {
         e.printStackTrace();
      } catch (ClassNotFoundException e) {
         e.printStackTrace();
      } catch (InterruptedException e) {
         e.printStackTrace();
      }
   }
}

