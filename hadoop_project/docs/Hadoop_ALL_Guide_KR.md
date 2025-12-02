# Apache Hadoop 완벽 설명서

## 목차
1. Hadoop의 역할
2. Hadoop 동작 원리
3. Hadoop의 핵심 컴포넌트
4. Hadoop 설치 및 실행
5. MapReduce 프로그래밍 모델
6. 실습 예제

---

## 1. Hadoop의 역할

### Hadoop이란?
Hadoop은 대규모 데이터를 **분산 저장**하고 **병렬 처리**하기 위한 오픈소스 프레임워크입니다. Google의 GFS(Google File System)와 MapReduce 논문(2004년)을 기반으로 2006년 Doug Cutting에 의해 개발되었으며, 테라바이트~페타바이트 규모의 데이터를 저가의 x86 서버 클러스터로 처리할 수 있습니다.

### Hadoop이 해결하는 문제
전통적인 데이터베이스는 한 대의 컴퓨터에서 처리하므로:
- **데이터 크기 제한**: 물리적 저장 용량 초과 시 처리 불가
- **처리 속도 한계**: 대용량 데이터 분석에 시간이 너무 오래 걸림
- **장애에 취약**: 서버 장애 시 모든 데이터 손실 위험

Hadoop은 이러한 문제를 다음과 같이 해결합니다:
- **분산 저장(HDFS)**: 데이터를 여러 노드에 나누어 저장
- **병렬 처리(MapReduce/YARN)**: 데이터가 있는 곳에서 직접 처리
- **장애 복구**: 데이터 복제로 노드 장애 대응

---

## 2. Hadoop 동작 원리

### Hadoop의 핵심 아키텍처

Hadoop은 **저장**과 **처리** 두 가지 계층으로 구분됩니다:

```
┌─────────────────────────────────────────────┐
│  YARN (Yet Another Resource Negotiator)     │
│  - 리소스 관리 및 작업 스케줄링               │
│  - MapReduce, Spark 등 다양한 엔진 지원      │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│  HDFS (Hadoop Distributed File System)      │
│  - 분산 파일 시스템 (저장계층)                │
│  - NameNode: 메타데이터 관리                  │
│  - DataNode: 실제 데이터 저장                │
└─────────────────────────────────────────────┘
```

### 데이터 읽기 흐름

1. **클라이언트** → HDFS에 파일 읽기 요청
2. **NameNode** → 파일의 블록 위치 정보 제공
3. **클라이언트** → 가장 가까운 DataNode에서 블록 읽기 (Data Locality)
4. **DataNode** → 실제 데이터 전송

### 데이터 쓰기 흐름

1. **클라이언트** → HDFS에 파일 쓰기 요청
2. **NameNode** → 새 파일 생성, 메타데이터 기록
3. **클라이언트** → 첫 번째 DataNode에 데이터 블록 쓰기
4. **첫 번째 DataNode** → 두 번째 DataNode로 복제 (Replication)
5. **두 번째 DataNode** → 세 번째 DataNode로 복제 (기본 복제 계수: 3)

---

## 3. Hadoop의 핵심 컴포넌트

### 3.1 HDFS (분산 파일 시스템)

#### HDFS의 특성

| 특성 | 설명 |
|------|------|
| **Master-Slave 아키텍처** | NameNode(1개)가 메타데이터 관리, DataNode(다수)가 데이터 저장 |
| **블록 기반 저장** | 파일을 128MB 또는 256MB 크기의 블록으로 분할 |
| **복제 기반 장애 복구** | 각 블록을 3개 이상으로 복제하여 높은 가용성 확보 |
| **Write-Once-Read-Many (WORM)** | 파일 쓰기 후 수정 불가, 읽기만 가능 (대용량 순차 읽기에 최적화) |
| **Data Locality** | 계산 코드가 데이터가 있는 노드로 이동 |

#### NameNode vs DataNode

**NameNode (메타데이터 관리)**
- 파일 시스템의 네임스페이스 유지
- 파일 시스템 트리 및 모든 파일/디렉토리 메타데이터 관리
- 블록 매핑 정보 보유
- 단일 장애점(Single Point of Failure) → Secondary NameNode 또는 HA 설정으로 보완

**DataNode (데이터 저장)**
- 실제 데이터 블록 저장
- 주기적으로 NameNode에 하트비트(Heartbeat) 전송 (3초 마다)
- 저장 중인 블록 리포트 전송

### 3.2 MapReduce (처리 엔진)

MapReduce는 **분산 처리를 위한 프로그래밍 모델**입니다.

#### 핵심 개념: Map과 Reduce

```
입력 데이터
   ↓
[Splitting] - 데이터를 여러 조각으로 분할
   ↓
[Mapping] - 각 조각을 (Key, Value) 쌍으로 변환
   ↓
[Shuffling & Sorting] - 같은 Key끼리 그룹화
   ↓
[Reducing] - 같은 Key의 Value들을 집계
   ↓
최종 결과
```

#### WordCount 예제 흐름

입력 텍스트:
```
"Hadoop Hadoop Spark"
"Spark Hadoop"
```

**Map Phase (매핑)**
```
Hadoop → (Hadoop, 1)
Hadoop → (Hadoop, 1)
Spark → (Spark, 1)
Spark → (Spark, 1)
Hadoop → (Hadoop, 1)
```

**Shuffle & Sort Phase (같은 키 그룹화)**
```
(Hadoop, [1, 1, 1])
(Spark, [1, 1])
```

**Reduce Phase (집계)**
```
(Hadoop, 3)
(Spark, 2)
```

### 3.3 YARN (리소스 관리)

Hadoop 2.x부터 도입된 **클러스터 리소스 관리 시스템**

| 컴포넌트 | 역할 |
|---------|------|
| **ResourceManager** | 클러스터 전체 리소스 관리, 애플리케이션 스케줄링 |
| **NodeManager** | 각 노드의 리소스 사용량 모니터링, 컨테이너 관리 |
| **ApplicationMaster** | 특정 애플리케이션의 리소스 요청 및 작업 관리 |

---

## 4. Hadoop 설치 및 실행

### 4.1 설치 전 요구사항

- **Java**: JDK 8 이상 (openjdk-8 또는 openjdk-11)
- **OS**: Linux (Ubuntu, CentOS 등) 또는 WSL2 (Windows)
- **네트워크**: SSH 접속 가능 환경

### 4.2 환경 설정

#### Step 1: Java 설치
```bash
# Ubuntu의 경우
sudo apt update
sudo apt install openjdk-11-jdk

# Java 경로 확인
which java
# /usr/bin/java → 실제 위치: /usr/lib/jvm/java-11-openjdk-amd64
```

#### Step 2: Hadoop 다운로드
```bash
cd ~
wget https://dlcdn.apache.org/hadoop/common/hadoop-3.4.1/hadoop-3.4.1.tar.gz
tar -zxvf hadoop-3.4.1.tar.gz
mv hadoop-3.4.1 hadoop
```

#### Step 3: 환경변수 설정
```bash
# ~/.bashrc 또는 ~/.profile 수정
export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
export HADOOP_HOME=$HOME/hadoop
export PATH=$PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin

# 적용
source ~/.bashrc

# 확인
hadoop version
```

### 4.3 Hadoop 실행 모드

#### 모드 1: 로컬(Local) 모드
**특징**: 단일 JVM에서 실행, 디버깅 용도
```bash
# 입력 디렉토리 생성
mkdir input

# 샘플 파일 생성
echo "Hello Hadoop" > input/file1.txt
echo "Hadoop is great" > input/file2.txt

# WordCount 실행
hadoop jar $HADOOP_HOME/share/hadoop/mapreduce/hadoop-mapreduce-examples-3.4.1.jar \
  wordcount input output

# 결과 확인
cat output/part-r-00000
```

**출력 예시**:
```
Hadoop 2
Hello 1
is 1
great 1
```

#### 모드 2: 의사 분산(Pseudo-Distributed) 모드
**특징**: 단일 노드에서 HDFS와 YARN 실행

**Step 1: SSH 설정**
```bash
# SSH 키 생성
ssh-keygen -t rsa -P "" -f ~/.ssh/id_rsa

# 공개키를 authorized_keys에 추가
cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys
chmod 0600 ~/.ssh/authorized_keys

# 로컬호스트 SSH 테스트
ssh localhost
```

**Step 2: Hadoop 설정**

`~/hadoop/etc/hadoop/core-site.xml` 수정:
```xml
<configuration>
    <property>
        <name>fs.defaultFS</name>
        <value>hdfs://localhost:9000</value>
    </property>
</configuration>
```

`~/hadoop/etc/hadoop/hdfs-site.xml` 수정:
```xml
<configuration>
    <property>
        <name>dfs.replication</name>
        <value>1</value>
    </property>
    <property>
        <name>dfs.namenode.name.dir</name>
        <value>/home/user/hadoop_data/namenode</value>
    </property>
    <property>
        <name>dfs.datanode.data.dir</name>
        <value>/home/user/hadoop_data/datanode</value>
    </property>
</configuration>
```

`~/hadoop/etc/hadoop/mapred-site.xml` 수정:
```xml
<configuration>
    <property>
        <name>mapreduce.framework.name</name>
        <value>yarn</value>
    </property>
</configuration>
```

`~/hadoop/etc/hadoop/yarn-site.xml` 수정:
```xml
<configuration>
    <property>
        <name>yarn.resourcemanager.hostname</name>
        <value>localhost</value>
    </property>
    <property>
        <name>yarn.nodemanager.aux-services</name>
        <value>mapreduce_shuffle</value>
    </property>
</configuration>
```

**Step 3: NameNode 포맷 및 시작**
```bash
# NameNode 포맷 (최초 1회만)
hdfs namenode -format -force

# HDFS 데몬 시작
start-dfs.sh

# YARN 데몬 시작
start-yarn.sh

# 실행 중인 Java 프로세스 확인
jps
# NameNode
# DataNode
# ResourceManager
# NodeManager
# SecondaryNameNode
```

**Step 4: HDFS 작업 디렉토리 생성**
```bash
# 입력 디렉토리 생성
hdfs dfs -mkdir -p /user/bigdata/input

# 디렉토리 확인
hdfs dfs -ls /

# 로컬 파일을 HDFS에 업로드
echo "Hello Hadoop World" > file1.txt
hdfs dfs -put file1.txt /user/bigdata/input/

# HDFS에서 파일 확인
hdfs dfs -ls /user/bigdata/input
```

**Step 5: WordCount 실행**
```bash
# MapReduce 작업 실행
hadoop jar $HADOOP_HOME/share/hadoop/mapreduce/hadoop-mapreduce-examples-3.4.1.jar \
  wordcount /user/bigdata/input /user/bigdata/output

# 결과 확인
hdfs dfs -cat /user/bigdata/output/part-r-00000

# 결과를 로컬로 다운로드
hdfs dfs -get /user/bigdata/output ./output_result
cat output_result/part-r-00000
```

**Step 6: 웹 인터페이스 확인**

브라우저에서 다음 주소 접속:
- NameNode: http://localhost:9870/
- ResourceManager: http://localhost:8088/

**Step 7: 데몬 종료**
```bash
stop-yarn.sh
stop-dfs.sh
```

#### 모드 3: 완전 분산(Fully-Distributed) 모드
**특징**: 여러 노드에서 클러스터 구성

필수 조건:
- 3개 이상의 Linux 서버 필요
- 모든 서버 간 SSH 접속 가능
- IP 주소 및 호스트명 설정

**기본 구조**:
```
NameNode (bigpie1)
  ├── DataNode (bigpie2)
  ├── DataNode (bigpie3)
  └── DataNode (bigpie4)
```

**설정 파일 예시 (core-site.xml)**:
```xml
<configuration>
    <property>
        <name>fs.defaultFS</name>
        <value>hdfs://bigpie1:9000</value>
    </property>
</configuration>
```

---

## 5. MapReduce 프로그래밍

### 5.1 Java 기반 MapReduce 개발

#### Mapper 클래스 작성
```java
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.io.IntWritable;
import java.io.IOException;
import java.util.StringTokenizer;

public class WordCountMapper extends Mapper<Object, Text, Text, IntWritable> {
    private final static IntWritable one = new IntWritable(1);
    private Text word = new Text();

    @Override
    protected void map(Object key, Text value, Context context) 
            throws IOException, InterruptedException {
        StringTokenizer itr = new StringTokenizer(value.toString());
        while (itr.hasMoreTokens()) {
            word.set(itr.nextToken());
            context.write(word, one);
        }
    }
}
```

**코드 설명**:
- `map()` 메서드: 각 줄(value)을 단어로 분할하여 (단어, 1) 쌍 생성
- `context.write()`: Shuffle 단계로 데이터 전달

#### Reducer 클래스 작성
```java
import org.apache.hadoop.mapreduce.Reducer;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.io.IntWritable;
import java.io.IOException;

public class WordCountReducer extends Reducer<Text, IntWritable, Text, IntWritable> {
    private IntWritable result = new IntWritable();

    @Override
    protected void reduce(Text key, Iterable<IntWritable> values, Context context)
            throws IOException, InterruptedException {
        int sum = 0;
        for (IntWritable val : values) {
            sum += val.get();
        }
        result.set(sum);
        context.write(key, result);
    }
}
```

**코드 설명**:
- `reduce()` 메서드: 같은 단어의 모든 1을 합산
- 최종 결과: (단어, 총 개수)

#### Driver 클래스 작성
```java
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;

public class WordCount {
    public static void main(String[] args) throws Exception {
        Configuration conf = new Configuration();
        
        // Hadoop 클러스터 설정 (의사 분산 모드)
        conf.set("fs.defaultFS", "hdfs://localhost:9000");
        conf.set("mapreduce.framework.name", "yarn");
        conf.set("yarn.resourcemanager.hostname", "localhost");
        
        // Job 생성
        Job job = Job.getInstance(conf, "Word Count");
        job.setJarByClass(WordCount.class);
        
        // Mapper, Reducer 클래스 지정
        job.setMapperClass(WordCountMapper.class);
        job.setReducerClass(WordCountReducer.class);
        
        // 출력 타입 지정
        job.setOutputKeyClass(Text.class);
        job.setOutputValueClass(IntWritable.class);
        
        // 입력 및 출력 경로
        FileInputFormat.addInputPath(job, new Path(args[0]));
        FileOutputFormat.setOutputPath(job, new Path(args[1]));
        
        // 작업 실행
        System.exit(job.waitForCompletion(true) ? 0 : 1);
    }
}
```

#### JAR 파일 생성 및 실행
```bash
# Java 파일 컴파일
javac -classpath $HADOOP_HOME/share/hadoop/common/* \
    -d . WordCountMapper.java WordCountReducer.java WordCount.java

# JAR 파일 생성
jar cvf wordcount.jar *.class

# Hadoop에서 실행
hadoop jar wordcount.jar WordCount /user/bigdata/input /user/bigdata/output
```

### 5.2 Python 기반 Streaming

Hadoop Streaming을 사용하면 Python으로도 MapReduce 개발 가능합니다.

#### Python Mapper
```python
#!/usr/bin/env python
import sys

for line in sys.stdin:
    words = line.strip().split()
    for word in words:
        print(f"{word}\t1")
```

#### Python Reducer
```python
#!/usr/bin/env python
import sys

current_word = None
current_count = 0

for line in sys.stdin:
    word, count = line.strip().split('\t')
    count = int(count)
    
    if word == current_word:
        current_count += count
    else:
        if current_word:
            print(f"{current_word}\t{current_count}")
        current_word = word
        current_count = count

if current_word:
    print(f"{current_word}\t{current_count}")
```

#### 실행 방법
```bash
# 파일 권한 설정
chmod +x mapper.py reducer.py

# 입력 데이터 준비
echo -e "Hello Hadoop\nHadoop is great\nHello world" > input.txt
hdfs dfs -put input.txt /user/bigdata/input/

# Streaming 작업 실행
hadoop jar $HADOOP_HOME/share/hadoop/tools/lib/hadoop-streaming-3.4.1.jar \
  -input /user/bigdata/input/input.txt \
  -output /user/bigdata/output \
  -mapper mapper.py \
  -reducer reducer.py

# 결과 확인
hdfs dfs -cat /user/bigdata/output/part-00000
```

---

## 6. 실습 예제

### 예제 1: 로컬 모드에서 기본 WordCount 실행

```bash
# 1. 입력 파일 준비
mkdir hadoop_input
cd hadoop_input

cat > file1.txt << EOF
Apache Hadoop is a framework for distributed computing
Hadoop provides scalability and fault tolerance
Distributed computing with Hadoop
EOF

cat > file2.txt << EOF
Hadoop ecosystem includes MapReduce
MapReduce is used for batch processing
Big Data processing with Hadoop
EOF

cd ..

# 2. WordCount 예제 실행
hadoop jar $HADOOP_HOME/share/hadoop/mapreduce/hadoop-mapreduce-examples-3.4.1.jar \
  wordcount hadoop_input hadoop_output

# 3. 결과 확인
cat hadoop_output/part-r-00000
```

**예상 출력**:
```
Apache 1
Big 1
Data 2
Distributed 2
Hadoop 4
MapReduce 2
...
```

### 예제 2: HDFS에 데이터 업로드 및 처리

```bash
# 1. HDFS 디렉토리 생성
hdfs dfs -mkdir -p /wordcount/input

# 2. 로컬 파일을 HDFS에 업로드
hdfs dfs -put hadoop_input/* /wordcount/input/

# 3. HDFS에서 파일 확인
hdfs dfs -ls -R /wordcount/

# 4. WordCount 실행
hadoop jar $HADOOP_HOME/share/hadoop/mapreduce/hadoop-mapreduce-examples-3.4.1.jar \
  wordcount /wordcount/input /wordcount/output

# 5. 결과 확인
hdfs dfs -cat /wordcount/output/part-r-00000

# 6. 결과를 로컬로 다운로드
hdfs dfs -get /wordcount/output local_output
cat local_output/part-r-00000
```

### 예제 3: 의사 분산 모드에서 멀티노드 흉내내기

```bash
# 1. 현재 상태 확인
jps

# 2. MapReduce 작업 모니터링
# ResourceManager 웹 UI 접속: http://localhost:8088/
# 실시간 작업 진행 상황 확인 가능

# 3. 작업 로그 확인
yarn logs -applicationId application_<id>_<id>

# 4. 전체 워크플로우
echo "test file for mapreduce" > test.txt
hdfs dfs -put test.txt /user/bigdata/input/

hadoop jar $HADOOP_HOME/share/hadoop/mapreduce/hadoop-mapreduce-examples-3.4.1.jar \
  wordcount /user/bigdata/input /user/bigdata/output

hdfs dfs -cat /user/bigdata/output/*
```

---

## 7. 주요 HDFS 명령어

| 명령어 | 설명 | 예시 |
|--------|------|------|
| `hdfs dfs -ls` | 디렉토리 목록 | `hdfs dfs -ls /user` |
| `hdfs dfs -mkdir` | 디렉토리 생성 | `hdfs dfs -mkdir /test` |
| `hdfs dfs -put` | 로컬 → HDFS | `hdfs dfs -put local.txt /test/` |
| `hdfs dfs -get` | HDFS → 로컬 | `hdfs dfs -get /test/remote.txt .` |
| `hdfs dfs -cat` | 파일 내용 출력 | `hdfs dfs -cat /test/file.txt` |
| `hdfs dfs -rm` | 파일 삭제 | `hdfs dfs -rm /test/file.txt` |
| `hdfs dfs -du` | 디스크 사용량 | `hdfs dfs -du -h /` |
| `hdfs dfs -chmod` | 권한 변경 | `hdfs dfs -chmod 755 /test` |
| `hdfs dfsadmin -report` | 클러스터 상태 | 모든 DataNode 정보 표시 |

---

## 8. 트러블슈팅

### 문제 1: Java heap space 에러
```bash
# mapred-site.xml에서 메모리 증가
# mapreduce.map.memory.mb: 256 → 512
# mapreduce.reduce.memory.mb: 256 → 512
```

### 문제 2: NameNode 포맷 실패
```bash
# 기존 데이터 삭제 후 재포맷
rm -rf ~/hadoop_data/namenode/*
hdfs namenode -format -force
```

### 문제 3: DataNode 연결 불가
```bash
# SSH 연결 확인
ssh localhost

# 방화벽 포트 확인
netstat -tlnp | grep 9000  # NameNode 포트
netstat -tlnp | grep 50010 # DataNode 포트
```

---

## 9. Hadoop 에코시스템

| 도구 | 목적 |
|------|------|
| **Hive** | SQL을 MapReduce로 자동 변환 |
| **Pig** | 데이터 흐름 스크립트 언어 |
| **Spark** | 인메모리 분산 처리 (MapReduce 대체) |
| **HBase** | 열 기반 NoSQL 데이터베이스 |
| **Flume** | 로그 수집 및 스트리밍 |
| **Kafka** | 고성능 메시지 큐 |
| **Sqoop** | RDBMS ↔ HDFS 데이터 이동 |
| **ZooKeeper** | 분산 코디네이션 서비스 |

---

## 10. 요약

**Hadoop의 핵심:**
1. **HDFS**: 대용량 데이터 분산 저장
2. **MapReduce**: 데이터가 있는 곳에서 병렬 처리
3. **YARN**: 클러스터 리소스 관리
4. **복제**: 장애 복구

**실행 흐름:**
```
데이터 입력 (HDFS)
    ↓
Map Phase (데이터 → Key-Value)
    ↓
Shuffle & Sort (같은 Key 그룹화)
    ↓
Reduce Phase (집계)
    ↓
최종 결과 (HDFS 저장)
```

**학습 순서:**
1. 로컬 모드에서 기본 개념 학습
2. 의사 분산 모드에서 실습
3. Java/Python으로 MapReduce 개발
4. 완전 분산 모드 클러스터 구성