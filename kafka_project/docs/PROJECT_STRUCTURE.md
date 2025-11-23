# Kafka 프로젝트 구조 상세 가이드

전체 프로젝트의 디렉토리 구조와 각 파일의 역할을 설명합니다.

## 📂 전체 디렉토리 구조

```
kafka_project/
│
├── 📄 README.md                          # 프로젝트 전체 개요 및 빠른 시작 가이드
│
├── 📁 docs/                              # 문서 디렉토리
│   ├── cluster_setup_guide.md           # 3-node 클러스터 설정 가이드
│   ├── WINDOWS_SINGLE_MACHINE_SETUP.md  # Windows 단일 머신 설정 가이드
│   ├── PROJECT_STRUCTURE.md             # 이 파일 (상세 구조 설명)
│   ├── KAFKA_TEST_RESULTS.md            # 기본 테스트 결과 문서
│   └── CLUSTER_TEST_RESULTS.md          # 클러스터 테스트 결과 문서
│
├── 📁 scripts/                           # 테스트 스크립트 디렉토리
│   ├── test_kafka.sh                    # 기본 Kafka 기능 테스트
│   ├── test_cluster_topics.sh           # 클러스터 환경에서 토픽 테스트
│   ├── test_producer_config.sh          # Producer 설정 테스트
│   ├── test_consumer_groups.sh          # Consumer Groups 테스트
│   ├── test_offset_management.sh        # Offset 관리 테스트
│   └── run_cluster_tests.sh             # 통합 테스트 스크립트
│
├── 📁 config/                            # Kafka 설정 파일
│   ├── server.properties.example        # 서버 설정 예제 (3-node 클러스터)
│   └── producer.properties              # Producer 설정 파일
│
├── 📁 kafka_demo/                        # Kafka Producer/Consumer 실습
│   │
│   ├── 📄 README.md                      # Producer/Consumer 가이드
│   ├── 📄 DEPLOYMENT.md                  # Runnable JAR 배포 가이드
│   ├── 📄 pom.xml                        # Maven 프로젝트 설정
│   ├── 📄 Producer.py                    # Python Producer 예제
│   ├── 📄 Consumer.py                    # Python Consumer 예제
│   │
│   └── 📁 src/main/java/bigdata/kafka/demo/
│       ├── Util.java                     # Producer/Consumer 설정 유틸리티
│       ├── Producer.java                 # 기본 Producer
│       ├── CallbackProducer.java         # Callback을 사용한 Producer
│       ├── KeyedCallbackProducer.java    # Key를 사용한 Producer
│       ├── Consumer.java                 # 기본 Consumer
│       └── PartitionedConsumer.java      # 특정 파티션에서 읽는 Consumer
│
└── 📁 kafka_streams/                     # Kafka Streams 실습
    │
    ├── 📄 README.md                       # Streams 가이드
    ├── 📄 pom.xml                         # Maven 프로젝트 설정
    ├── 📄 run.sh                          # 실행 스크립트
    ├── 📄 setup_topics.sh                 # 토픽 생성 스크립트
    ├── 📄 start_kafka.sh                  # Kafka 서버 시작 스크립트
    │
    └── 📁 src/main/java/bigdata/kstream/demo/
        ├── Util.java                      # Streams 설정 유틸리티
        ├── SimplePipe.java                # 기본 스트림 파이프라인
        ├── ComplexPipe.java               # 복잡한 스트림 파이프라인
        ├── AccountBalanceTracker.java      # KTable 예제
        ├── InvokeTransactions.java        # 트랜잭션 Producer
        ├── BalanceReader.java             # 잔액 Consumer
        └── QueryKTable.java               # KTable State Store 쿼리
```

## 📋 파일별 상세 설명

### 루트 디렉토리 문서

#### `README.md`
- 프로젝트 전체 개요
- 빠른 시작 가이드
- 주요 기능 요약
- 관련 문서 링크

### 문서 디렉토리 (`docs/`)

#### `cluster_setup_guide.md`
- 3-node Kafka 클러스터 설정 가이드
- KRaft Quorum 설정
- 각 노드별 server.properties 설정
- 클러스터 초기화 및 시작 절차

#### `WINDOWS_SINGLE_MACHINE_SETUP.md`
- Windows 단일 머신에서 Kafka 설정
- UUID 생성 및 로그 디렉토리 포맷
- 서버 시작 및 테스트
- Linux/Mac 단일 머신 설정도 포함

#### `PROJECT_STRUCTURE.md`
- 이 파일 (상세 프로젝트 구조 설명)
- 각 파일의 역할 및 설명
- 데이터 흐름 다이어그램

#### `KAFKA_TEST_RESULTS.md`
- 기본 Kafka 기능 테스트 결과
- Topic 생성/삭제 테스트
- Producer/Consumer 테스트 결과

#### `CLUSTER_TEST_RESULTS.md`
- 3-node 클러스터 테스트 결과
- 분산 환경에서의 동작 확인

### 테스트 스크립트 디렉토리 (`scripts/`)

#### `test_kafka.sh`
- 기본 Kafka 기능 테스트
- Topic 생성/삭제
- Producer/Consumer 테스트

#### `test_cluster_topics.sh`
- 클러스터 환경에서 토픽 테스트
- 파티션 및 복제 팩터 확인

#### `test_producer_config.sh`
- Producer 설정 테스트
- `producer.properties` 사용

#### `test_consumer_groups.sh`
- Consumer Groups 테스트
- 그룹별 메시지 분산 확인

#### `test_offset_management.sh`
- Offset 관리 테스트
- Offset 리셋 기능 확인

#### `run_cluster_tests.sh`
- 통합 테스트 스크립트
- 모든 테스트 실행

### 설정 파일 (`config/`)

#### `server.properties.example`
3-node 클러스터 설정 예제:
- Node 0 (bigpie2): 192.168.0.20
- Node 1 (bigpie3): 192.168.0.22
- Node 2 (bigpie4): 192.168.0.23

주요 설정:
- `process.roles=broker,controller`
- `node.id`: 각 노드별 고유 ID
- `controller.quorum.voters`: 모든 노드의 컨트롤러 정보
- `listeners`: PLAINTEXT 및 CONTROLLER 리스너
- `log.dirs`: 로그 디렉토리 경로

#### `producer.properties`
Producer 설정:
- `compression.type=gzip`: 압축 타입
- `partitioner.class=RoundRobinPartitioner`: 파티셔너 클래스
- `linger.ms=100`: 배치 전송 전 대기 시간
- `acks=all`: 모든 복제본 확인

### Kafka Producer/Consumer (`kafka_demo/`)

#### Java 클래스

**`Util.java`**
- `getProducerProperties(String bootStrapServer)`: Producer 설정 생성
- `getConsumerProperties(String bootStrapServer, String group)`: Consumer 설정 생성

**`Producer.java`**
- 기본 Producer 예제
- 메시지 전송 및 종료

**`CallbackProducer.java`**
- Callback을 사용한 비동기 Producer
- `onCompletion()` 메서드로 메타데이터 확인

**`KeyedCallbackProducer.java`**
- Key를 사용한 Producer
- 같은 Key는 같은 파티션으로 전송

**`Consumer.java`**
- 기본 Consumer 예제
- 토픽 구독 및 메시지 읽기
- try-catch-finally로 리소스 관리

**`PartitionedConsumer.java`**
- 특정 파티션에서 읽기
- `TopicPartition` 및 `assign()` 사용
- `seekToEnd()`, `seekToBeginning()` 지원

#### Python 스크립트

**`Producer.py`**
- `kafka-python` 라이브러리 사용
- Key, Value 전송
- `timeout=10` 설정
- try-except-finally 구조

**`Consumer.py`**
- `kafka-python` 라이브러리 사용
- Consumer Group 지원
- Key/Value 역직렬화 (UTF-8)
- `auto_offset_reset='earliest'`

#### 문서

**`README.md`**
- Producer/Consumer 가이드
- 실행 방법
- 주요 클래스 설명

**`DEPLOYMENT.md`**
- Runnable JAR 생성 방법
- Eclipse IDE Export 방법
- 원격 서버 배포 방법
- 실행 명령어

### Kafka Streams (`kafka_streams/`)

#### Java 클래스

**`Util.java`**
- `getStreamsProperties(String appID, String bootStrapServers)`: Streams 설정 생성
- 필수 StreamsConfig 속성 설정

**`SimplePipe.java`**
- 기본 스트림 파이프라인
- `bigdata` → `analytics` 토픽 전송
- `mapValues()`로 대문자 변환
- ShutdownHook 등록

**`ComplexPipe.java`**
- 조건부 변환 및 라우팅
- 다중 토픽 소스 (`bigdata`, `ebusiness`)
- 길이에 따른 대소문자 변환
- 조건부 필터링 및 라우팅

**`AccountBalanceTracker.java`**
- KStream → KTable 변환
- `groupByKey().aggregate()` 사용
- Materialized State Store
- KTable → KStream 변환

**`InvokeTransactions.java`**
- 트랜잭션 데이터 생성
- Float 타입 Producer
- 랜덤 트랜잭션 생성 (-10.0 ~ 20.0)
- 사용자 리스트 (bob, alice, john)

**`BalanceReader.java`**
- 계정 잔액 읽기
- Float 타입 Consumer
- `balance` 토픽 구독
- 메시지 출력

**`QueryKTable.java`**
- KTable State Store 쿼리
- `waitStore()` 헬퍼 메서드
- `ReadOnlyKeyValueStore` 사용
- 모든 계정 잔액 조회

#### 스크립트

**`setup_topics.sh`**
- 필요한 토픽 생성 스크립트
- `bigdata`, `analytics`, `archive`, `ebusiness`, `account`, `balance`

**`start_kafka.sh`**
- Kafka 서버 시작 스크립트

**`run.sh`**
- Streams 애플리케이션 실행 스크립트

#### 문서

**`README.md`**
- Streams 가이드
- 실행 방법
- 주요 클래스 설명
- Stateless vs Stateful 개념
- KStream vs KTable 개념

## 🔄 데이터 흐름

### Producer/Consumer 흐름
```
Producer → Kafka Topic → Consumer
```

### Streams 흐름
```
Source Topic → KStream → Processors → KStream/KTable → Sink Topic
```

### AccountBalanceTracker 흐름
```
InvokeTransactions → account topic → AccountBalanceTracker → balance topic → BalanceReader
                                                              ↓
                                                         State Store
                                                              ↓
                                                         QueryKTable
```

## 📦 Maven 의존성

### `kafka_demo/pom.xml`
- `kafka-clients` (4.0.0)
- `log4j-slf4j2-impl` (2.24.3)
- `jackson-databind` (2.19.0)
- `maven-shade-plugin` (Runnable JAR 생성)

### `kafka_streams/pom.xml`
- `kafka-streams` (4.0.0)

## 🎯 학습 경로

### 초급
1. `Producer.java` - 기본 메시지 전송
2. `Consumer.java` - 기본 메시지 수신
3. `SimplePipe.java` - 기본 스트림 처리

### 중급
1. `CallbackProducer.java` - 비동기 처리
2. `KeyedCallbackProducer.java` - Key 사용
3. `PartitionedConsumer.java` - 파티션 관리
4. `ComplexPipe.java` - 조건부 처리

### 고급
1. `AccountBalanceTracker.java` - Stateful 처리
2. `QueryKTable.java` - State Store 쿼리
3. 클러스터 설정 및 관리

## 🔗 관련 문서

- [프로젝트 전체 가이드](../README.md)
- [Producer/Consumer 가이드](../kafka_demo/README.md)
- [Streams 가이드](../kafka_streams/README.md)
- [클러스터 설정 가이드](cluster_setup_guide.md)
- [Windows 설정 가이드](WINDOWS_SINGLE_MACHINE_SETUP.md)
