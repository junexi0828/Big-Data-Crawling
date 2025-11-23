# Kafka Streams 실습 프로젝트

Kafka Streams를 사용한 실시간 스트림 처리 애플리케이션 실습 프로젝트입니다.

## 📁 프로젝트 구조

```
kafka_streams/
├── README.md                    # 이 파일
├── pom.xml                     # Maven 프로젝트 설정
├── run.sh                      # 실행 스크립트
├── setup_topics.sh             # 토픽 생성 스크립트
├── start_kafka.sh              # Kafka 서버 시작 스크립트
└── src/main/java/bigdata/kstream/demo/
    ├── Util.java                # Streams 설정 유틸리티
    ├── SimplePipe.java          # 기본 스트림 파이프라인
    ├── ComplexPipe.java         # 복잡한 스트림 파이프라인
    ├── AccountBalanceTracker.java # KTable 예제
    ├── InvokeTransactions.java  # 트랜잭션 Producer
    ├── BalanceReader.java       # 잔액 Consumer
    └── QueryKTable.java         # KTable State Store 쿼리
```

## 🚀 빠른 시작

### 1. 사전 요구사항

- Java 8 이상
- Maven 3.x
- Kafka 서버 (localhost:9092에서 실행 중이어야 함)

### 2. Maven 프로젝트 빌드

```bash
cd kafka_project/kafka_streams
mvn clean compile
```

### 3. 토픽 생성

```bash
# 필요한 토픽 생성
./setup_topics.sh
```

생성되는 토픽:
- `bigdata`: 입력 토픽
- `analytics`: 출력 토픽
- `archive`: 아카이브 토픽
- `ebusiness`: 비즈니스 토픽
- `account`: 계정 트랜잭션 토픽
- `balance`: 계정 잔액 토픽

### 4. 예제 실행

#### SimplePipe (기본 스트림 파이프라인)
```bash
mvn exec:java -Dexec.mainClass="bigdata.kstream.demo.SimplePipe"
```

#### ComplexPipe (조건부 변환)
```bash
mvn exec:java -Dexec.mainClass="bigdata.kstream.demo.ComplexPipe"
```

#### AccountBalanceTracker (KTable 예제)
```bash
# 터미널 1: AccountBalanceTracker 실행
mvn exec:java -Dexec.mainClass="bigdata.kstream.demo.AccountBalanceTracker"

# 터미널 2: 트랜잭션 생성
mvn exec:java -Dexec.mainClass="bigdata.kstream.demo.InvokeTransactions"

# 터미널 3: 잔액 읽기
mvn exec:java -Dexec.mainClass="bigdata.kstream.demo.BalanceReader"
```

#### QueryKTable (State Store 쿼리)
```bash
# 터미널 1: AccountBalanceTracker 실행
mvn exec:java -Dexec.mainClass="bigdata.kstream.demo.AccountBalanceTracker"

# 터미널 2: 트랜잭션 생성
mvn exec:java -Dexec.mainClass="bigdata.kstream.demo.InvokeTransactions"

# 터미널 3: State Store 쿼리
mvn exec:java -Dexec.mainClass="bigdata.kstream.demo.QueryKTable"
```

## 📚 주요 클래스 설명

### Util.java
Kafka Streams 설정 Properties를 생성하는 유틸리티 클래스입니다.

**메서드:**
- `getStreamsProperties(String appID, String bootStrapServers)`: Streams 설정 Properties 생성

**설정 항목:**
- `APPLICATION_ID_CONFIG`: 애플리케이션 ID
- `BOOTSTRAP_SERVERS_CONFIG`: Kafka 브로커 주소
- `DEFAULT_KEY_SERDE_CLASS_CONFIG`: 기본 Key Serde (String)
- `DEFAULT_VALUE_SERDE_CLASS_CONFIG`: 기본 Value Serde (String)
- `AUTO_OFFSET_RESET_CONFIG`: "earliest"

### SimplePipe.java
기본 스트림 파이프라인 예제입니다.

**기능:**
- `bigdata` 토픽에서 읽기
- 메시지를 대문자로 변환 (`mapValues`)
- `analytics` 토픽에 쓰기

**학습 포인트:**
- KStream 생성
- Topology 정의
- ShutdownHook 등록

### ComplexPipe.java
조건부 변환 및 라우팅 예제입니다.

**기능:**
- `bigdata`, `ebusiness` 토픽에서 읽기
- 조건부 변환:
  - 길이 > 20: `toUpperCase()`
  - 길이 ≤ 20: `toLowerCase()`
- 모든 메시지를 `archive` 토픽에 쓰기
- 대문자 메시지만 `analytics` 토픽에 쓰기

**학습 포인트:**
- 다중 토픽 소스
- 조건부 변환 (`mapValues`)
- 필터링 및 라우팅 (`filter`)

### AccountBalanceTracker.java
KTable을 사용한 상태 관리 예제입니다.

**기능:**
- `account` 토픽에서 트랜잭션 읽기
- KStream → KTable 변환 (`groupByKey().aggregate()`)
- 계정별 잔액 집계
- `balance` 토픽에 잔액 쓰기

**학습 포인트:**
- KStream과 KTable의 차이
- Stateful 처리 (aggregation)
- Materialized State Store

### InvokeTransactions.java
트랜잭션 데이터를 생성하는 Producer입니다.

**기능:**
- 랜덤 트랜잭션 생성 (-10.0 ~ 20.0)
- 사용자 리스트 (bob, alice, john)
- `account` 토픽에 전송

### BalanceReader.java
계정 잔액을 읽는 Consumer입니다.

**기능:**
- `balance` 토픽에서 잔액 읽기
- Float 타입 역직렬화
- 메시지 출력 (Key, Value, Partition, Offset)

### QueryKTable.java
KTable의 State Store를 쿼리하는 예제입니다.

**기능:**
- `AccountBalanceStore` State Store 쿼리
- 모든 계정 잔액 조회
- `waitStore()` 헬퍼 메서드로 Store 준비 대기

**학습 포인트:**
- State Store 쿼리
- ReadOnlyKeyValueStore 사용
- Store 준비 상태 확인

## 🔧 Kafka Streams 개념

### Stateless vs Stateful

#### Stateless (SimplePipe, ComplexPipe)
- 각 레코드를 독립적으로 처리
- 이전 레코드 정보 불필요
- 예: `map`, `filter`, `branching`

#### Stateful (AccountBalanceTracker)
- 이전 레코드 정보 유지
- 내부 상태 관리
- 예: `aggregate`, `join`, `window`, `deduplication`

### KStream vs KTable

#### KStream
- 무한한 순서 있는 레코드 시퀀스
- 이벤트 로그
- 예: 클릭스트림 데이터

#### KTable
- 특정 키의 최신 상태
- 변경 로그 스트림
- 예: 사용자 프로필 테이블

### Topology
- 스트림 프로세서 그래프
- Source → Processors → Sink
- `StreamsBuilder`로 정의

## 📊 실행 흐름

### SimplePipe 실행 흐름
```
1. Kafka 서버 시작
2. 토픽 생성 (bigdata, analytics)
3. SimplePipe 실행
4. bigdata 토픽에 메시지 전송
5. analytics 토픽에서 변환된 메시지 확인
```

### AccountBalanceTracker 실행 흐름
```
1. Kafka 서버 시작
2. 토픽 생성 (account, balance)
3. AccountBalanceTracker 실행
4. InvokeTransactions 실행 (트랜잭션 생성)
5. BalanceReader 실행 (잔액 확인)
6. QueryKTable 실행 (State Store 쿼리)
```

## 🛠️ 유용한 명령어

### 토픽 확인
```bash
# 토픽 리스트
kafka-topics --list --bootstrap-server localhost:9092

# 토픽 상세 정보
kafka-topics --describe --topic bigdata --bootstrap-server localhost:9092
```

### 메시지 확인
```bash
# Consumer로 메시지 읽기
kafka-console-consumer --topic analytics --bootstrap-server localhost:9092 --from-beginning
```

### State Store 확인
```bash
# QueryKTable 실행 후 State Store 내용 확인
# QueryKTable 애플리케이션에서 직접 출력됨
```

## ⚠️ 주의사항

1. **애플리케이션 ID**: 각 Streams 애플리케이션은 고유한 `APPLICATION_ID`를 가져야 합니다.
2. **State Store**: State Store는 로컬에 저장되며, 애플리케이션 재시작 시 복구됩니다.
3. **토픽 생성**: 실행 전에 필요한 토픽을 미리 생성해야 합니다.
4. **ShutdownHook**: 애플리케이션 종료 시 `streams.close()`를 호출하여 안전하게 종료합니다.

## 🔗 관련 문서

- [Kafka 프로젝트 전체 가이드](../README.md)
- [Kafka Producer/Consumer 가이드](../kafka_demo/README.md)
- [Apache Kafka Streams 문서](https://kafka.apache.org/documentation/streams/)

## 📝 참고 자료

- **Stateless Operations**: `map`, `filter`, `branching`
- **Stateful Operations**: `aggregate`, `join`, `window`, `deduplication`
- **Topology**: Source Processors, Stream Processors, Sink Processors
- **State Management**: Materialized State Store, Changelog Topics
