package bigdata.hadoop.demo;

import java.io.InputStream;
import java.net.URL;
import org.apache.hadoop.fs.FsUrlStreamHandlerFactory;

public class URLAccess {
   public static void main(String[] args) {
      // 1. construct a stream handler for hdfs protocol.
      URL.setURLStreamHandlerFactory(new FsUrlStreamHandlerFactory());

      // 2. URL pattern = "hdfs://server:port/path/to/filename.data"
      String resourceURL = "hdfs://bigpie1:9000" + args[0];
      try ( InputStream in = new URL(resourceURL).openStream();    // 3. open url connection.
            InputStream in2 = new URL(resourceURL).openStream() ){
         byte[] buffer = new byte[1024];   // 4. read & write stream.
         int read;
         while ((read = in.read(buffer)) > 0)
            System.out.write(buffer, 0, read);

         System.out.println("==== Use IOUtils (buffer: 1024, close: false) ====");
         org.apache.hadoop.io.IOUtils.copyBytes(in2, System.out, 1024, false);
      } catch (Exception ex) {
         ex.printStackTrace();
      }
   }
}

