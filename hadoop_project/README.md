# Hadoop 실습 프로젝트

Apache Hadoop 실습을 위한 프로젝트입니다. 강의 슬라이드를 기반으로 작성되었습니다.

## 📚 목차

1. [프로젝트 구조](#프로젝트-구조)
2. [개념 정리](#개념-정리)
3. [설정 가이드](#설정-가이드)
4. [실습 스크립트](#실습-스크립트)
5. [MapReduce 개발](#mapreduce-개발)
6. [빠른 시작](#빠른-시작)

---

## 프로젝트 구조

```
hadoop_project/
├── docs/                          # 문서
│   ├── HADOOP_CONCEPTS.md         # Hadoop 개념 정리
│   ├── SETUP_GUIDE.md            # 설정 가이드
│   └── MAPREDUCE_DEVELOPMENT.md  # MapReduce 개발 가이드
├── config/                        # 설정 파일 템플릿
│   ├── core-site.xml.example
│   ├── hdfs-site.xml.example
│   ├── mapred-site.xml.example
│   └── yarn-site.xml.example
├── scripts/                       # 실습 스크립트
│   ├── setup_local_mode.sh        # Local Mode 설정
│   ├── setup_single_node_wo_yarn.sh    # Single-Node (w/o YARN)
│   ├── setup_single_node_with_yarn.sh # Single-Node (with YARN)
│   ├── setup_multi_node_cluster.sh     # Multi-Node Cluster
│   └── run_wordcount_example.sh        # Wordcount 예제
├── examples/                      # MapReduce 예제 프로젝트
│   ├── pom.xml                    # Maven 프로젝트 설정
│   ├── src/
│   │   └── main/
│   │       ├── java/bigdata/hadoop/demo/
│   │       │   ├── WordCount.java
│   │       │   ├── URLAccess.java
│   │       │   ├── PutFile.java
│   │       │   └── FileSystemAccess.java
│   │       └── resources/
│   │           └── log4j.properties
│   └── README.md
├── deployment/                    # 배포 스크립트
│   ├── deploy_namenode.sh
│   ├── deploy_datanodes.sh
│   ├── deploy_all.sh
│   └── README.md
└── README.md                      # 이 파일
```

---

## 개념 정리

Hadoop의 핵심 개념과 아키텍처에 대한 자세한 설명은 다음 문서를 참고하세요:

📖 [HADOOP_CONCEPTS.md](docs/HADOOP_CONCEPTS.md)

주요 내용:

- Hadoop 개요 및 기원
- Hadoop Systems and Variants
- Apache Hadoop Architecture (Hadoop 1, 2, 3)
- Key Features and Advantages
- Hadoop's Core Components (HDFS, MapReduce, YARN)
- The Expanding Hadoop Ecosystem

---

## 설정 가이드

상세한 설정 가이드는 다음 문서를 참고하세요:

📖 [SETUP_GUIDE.md](docs/SETUP_GUIDE.md)

### 3가지 모드

| 모드                    | 설명                         | 용도               |
| ----------------------- | ---------------------------- | ------------------ |
| **Local (Standalone)**  | 단일 Java 프로세스로 실행    | 디버깅용           |
| **Single-Node Cluster** | 단일 머신에서 모든 데몬 실행 | 학습, 개발, 테스트 |
| **Multi-Node Cluster**  | 프로덕션급 분산 클러스터     | 프로덕션 환경      |

---

## 실습 스크립트

### 1. Local (Standalone) Mode

```bash
chmod +x scripts/setup_local_mode.sh
./scripts/setup_local_mode.sh
```

**특징:**

- 다운로드한 바이너리의 기본 설정 모드
- 단일 Java 프로세스로 실행
- 디버깅에 유용

### 2. Single-Node Cluster Mode (w/o YARN)

```bash
chmod +x scripts/setup_single_node_wo_yarn.sh
./scripts/setup_single_node_wo_yarn.sh
```

**특징:**

- NameNode, DataNode만 실행
- YARN 없이 HDFS만 사용
- 학습 및 개발에 이상적

### 3. Single-Node Cluster Mode (with YARN)

```bash
chmod +x scripts/setup_single_node_with_yarn.sh
./scripts/setup_single_node_with_yarn.sh
```

**특징:**

- YARN을 포함한 완전한 클러스터 모드
- ResourceManager, NodeManager 추가 실행
- MapReduce 작업 실행 가능

### 4. Multi-Node Cluster Mode

```bash
chmod +x scripts/setup_multi_node_cluster.sh
# 스크립트 내 변수 수정 후 실행
./scripts/setup_multi_node_cluster.sh
```

**특징:**

- 프로덕션급 분산 클러스터
- NameNode: bigpie1
- DataNode: bigpie2, bigpie3, bigpie4

**⚠️ 주의:** 스크립트 내 노드 IP 주소 및 호스트명을 실제 환경에 맞게 수정해야 합니다.

### 5. Wordcount 예제 실행

```bash
chmod +x scripts/run_wordcount_example.sh

# Local Mode
./scripts/run_wordcount_example.sh local

# HDFS Mode
./scripts/run_wordcount_example.sh
```

---

## MapReduce 개발

### 예제 프로젝트

Maven 기반의 MapReduce 개발 예제가 `examples/` 디렉토리에 포함되어 있습니다.

**주요 예제:**

1. **WordCount**: 단어 빈도 계산 MapReduce 프로그램
2. **URLAccess**: URL을 통한 HDFS 파일 접근
3. **PutFile**: 로컬 파일을 HDFS에 업로드
4. **FileSystemAccess**: FileSystem API를 통한 HDFS 접근

**빠른 시작:**

```bash
# 1. 프로젝트 빌드
cd examples
mvn clean package

# 2. WordCount 실행
$HADOOP_HOME/bin/hadoop jar target/hadoop.demo-0.0.1-SNAPSHOT.jar \
    bigdata.hadoop.demo.WordCount \
    /wordcount/input /wordcount/output
```

**상세 가이드:**

📖 [MapReduce 개발 가이드](docs/MAPREDUCE_DEVELOPMENT.md) - MapReduce 개발 방법 및 예제 설명

📖 [예제 프로젝트 README](examples/README.md) - 예제 프로젝트 사용법

---

## 빠른 시작

### 사전 준비사항

1. **Java JDK 설치** (v8 이상 또는 v11 이상)

   ```bash
   # Ubuntu/Debian
   sudo apt install openjdk-8-jdk

   # macOS
   brew install openjdk@8
   ```

2. **SSH 설치** (Single-Node 및 Multi-Node 모드)
   ```bash
   sudo apt install ssh
   ```

### Local Mode 빠른 시작

```bash
# 1. 스크립트 실행
chmod +x scripts/setup_local_mode.sh
./scripts/setup_local_mode.sh

# 2. Wordcount 예제 실행
cd hadoop-3.4.1
mkdir input
echo "Hello Hadoop" > input/file01.txt
bin/hadoop jar share/hadoop/mapreduce/hadoop-mapreduce-examples-3.4.1.jar wordcount input output
cat output/part-r-00000
```

### Single-Node Cluster Mode 빠른 시작

```bash
# 1. 스크립트 실행
chmod +x scripts/setup_single_node_wo_yarn.sh
./scripts/setup_single_node_wo_yarn.sh

# 2. 데몬 시작
cd hadoop-3.4.1
sbin/start-dfs.sh

# 3. 웹 인터페이스 확인
# 브라우저에서 http://localhost:9870/ 접속

# 4. HDFS 사용
bin/hdfs dfs -mkdir -p /user/$(whoami)/input
bin/hdfs dfs -put *.txt input
bin/hadoop jar share/hadoop/mapreduce/hadoop-mapreduce-examples-3.4.1.jar wordcount input output
bin/hdfs dfs -cat output/*
```

---

## 설정 파일 템플릿

`config/` 디렉토리에 각 모드별 설정 파일 템플릿이 있습니다:

- `core-site.xml.example`: 파일시스템 기본 설정
- `hdfs-site.xml.example`: HDFS 설정
- `mapred-site.xml.example`: MapReduce 설정
- `yarn-site.xml.example`: YARN 설정

사용 방법:

1. 예제 파일을 `$HADOOP_HOME/etc/hadoop/`로 복사
2. 파일명에서 `.example` 제거
3. 환경에 맞게 수정

---

## 웹 인터페이스

### NameNode 웹 UI

- **URL**: `http://localhost:9870/` (Single-Node)
- **URL**: `http://bigpie1:9870/` (Multi-Node)
- **기능**: HDFS 파일시스템 상태 확인

### ResourceManager 웹 UI (YARN 모드)

- **URL**: `http://localhost:8088/` (Single-Node)
- **URL**: `http://bigpie1:8088/` (Multi-Node)
- **기능**: YARN 리소스 관리 상태 확인

### JobHistory 웹 UI (Multi-Node)

- **URL**: `http://bigpie1:19888/`
- **기능**: MapReduce 작업 이력 확인

---

## 트러블슈팅

### Java heap space 오류

`mapred-site.xml`에서 메모리 크기 증가:

- `mapreduce.map.memory.mb`: 256 → 384 → 512
- `mapreduce.reduce.memory.mb`: 256 → 384 → 512

### SSH 연결 문제

```bash
chmod 0600 ~/.ssh/authorized_keys
ssh -v localhost  # 디버깅
```

### 데몬이 시작되지 않음

```bash
# 로그 확인
tail -f $HADOOP_HOME/logs/*.log

# 포트 충돌 확인
netstat -tulpn | grep 9000
```

---

## 노드별 준비 상태 및 배포

### 현재 구조

**로컬 개발** (`hadoop_project` 폴더):

- 설정 스크립트 및 템플릿 관리
- 로컬 테스트용 (Local Mode, Single-Node Mode)

**실제 클러스터 배포**:

- 각 노드에 파일을 배포하는 스크립트 제공
- 암호화폐 클러스터 프로젝트와 유사한 방식

### 배포 방법

1. **NameNode 배포**: `deployment/deploy_namenode.sh`
2. **DataNode 배포**: `deployment/deploy_datanodes.sh`
3. **전체 배포**: `deployment/deploy_all.sh`

자세한 내용은 [배포 가이드](deployment/README.md)와 [노드별 준비 상태](docs/NODE_PREPARATION.md)를 참조하세요.

## 참고 자료

- [Apache Hadoop 공식 문서](https://hadoop.apache.org/docs/current/)
- [Hadoop 설정 가이드](https://hadoop.apache.org/docs/current/hadoop-project-dist/hadoop-common/SingleCluster.html)
- [Hadoop Ecosystem](www.turing.com/kb/hadoop-ecosystem-and-hadoop-components-for-big-data-problems)

---

## 라이선스

이 프로젝트는 교육 목적으로 작성되었습니다.
