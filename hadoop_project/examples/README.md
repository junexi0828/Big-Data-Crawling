# MapReduce 예제 프로젝트

이 디렉토리는 Hadoop MapReduce 애플리케이션 개발 예제를 포함합니다.

## 📁 프로젝트 구조

```
examples/
├── pom.xml                                    # Maven 프로젝트 설정
├── src/
│   ├── main/
│   │   ├── java/
│   │   │   └── bigdata/hadoop/demo/
│   │   │       ├── WordCount.java            # WordCount MapReduce 프로그램
│   │   │       ├── URLAccess.java            # URL을 통한 HDFS 접근 예제
│   │   │       ├── PutFile.java              # 로컬 파일을 HDFS에 업로드
│   │   │       └── FileSystemAccess.java     # FileSystem API를 통한 HDFS 접근
│   │   └── resources/
│   │       └── log4j.properties              # Log4j 설정 파일
└── README.md                                  # 이 파일
```

## 🚀 빠른 시작

### 1. 프로젝트 빌드

```bash
cd examples
mvn clean package
```

빌드가 성공하면 `target/hadoop.demo-0.0.1-SNAPSHOT.jar` 파일이 생성됩니다.

### 2. WordCount 실행

```bash
# 입력 파일 준비
hdfs dfs -mkdir -p /wordcount/input
echo "Hello Hadoop Bye Bye" > file01.txt
echo "This is a test for mapreduce" >> file01.txt
echo "Hello Hadoop Bye Hadoop" > file02.txt
echo "This is another test for hadoop" >> file02.txt

# HDFS에 업로드
hdfs dfs -put file*.txt /wordcount/input

# WordCount 실행
$HADOOP_HOME/bin/hadoop jar target/hadoop.demo-0.0.1-SNAPSHOT.jar \
    bigdata.hadoop.demo.WordCount \
    /wordcount/input /wordcount/output

# 결과 확인
hdfs dfs -cat /wordcount/output/part-r-00000
```

## 📝 예제 프로그램 설명

### 1. WordCount

단어 빈도를 계산하는 MapReduce 프로그램입니다.

**클래스**: `bigdata.hadoop.demo.WordCount`

**사용법:**

```bash
hadoop jar hadoop.demo-0.0.1-SNAPSHOT.jar \
    bigdata.hadoop.demo.WordCount \
    <input_path> <output_path>
```

**예시:**

```bash
hadoop jar hadoop.demo-0.0.1-SNAPSHOT.jar \
    bigdata.hadoop.demo.WordCount \
    /wordcount/input /wordcount/output
```

### 2. URLAccess

URL을 통해 HDFS 파일에 접근하는 예제입니다.

**클래스**: `bigdata.hadoop.demo.URLAccess`

**사용법:**

```bash
java -cp target/hadoop.demo-0.0.1-SNAPSHOT.jar \
    bigdata.hadoop.demo.URLAccess \
    <hdfs_file_path>
```

**예시:**

```bash
# HDFS 파일 경로만 전달 (프로토콜과 서버는 코드에서 자동 추가)
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

**클래스**: `bigdata.hadoop.demo.PutFile`

**사용법:**

```bash
java -cp target/hadoop.demo-0.0.1-SNAPSHOT.jar \
    bigdata.hadoop.demo.PutFile \
    <local_file_path> <hdfs_file_path>
```

**예시:**

```bash
java -cp target/hadoop.demo-0.0.1-SNAPSHOT.jar \
    bigdata.hadoop.demo.PutFile \
    /path/to/local/file.txt \
    hdfs://bigpie1:9000/hdfs/path/file.txt
```

### 4. FileSystemAccess

FileSystem API를 사용하여 HDFS 파일에 접근하는 예제입니다.

**클래스**: `bigdata.hadoop.demo.FileSystemAccess`

**사용법:**

```bash
java -cp target/hadoop.demo-0.0.1-SNAPSHOT.jar \
    bigdata.hadoop.demo.FileSystemAccess \
    <hdfs_file_path>
```

**예시:**

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

## 🔧 개발 환경 설정

### Eclipse IDE에서 프로젝트 열기

1. **File → Import → Existing Maven Projects**
2. `examples` 디렉토리 선택
3. 프로젝트가 자동으로 빌드됩니다

### Eclipse에서 Runnable JAR 파일 생성

1. **프로젝트 우클릭 → Export → Java → Runnable JAR file**
2. **Launch configuration**: 실행할 메인 클래스 선택 (예: `WordCount - hadoop.demo`)
3. **Export destination**: JAR 파일 저장 경로 지정 (예: `wc_v2.jar`)
4. **Library handling**: `Copy required libraries into a sub-folder next to the generated JAR` 선택
   - 이렇게 하면 `wc_v2_lib` 폴더가 생성되어 필요한 라이브러리가 포함됩니다
5. **Finish** 클릭

### JAR 파일을 클러스터로 전송 (SFTP)

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

### 클러스터에서 실행

```bash
# bigpie1에 SSH 접속
ssh bigdata@bigpie1

# WordCount 실행
hadoop jar wc_v2.jar input result

# 또는 전체 클래스명 지정
hadoop jar wc_v2.jar bigdata.hadoop.demo.WordCount input result
```

### IntelliJ IDEA에서 프로젝트 열기

1. **File → Open**
2. `examples` 디렉토리 선택
3. Maven 프로젝트로 자동 인식됩니다

## 📚 상세 문서

자세한 개발 가이드는 다음 문서를 참고하세요:

- [MapReduce 개발 가이드](../docs/MAPREDUCE_DEVELOPMENT.md)

## 🌐 결과 확인 (HDFS 웹 UI)

MapReduce 작업 완료 후 웹 UI를 통해 결과를 확인할 수 있습니다:

1. **NameNode 웹 UI**: `http://bigpie1:9870/`

   - HDFS 파일 시스템 브라우징
   - 출력 디렉토리 확인: `/user/bigdata/result`
   - `_SUCCESS` 파일과 `part-r-00000` 파일 확인

2. **ResourceManager 웹 UI**: `http://bigpie1:8088/`
   - YARN 작업 상태 확인
   - 작업 이력 및 로그 확인

## ⚠️ 주의사항

1. **Hadoop 클러스터 실행 확인**

   - WordCount 실행 전에 HDFS와 YARN이 실행 중이어야 합니다
   - `jps` 명령어로 데몬 상태 확인

2. **설정 파일 확인**

   - `WordCount.java`의 `fs.defaultFS` 설정이 실제 클러스터와 일치해야 합니다
   - Single-Node: `hdfs://localhost:9000`
   - Multi-Node: `hdfs://bigpie1:9000`

3. **출력 디렉토리**

   - 출력 디렉토리는 존재하지 않아야 합니다 (자동 생성됨)
   - 기존 디렉토리가 있으면 오류 발생

4. **사용자 디렉토리 생성**
   - HDFS 접근을 위해 사용자 디렉토리를 생성해야 할 수 있습니다:
   ```bash
   hdfs dfs -mkdir -p /user/bigdata
   hdfs dfs -chown bigdata:supergroup /user/bigdata
   ```

## 🔗 관련 링크

- [Apache Hadoop MapReduce Tutorial](https://hadoop.apache.org/docs/current/hadoop-mapreduce-client/hadoop-mapreduce-client-core/MapReduceTutorial.html)
- [Hadoop API Documentation](https://hadoop.apache.org/docs/current/api/)
