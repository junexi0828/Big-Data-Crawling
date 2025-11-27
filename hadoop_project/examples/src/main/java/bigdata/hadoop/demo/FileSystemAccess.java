package bigdata.hadoop.demo;

import java.io.InputStream;
import java.net.URI;
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.IOUtils;

public class FileSystemAccess {
   public static void main(String[] args) throws Exception {
      String hdfsFilePath = args[0];  // 1. get the path & filename.
      InputStream in = null;
      try {
         // 2. create a Hadoop Configuration for core-site.xml, hdfs-site.xml.
         Configuration conf = new Configuration();

         // 3. set(or override) "fs.defaultFS" configuration in the core-site.xml.
         conf.set("fs.defaultFS", "hdfs://bigpie1:9000");  // optional step.
         FileSystem fs = FileSystem.get(URI.create(hdfsFilePath), conf); // 4. get FileSystem.

         Path hdfsPath = new Path(hdfsFilePath);  // 5. create a Path object.
         if (!fs.exists(hdfsPath)) {  // 6. check if the file exists.
            System.err.println("Error: File does not exist at " + hdfsFilePath);
            System.exit(1);
         }

         in = fs.open(hdfsPath); // 7. open the file for reading.
         IOUtils.copyBytes(in, System.out, 1024, false); // buffer size 4096, do not close the output stream
      } catch (Exception e) {
         e.printStackTrace();
      } finally {
         IOUtils.closeStream(in);  // 8. close the input stream
      }
   }
}

