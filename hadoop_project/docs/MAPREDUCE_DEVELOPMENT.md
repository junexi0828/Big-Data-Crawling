# MapReduce 개발 가이드

이 문서는 Hadoop MapReduce 애플리케이션을 개발하고 실행하는 방법을 설명합니다.

## 📚 목차

1. [MapReduce 기본 개념](#mapreduce-기본-개념)
2. [개발 환경 설정](#개발-환경-설정)
3. [MapReduce 개발 단계](#mapreduce-개발-단계)
4. [예제 프로그램](#예제-프로그램)
5. [실행 방법](#실행-방법)

---

## MapReduce 기본 개념

### MapReduce란?

MapReduce는 대용량 데이터를 분산 환경에서 처리하기 위한 프로그래밍 모델입니다.

**핵심 특징:**

1. **데이터 이동 최소화**: 처리 코드가 데이터가 있는 서버로 이동

   - 기존 R-DB: 데이터가 처리 로직으로 이동
   - MapReduce: 프로그램이 데이터 노드로 이동

2. **<Key, Value> 기반 처리**

   - 입력: `<Key₁, Value₁>` → `<Key₂, Value₂>` 리스트로 변환
   - 출력: `<Key₂, List<Value₂>>` → `<Key₃, Value₃>` 리스트로 변환

3. **Share Nothing 구조**

   - Map Task와 Reduce Task 간 데이터 공유 없음
   - 각 단계에서 독립적으로 데이터 블록 처리
   - 처리 결과는 HDFS에 저장 및 복제

4. **배치 처리에 최적화**
   - 실시간 처리에는 비효율적 (→ Spark: 마이크로 배치 처리)
   - 대용량 데이터의 배치 처리에 강점

### MapReduce 처리 단계

**WordCount 예제를 통한 처리 흐름:**

```
Input → Splitting → Mapping → Shuffling → Reducing → Result
```

1. **Input**: 원본 데이터

   ```
   Deer Bear Lake
   Car Car Lake
   Deer Car Bear
   ```

2. **Splitting**: 데이터를 여러 블록으로 분할

3. **Mapping**: 각 단어를 `<word, 1>` 형태로 변환

   - `Deer 1`, `Bear 1`, `Lake 1`
   - `Car 1`, `Car 1`, `Lake 1`
   - `Deer 1`, `Car 1`, `Bear 1`

4. **Shuffling**: 같은 키를 가진 값들을 그룹화

   - `Bear: [1, 1]`
   - `Car: [1, 1, 1]`
   - `Deer: [1, 1]`
   - `Lake: [1, 1]`

5. **Reducing**: 각 키의 값들을 집계

   - `Bear 2`
   - `Car 3`
   - `Deer 2`
   - `Lake 2`

6. **Result**: 최종 결과 출력

---

## 개발 환경 설정

### 1. Eclipse IDE에서 Maven 프로젝트 생성

1. **New Maven Project 생성**

   - `File → New → Other... → Maven → Maven Project`
   - `Use default Workspace location` 체크 → `Next`

2. **Archetype 선택**

   - Catalog: `Internal`
   - Archetype: `org.apache.maven.archetypes:maven-archetype-quickstart:1.1`

3. **프로젝트 정보 입력**
   - Group Id: `bigdata`
   - Artifact Id: `hadoop.demo`
   - Version: `0.0.1-SNAPSHOT`

### 2. Maven 의존성 추가

`pom.xml`에 다음 의존성을 추가합니다:

```xml
<dependencies>
    <!-- JUnit (테스트용) -->
    <dependency>
        <groupId>junit</groupId>
        <artifactId>junit</artifactId>
        <version>3.8.1</version>
        <scope>test</scope>
    </dependency>

    <!-- Log4j SLF4J Binding -->
    <dependency>
        <groupId>org.apache.logging.log4j</groupId>
        <artifactId>log4j-slf4j2-impl</artifactId>
        <version>2.25.0</version>
        <scope>compile</scope>
    </dependency>

    <!-- Apache Hadoop Common -->
    <dependency>
        <groupId>org.apache.hadoop</groupId>
        <artifactId>hadoop-common</artifactId>
        <version>3.4.1</version>
    </dependency>

    <!-- Apache Hadoop HDFS Client -->
    <dependency>
        <groupId>org.apache.hadoop</groupId>
        <artifactId>hadoop-hdfs-client</artifactId>
        <version>3.4.1</version>
    </dependency>

    <!-- Apache Hadoop MapReduce Common -->
    <dependency>
        <groupId>org.apache.hadoop</groupId>
        <artifactId>hadoop-mapreduce-client-common</artifactId>
        <version>3.4.1</version>
        <scope>compile</scope>
    </dependency>

    <!-- Apache Hadoop MapReduce JobClient -->
    <dependency>
        <groupId>org.apache.hadoop</groupId>
        <artifactId>hadoop-mapreduce-client-jobclient</artifactId>
        <version>3.4.1</version>
        <scope>compile</scope>
    </dependency>
</dependencies>
```

### 3. Log4j 설정

`src/main/resources/log4j.properties` 파일을 생성하고 다음 내용을 추가합니다:

```properties
hadoop.root.logger=INFO, CONSOLE
hadoop.console.threshold=INFO
log4j.rootLogger=${hadoop.root.logger}
log4j.appender.CONSOLE=org.apache.log4j.ConsoleAppender
log4j.appender.CONSOLE.Threshold=${hadoop.console.threshold}
log4j.appender.CONSOLE.layout=org.apache.log4j.PatternLayout
log4j.appender.CONSOLE.layout.ConversionPattern=%d{ISO8601} %-5p [%C]: %m%n
```

이 설정은 Hadoop의 경고 메시지를 제거하고 로그 출력을 제어합니다.

---

## MapReduce 개발 단계

### 1. <Key, Value> I/O 구조 설계

각 단계에서 사용할 Key-Value 쌍의 구조를 설계합니다.

**예시 (WordCount):**

- Map 입력: `<LongWritable, Text>` (줄 번호, 줄 내용)
- Map 출력: `<Text, IntWritable>` (단어, 1)
- Reduce 입력: `<Text, Iterable<IntWritable>>` (단어, [1, 1, ...])
- Reduce 출력: `<Text, IntWritable>` (단어, 총 개수)

### 2. Mapper 클래스 구현

`org.apache.hadoop.mapreduce.Mapper`를 상속받아 구현합니다.

```java
public static class TokenizerMapper
    extends Mapper<Object, Text, Text, IntWritable> {

    private final static IntWritable one = new IntWritable(1);
    private Text word = new Text();

    public void map(Object key, Text value, Context context)
            throws IOException, InterruptedException {
        StringTokenizer itr = new StringTokenizer(value.toString());
        while (itr.hasMoreTokens()) {
            word.set(itr.nextToken());
            context.write(word, one);
        }
    }
}
```

### 3. Reducer 클래스 구현

`org.apache.hadoop.mapreduce.Reducer`를 상속받아 구현합니다.

```java
public static class IntSumReducer
    extends Reducer<Text, IntWritable, Text, IntWritable> {

    private IntWritable result = new IntWritable();

    public void reduce(Text key, Iterable<IntWritable> values,
            Context context) throws IOException, InterruptedException {
        int sum = 0;
        for (IntWritable val : values)
            sum += val.get();
        result.set(sum);
        context.write(key, result);
    }
}
```

### 4. Driver 클래스 작성

`org.apache.hadoop.mapreduce.Job` 객체를 생성하고 설정합니다.

```java
public static void main(String[] args) {
    Configuration conf = new Configuration();
    conf.set("fs.defaultFS", "hdfs://bigpie1:9000");
    conf.set("mapreduce.framework.name", "yarn");
    conf.set("yarn.resourcemanager.hostname", "bigpie1");

    Job job = Job.getInstance(conf, "Word Count");
    job.setJarByClass(WordCount.class);
    job.setMapperClass(TokenizerMapper.class);
    job.setCombinerClass(IntSumReducer.class);
    job.setReducerClass(IntSumReducer.class);
    job.setOutputKeyClass(Text.class);
    job.setOutputValueClass(IntWritable.class);

    FileInputFormat.addInputPath(job, new Path(args[0]));
    FileOutputFormat.setOutputPath(job, new Path(args[1]));

    System.exit(job.waitForCompletion(true) ? 0 : 1);
}
```

### 5. JAR 파일 빌드 및 실행

```bash
# Maven으로 빌드
mvn clean package

# Hadoop에서 실행
$HADOOP_HOME/bin/hadoop jar target/hadoop.demo-0.0.1-SNAPSHOT.jar \
    bigdata.hadoop.demo.WordCount \
    /wordcount/input /wordcount/output
```

---

## 예제 프로그램

### 1. WordCount

단어 빈도를 계산하는 MapReduce 프로그램입니다.

**파일 위치**: `examples/src/main/java/bigdata/hadoop/demo/WordCount.java`

**실행 방법:**

```bash
# 1. 입력 파일 준비
hdfs dfs -mkdir -p /wordcount/input
echo "Hello Hadoop Bye Bye" > file01.txt
echo "This is a test for mapreduce" >> file01.txt
echo "Hello Hadoop Bye Hadoop" > file02.txt
echo "This is another test for hadoop" >> file02.txt

# 2. HDFS에 업로드
hdfs dfs -put file*.txt /wordcount/input

# 3. WordCount 실행
hadoop jar hadoop.demo-0.0.1-SNAPSHOT.jar \
    bigdata.hadoop.demo.WordCount \
    /wordcount/input /wordcount/output

# 4. 결과 확인
hdfs dfs -cat /wordcount/output/part-r-00000
```

**예상 결과:**

```
Bye        3
Hadoop     3
Hello      2
This       2
a          1
another    1
for        2
hadoop     1
is         2
mapreduce  1
test       2
```

### 2. URLAccess

URL을 통해 HDFS 파일에 접근하는 예제입니다.

**파일 위치**: `examples/src/main/java/bigdata/hadoop/demo/URLAccess.java`

**실행 방법:**

```bash
# HDFS 경로만 전달 (프로토콜과 서버는 코드에서 자동 추가)
java -cp target/hadoop.demo-0.0.1-SNAPSHOT.jar \
    bigdata.hadoop.demo.URLAccess \
    /user/bigdata/input/README.txt
```

**Eclipse에서 실행:**

1. `Run As → Run Configurations...`
2. `Arguments` 탭에서 `Program arguments` 입력: `/user/bigdata/input/README.txt`
3. 실행

**주의사항:**

- 프로그램 인자는 HDFS 경로만 전달 (예: `/user/bigdata/input/README.txt`)
- 코드에서 자동으로 `hdfs://bigpie1:9000`가 앞에 붙습니다
- 실행 전에 해당 파일이 HDFS에 존재해야 합니다

### 3. PutFile

로컬 파일을 HDFS에 업로드하는 예제입니다.

**파일 위치**: `examples/src/main/java/bigdata/hadoop/demo/PutFile.java`

**실행 방법:**

```bash
java -cp target/hadoop.demo-0.0.1-SNAPSHOT.jar \
    bigdata.hadoop.demo.PutFile \
    <local_file_path> <hdfs_file_path>
```

**예시:**

```bash
# Windows 경로 예시
java -cp target/hadoop.demo-0.0.1-SNAPSHOT.jar \
    bigdata.hadoop.demo.PutFile \
    C:/Temp/afile.jar \
    hdfs://bigpie1:9000/user/minsky/bfile.jar

# Linux/Mac 경로 예시
java -cp target/hadoop.demo-0.0.1-SNAPSHOT.jar \
    bigdata.hadoop.demo.PutFile \
    /tmp/local_file.txt \
    hdfs://bigpie1:9000/user/bigdata/remote_file.txt
```

**주의사항:**

- 첫 번째 인자: 로컬 파일 시스템의 파일 경로
- 두 번째 인자: HDFS에 저장할 전체 경로 (프로토콜 포함)
- 업로드 진행 상황은 콘솔에 `.`로 표시됩니다

### 4. FileSystemAccess

FileSystem API를 사용하여 HDFS 파일에 접근하는 예제입니다.

**파일 위치**: `examples/src/main/java/bigdata/hadoop/demo/FileSystemAccess.java`

**실행 방법:**

```bash
# 전체 HDFS URI 또는 경로만 전달 가능
java -cp target/hadoop.demo-0.0.1-SNAPSHOT.jar \
    bigdata.hadoop.demo.FileSystemAccess \
    hdfs://bigpie1:9000/user/bigdata/input/README.txt

# 또는 경로만 전달 (코드에서 fs.defaultFS 사용)
java -cp target/hadoop.demo-0.0.1-SNAPSHOT.jar \
    bigdata.hadoop.demo.FileSystemAccess \
    /user/bigdata/input/README.txt
```

**Eclipse에서 실행:**

1. `Run As → Run Configurations...`
2. `Arguments` 탭에서 `Program arguments` 입력: `/user/bigdata/input/README.txt`
3. 실행

---

## 실행 방법

### 1. 기본 WordCount 예제 (Hadoop 제공)

Hadoop이 제공하는 예제 JAR를 사용할 수 있습니다:

```bash
# 예제 목록 확인
$HADOOP_HOME/bin/hadoop jar \
    $HADOOP_HOME/share/hadoop/mapreduce/hadoop-mapreduce-examples-3.4.1.jar

# WordCount 실행
$HADOOP_HOME/bin/hadoop jar \
    $HADOOP_HOME/share/hadoop/mapreduce/hadoop-mapreduce-examples-3.4.1.jar \
    wordcount /wordcount/input /wordcount/output
```

### 2. 커스텀 MapReduce 프로그램 실행

**Maven 프로젝트 빌드:**

```bash
cd examples
mvn clean package
```

**JAR 파일 실행:**

```bash
# Single-Node Cluster
$HADOOP_HOME/bin/hadoop jar \
    target/hadoop.demo-0.0.1-SNAPSHOT.jar \
    bigdata.hadoop.demo.WordCount \
    /wordcount/input /wordcount/output

# Multi-Node Cluster
$HADOOP_HOME/bin/hadoop jar \
    target/hadoop.demo-0.0.1-SNAPSHOT.jar \
    bigdata.hadoop.demo.WordCount \
    /wordcount/input /wordcount/output

# 또는 간단하게 (메인 클래스가 지정된 경우)
hadoop jar wc_v2.jar input result
```

### 3. Eclipse에서 Runnable JAR 생성 및 배포

**Runnable JAR 파일 생성:**

1. **프로젝트 우클릭 → Export → Java → Runnable JAR file**
2. **Launch configuration**: 실행할 메인 클래스 선택 (예: `WordCount - hadoop.demo`)
3. **Export destination**: JAR 파일 저장 경로 지정 (예: `wc_v2.jar`)
4. **Library handling**: `Copy required libraries into a sub-folder next to the generated JAR` 선택
5. **Finish** 클릭

**SFTP를 통한 클러스터 배포:**

```bash
# SFTP로 bigpie1에 연결
sftp bigdata@bigpie1

# JAR 파일 전송
put wc_v2.jar

# 라이브러리 폴더 전송
put -r wc_v2_lib

# 종료
exit
```

**클러스터에서 실행:**

```bash
# bigpie1에 SSH 접속
ssh bigdata@bigpie1

# WordCount 실행
hadoop jar wc_v2.jar input result
```

### 4. 실행 결과 확인

**명령어를 통한 확인:**

```bash
# 출력 디렉토리 확인
hdfs dfs -ls /wordcount/output/

# 결과 파일 확인
hdfs dfs -cat /wordcount/output/part-r-00000

# _SUCCESS 파일 확인 (작업 성공 여부)
hdfs dfs -cat /wordcount/output/_SUCCESS
```

**웹 UI를 통한 확인:**

1. **NameNode 웹 UI**: `http://bigpie1:9870/`

   - HDFS 파일 시스템 브라우징
   - 출력 디렉토리 확인: `/user/bigdata/result`
   - `_SUCCESS` 파일과 `part-r-00000` 파일 확인
   - 파일 크기, 복제 수, 블록 크기 등 메타데이터 확인

2. **ResourceManager 웹 UI**: `http://bigpie1:8088/`

   - YARN 작업 상태 확인
   - 작업 이력 및 로그 확인
   - 리소스 사용량 모니터링

3. **JobHistory 웹 UI**: `http://bigpie1:19888/`
   - MapReduce 작업 이력 상세 확인
   - 작업 실행 시간, 태스크 정보 등

---

## Runtime Environment

### JobTracker와 TaskTracker

**Hadoop 1.x 아키텍처:**

```
Client
  ↓
JobTracker (NameNode)
  ↓
TaskTracker (DataNode)
  ├── Map Tasks
  └── Reduce Tasks
```

- **JobTracker**: 작업 스케줄링 및 관리
- **TaskTracker**: 실제 Map/Reduce 작업 실행

**Hadoop 2.x+ (YARN) 아키텍처:**

```
Client
  ↓
ResourceManager
  ↓
NodeManager
  ├── Map Tasks
  └── Reduce Tasks
```

- **ResourceManager**: 리소스 관리 및 스케줄링
- **NodeManager**: 컨테이너 관리 및 작업 실행

---

## 참고 자료

- [Apache Hadoop MapReduce Tutorial](https://hadoop.apache.org/docs/current/hadoop-mapreduce-client/hadoop-mapreduce-client-core/MapReduceTutorial.html)
- [Hadoop API Documentation](https://hadoop.apache.org/docs/current/api/)
- [Maven Repository - Hadoop](https://mvnrepository.com/artifact/org.apache.hadoop)

---

## 트러블슈팅

### 1. Native Library 경고

```
WARN util.NativeCodeLoader: Unable to load native-hadoop library
```

**해결 방법:** 이 경고는 무시해도 됩니다. Java 클래스를 사용하여 동작합니다.

### 2. Connection Timeout

```
java.net.ConnectException: Connection refused
```

**해결 방법:**

- HDFS 데몬이 실행 중인지 확인: `jps`
- `core-site.xml`의 `fs.defaultFS` 설정 확인
- 방화벽 설정 확인

### 3. 메모리 부족 오류

```
java.lang.OutOfMemoryError: Java heap space
```

**해결 방법:**

- `mapred-site.xml`에서 메모리 설정 증가
- `mapreduce.map.memory.mb`: 256 → 512
- `mapreduce.reduce.memory.mb`: 256 → 512

### 4. Staging Directory 생성 실패

```
Exception: staging dir/file creation failure
```

**원인:** YARN Application Master가 staging 디렉토리를 생성하지 못함

**해결 방법:**

`mapred-site.xml`에 다음 설정 추가:

```xml
<configuration>
    <!-- Job History 설정 -->
    <property>
        <name>mapreduce.jobhistory.address</name>
        <value>bigpie1:10020</value>
    </property>
    <property>
        <name>mapreduce.jobhistory.webapp.address</name>
        <value>bigpie1:19888</value>
    </property>

    <!-- Staging Directory 설정 (중요!) -->
    <property>
        <name>yarn.app.mapreduce.am.staging-dir</name>
        <value>/user/${user.name}/.staging</value>
    </property>

    <!-- YARN Application Master 리소스 설정 -->
    <property>
        <name>yarn.app.mapreduce.am.resource.mb</name>
        <value>512</value>
    </property>

    <!-- Map/Reduce 메모리 설정 -->
    <property>
        <name>mapreduce.map.memory.mb</name>
        <value>256</value>
    </property>
    <property>
        <name>mapreduce.reduce.memory.mb</name>
        <value>256</value>
    </property>

    <!-- MapReduce 클래스패스 설정 -->
    <property>
        <name>mapreduce.application.classpath</name>
        <value>/opt/hadoop/share/hadoop/mapreduce/*:/opt/hadoop/share/hadoop/mapreduce/lib/*</value>
    </property>
</configuration>
```

**추가 확인 사항:**

- 사용자 디렉토리가 HDFS에 존재하는지 확인: `hdfs dfs -ls /user/${user.name}`
- Staging 디렉토리 권한 확인: `hdfs dfs -chmod 755 /user/${user.name}/.staging`

---

## 다음 단계

1. **복잡한 MapReduce 작업 구현**

   - Secondary Sort
   - Join 연산
   - Aggregation

2. **성능 최적화**

   - Combiner 사용
   - Partitioner 커스터마이징
   - InputFormat/OutputFormat 커스터마이징

3. **고급 기능**
   - Counters 사용
   - DistributedCache 활용
   - Multiple Inputs/Outputs
