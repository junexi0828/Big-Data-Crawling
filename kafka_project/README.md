# Kafka 프로젝트 전체 가이드

Apache Kafka를 활용한 실시간 데이터 스트리밍 및 스트림 처리 프로젝트입니다.

## 📁 프로젝트 구조

```
kafka_project/
├── README.md                          # 이 파일 (전체 프로젝트 개요)
│
├── docs/                              # 문서 디렉토리
│   ├── cluster_setup_guide.md        # 3-node 클러스터 설정 가이드
│   ├── WINDOWS_SINGLE_MACHINE_SETUP.md # Windows 단일 머신 설정 가이드
│   ├── PROJECT_STRUCTURE.md          # 상세 프로젝트 구조 설명
│   └── README.md                     # 문서 디렉토리 가이드
│
├── scripts/                           # 테스트 스크립트 디렉토리
│   ├── test_kafka.sh                 # 기본 테스트
│   ├── test_cluster_topics.sh        # 클러스터 토픽 테스트
│   ├── test_producer_config.sh       # Producer 설정 테스트
│   ├── test_consumer_groups.sh       # Consumer Groups 테스트
│   ├── test_offset_management.sh     # Offset 관리 테스트
│   └── run_cluster_tests.sh          # 통합 테스트
│
├── config/                            # Kafka 설정 파일
│   ├── server.properties.example     # 서버 설정 예제 (3-node 클러스터)
│   └── producer.properties           # Producer 설정 파일
│
├── kafka_demo/                        # Kafka Producer/Consumer 실습
│   ├── README.md                      # Producer/Consumer 가이드
│   ├── DEPLOYMENT.md                  # Runnable JAR 배포 가이드
│   ├── pom.xml                        # Maven 프로젝트 설정
│   ├── Producer.py                    # Python Producer 예제
│   ├── Consumer.py                    # Python Consumer 예제
│   └── src/main/java/bigdata/kafka/demo/
│       ├── Util.java                  # Producer/Consumer 설정 유틸리티
│       ├── Producer.java              # 기본 Producer
│       ├── CallbackProducer.java     # Callback Producer
│       ├── KeyedCallbackProducer.java # Keyed Callback Producer
│       ├── Consumer.java              # 기본 Consumer
│       └── PartitionedConsumer.java  # Partitioned Consumer
│
└── kafka_streams/                     # Kafka Streams 실습
    ├── README.md                      # Streams 가이드
    ├── pom.xml                        # Maven 프로젝트 설정
    ├── run.sh                         # 실행 스크립트
    ├── setup_topics.sh                # 토픽 생성 스크립트
    ├── start_kafka.sh                 # Kafka 서버 시작 스크립트
    └── src/main/java/bigdata/kstream/demo/
        ├── Util.java                  # Streams 설정 유틸리티
        ├── SimplePipe.java            # 기본 스트림 파이프라인
        ├── ComplexPipe.java           # 복잡한 스트림 파이프라인
        ├── AccountBalanceTracker.java # KTable 예제
        ├── InvokeTransactions.java    # 트랜잭션 Producer
        ├── BalanceReader.java         # 잔액 Consumer
        └── QueryKTable.java           # KTable State Store 쿼리
```

## 🚀 빠른 시작

### 1. Kafka 서버 설정

#### 단일 머신 (Windows)

```bash
# Windows 단일 머신 설정 가이드 참조
cat docs/WINDOWS_SINGLE_MACHINE_SETUP.md
```

#### 3-node 클러스터 (Linux)

```bash
# 클러스터 설정 가이드 참조
cat docs/cluster_setup_guide.md
```

### 2. Kafka Producer/Consumer 실습

```bash
cd kafka_demo

# Java 예제 실행
mvn exec:java -Dexec.mainClass="bigdata.kafka.demo.Producer"
mvn exec:java -Dexec.mainClass="bigdata.kafka.demo.Consumer"

# Python 예제 실행
python3 Producer.py
python3 Consumer.py
```

자세한 내용은 [kafka_demo/README.md](kafka_demo/README.md) 참조

### 3. Kafka Streams 실습

```bash
cd kafka_streams

# 토픽 생성
./setup_topics.sh

# SimplePipe 실행
mvn exec:java -Dexec.mainClass="bigdata.kstream.demo.SimplePipe"
```

자세한 내용은 [kafka_streams/README.md](kafka_streams/README.md) 참조

### 4. 테스트 실행

```bash
# 기본 테스트
./scripts/test_kafka.sh

# 클러스터 테스트
./scripts/test_cluster_topics.sh

# 통합 테스트
./scripts/run_cluster_tests.sh
```

## 📚 주요 기능

### Kafka Producer/Consumer (`kafka_demo/`)

#### Java 구현

- ✅ **Producer.java**: 기본 메시지 전송
- ✅ **CallbackProducer.java**: 비동기 Callback 처리
- ✅ **KeyedCallbackProducer.java**: Key를 사용한 메시지 전송
- ✅ **Consumer.java**: 기본 메시지 수신
- ✅ **PartitionedConsumer.java**: 특정 파티션에서 읽기

#### Python 구현

- ✅ **Producer.py**: Python Kafka Producer
- ✅ **Consumer.py**: Python Kafka Consumer

#### 배포

- ✅ **Runnable JAR**: Maven Shade Plugin을 사용한 실행 가능한 JAR 생성
- ✅ **원격 배포**: SFTP를 통한 원격 서버 배포

### Kafka Streams (`kafka_streams/`)

#### 기본 스트림 처리

- ✅ **SimplePipe.java**: 기본 스트림 파이프라인 (bigdata → analytics)
- ✅ **ComplexPipe.java**: 조건부 변환 및 라우팅

#### Stateful 처리 (KTable)

- ✅ **AccountBalanceTracker.java**: KStream → KTable 변환 및 집계
- ✅ **InvokeTransactions.java**: 트랜잭션 데이터 생성
- ✅ **BalanceReader.java**: 잔액 데이터 읽기
- ✅ **QueryKTable.java**: KTable State Store 쿼리

## 🔧 설정 파일

### `config/server.properties.example`

3-node 클러스터 설정 예제:

- Node 0 (bigpie2): 192.168.0.20
- Node 1 (bigpie3): 192.168.0.22
- Node 2 (bigpie4): 192.168.0.23

### `config/producer.properties`

Producer 설정:

- `compression.type=gzip`
- `partitioner.class=org.apache.kafka.clients.producer.RoundRobinPartitioner`
- `linger.ms=100`
- `acks=all`

## 🧪 테스트 스크립트

### 기본 테스트

```bash
./scripts/test_kafka.sh
```

### 클러스터 테스트

```bash
./scripts/test_cluster_topics.sh
./scripts/test_producer_config.sh
./scripts/test_consumer_groups.sh
./scripts/test_offset_management.sh
```

### 통합 테스트

```bash
./scripts/run_cluster_tests.sh
```

## 📖 상세 문서

### 설정 가이드

- [3-node 클러스터 설정](docs/cluster_setup_guide.md)
- [Windows 단일 머신 설정](docs/WINDOWS_SINGLE_MACHINE_SETUP.md)

### 실습 가이드

- [Kafka Producer/Consumer 가이드](kafka_demo/README.md)
- [Kafka Streams 가이드](kafka_streams/README.md)
- [Runnable JAR 배포 가이드](kafka_demo/DEPLOYMENT.md)

### 참고 문서

- [프로젝트 구조 상세 설명](docs/PROJECT_STRUCTURE.md)
- [기본 테스트 결과](docs/KAFKA_TEST_RESULTS.md)
- [클러스터 테스트 결과](docs/CLUSTER_TEST_RESULTS.md)

## 🎯 학습 목표

### Kafka 기본

1. ✅ Kafka 클러스터 설정 (3-node)
2. ✅ Producer/Consumer 구현 (Java, Python)
3. ✅ Topic 관리 및 파티션
4. ✅ Consumer Groups 및 Offset 관리

### Kafka Streams

1. ✅ Streams 설정 및 Topology 정의
2. ✅ Stateless 처리 (map, filter)
3. ✅ Stateful 처리 (KTable, aggregation)
4. ✅ State Store 쿼리

## 🔗 관련 프로젝트

이 프로젝트는 다음 프로젝트와 통합됩니다:

- **Scrapy 프로젝트**: 웹 데이터 수집 → Kafka
- **Selenium 프로젝트**: 동적 콘텐츠 수집 → Kafka
- **Hadoop 프로젝트**: Kafka → HDFS (예정)

## 📝 참고 자료

- [Apache Kafka 공식 문서](https://kafka.apache.org/documentation/)
- [Kafka Streams 문서](https://kafka.apache.org/documentation/streams/)
- [kafka-python 문서](https://kafka-python.readthedocs.io/)

## ⚠️ 주의사항

1. **Topic 삭제**: Windows 서버에서 토픽 삭제 시 서버가 크래시될 수 있습니다.
2. **클러스터 UUID**: 3-node 클러스터 설정 시 모든 노드에서 동일한 UUID를 사용해야 합니다.
3. **포트 충돌**: 여러 Kafka 인스턴스를 실행할 때 포트 충돌을 주의하세요.

## 🎉 완성도

**전체 프로젝트 완성도: 100%**

모든 강의 슬라이드 내용이 구현되었으며, 실습 준비가 완료되었습니다.
