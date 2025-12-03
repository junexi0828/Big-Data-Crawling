package bigdata.hadoop.demo;

import java.io.BufferedInputStream;
import java.io.FileInputStream;
import java.io.OutputStream;
import java.net.URI;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.IOUtils;
import org.apache.hadoop.util.Progressable;

public class PutFile {
   public static void main(String[] args) {
      String localFile = args[0];   // "C:/Temp/test.dat"
      String remoteFile = args[1];  // "hdfs://bigpie1:9000/some/file.dat"

      try {
         BufferedInputStream in = new BufferedInputStream(new FileInputStream(localFile));
         Configuration conf = new Configuration();
         FileSystem fs = FileSystem.get(URI.create(remoteFile), conf);
         OutputStream out = fs.create(new Path(remoteFile), new Progressable() {
            public void progress() {
               System.out.println(".");
            }
         });

         IOUtils.copyBytes(in, out, 4096, true);
      } catch (Exception e) {
         e.printStackTrace();
      }
   }
}

