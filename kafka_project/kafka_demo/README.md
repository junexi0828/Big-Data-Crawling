# Kafka Producer & Consumer 실습 프로젝트

강의 슬라이드를 기반으로 한 Kafka Producer와 Consumer 실습 프로젝트입니다.

## 📁 프로젝트 구조

```
kafka_demo/
├── pom.xml                          # Maven 프로젝트 설정
├── README.md                         # 이 파일
├── Producer.py                      # Python Producer 예제
├── Consumer.py                      # Python Consumer 예제
└── src/
    └── main/
        └── java/
            └── bigdata/
                └── kafka/
                    └── demo/
                        ├── Util.java                 # Producer/Consumer 설정 유틸리티
                        ├── Producer.java            # 기본 Producer
                        ├── CallbackProducer.java    # Callback을 사용한 Producer
                        ├── KeyedCallbackProducer.java  # Key를 사용한 Producer
                        ├── Consumer.java            # 기본 Consumer
                        └── PartitionedConsumer.java # 특정 파티션에서 읽는 Consumer
```

## 🚀 빠른 시작

### 1. 사전 요구사항

- **Java 8 이상**
- **Maven 3.x**
- **Kafka 서버** (localhost:9092에서 실행 중이어야 함)
- **Python 3.x** (Python 예제 사용 시)
- **kafka-python** (Python 예제 사용 시): `pip install kafka-python`

### 2. Maven 프로젝트 빌드

```bash
cd kafka_project/kafka_demo
mvn clean compile
```

### 3. Java 예제 실행

#### Producer 실행
```bash
# 기본 Producer
mvn exec:java -Dexec.mainClass="bigdata.kafka.demo.Producer"

# Callback Producer
mvn exec:java -Dexec.mainClass="bigdata.kafka.demo.CallbackProducer"

# Keyed Callback Producer
mvn exec:java -Dexec.mainClass="bigdata.kafka.demo.KeyedCallbackProducer"
```

#### Consumer 실행
```bash
# 기본 Consumer
mvn exec:java -Dexec.mainClass="bigdata.kafka.demo.Consumer"

# Partitioned Consumer
mvn exec:java -Dexec.mainClass="bigdata.kafka.demo.PartitionedConsumer"
```

### 4. Python 예제 실행

```bash
# Producer 실행
python3 Producer.py

# Consumer 실행
python3 Consumer.py
```

## 📚 주요 클래스 설명

### Util.java
Producer와 Consumer의 Properties를 생성하는 유틸리티 클래스입니다.

- `getProducerProperties(String bootStrapServers)`: Producer 설정 Properties 생성
- `getConsumerProperties(String bootStrapServers, String groupId)`: Consumer 설정 Properties 생성

### Producer.java
기본 Producer 예제입니다.

1. Producer Properties 생성
2. KafkaProducer 생성
3. 메시지 전송
4. Producer 종료

### CallbackProducer.java
Callback을 사용한 Producer 예제입니다.

- 메시지 전송 결과를 비동기로 처리
- 성공/실패 여부와 메타데이터(토픽, 파티션, 오프셋) 확인 가능

### KeyedCallbackProducer.java
Key를 사용한 Producer 예제입니다.

- `ProducerRecord<K, V>(String topic, K key, V value)` 형태로 메시지 전송
- 같은 키를 가진 메시지는 같은 파티션으로 전송됨
- Callback을 사용하여 전송 결과 확인

### Consumer.java
기본 Consumer 예제입니다.

1. Consumer Properties 생성
2. KafkaConsumer 생성
3. 토픽 구독 및 poll(...)을 사용하여 메시지 읽기
4. Consumer 종료

**참고**: 첫 실행과 두 번째 실행 비교
- 첫 실행: `auto.offset.reset=earliest`로 설정되어 처음부터 모든 메시지 읽기
- 두 번째 실행: 마지막 offset부터 이후 메시지 읽기

### PartitionedConsumer.java
특정 파티션에서 메시지를 읽는 Consumer 예제입니다.

- `TopicPartition` 클래스를 사용하여 수동으로 파티션 할당
- `consumer.assign(...)` 메서드 사용
- **주의**: `assign()`을 사용하면 `subscribe()`를 사용할 수 없습니다.

## 🔧 Runnable JAR 파일 생성

Maven Shade Plugin을 사용하여 실행 가능한 JAR 파일을 생성할 수 있습니다.

```bash
# JAR 파일 생성
mvn clean package

# 생성된 JAR 파일 위치
# target/kafka.demo-0.0.1-SNAPSHOT.jar

# JAR 파일 실행
java -jar target/kafka.demo-0.0.1-SNAPSHOT.jar
```

## 📦 Maven 의존성

프로젝트는 다음 의존성을 사용합니다:

- **kafka-clients 4.0.0**: Kafka 클라이언트 라이브러리
- **log4j-slf4j2-impl 2.24.3**: 로깅 라이브러리
- **jackson-databind 2.19.0**: JSON 데이터 바인딩

## 🐍 Python 예제

### 설치
```bash
pip install kafka-python
```

또는 requirements.txt 사용:
```bash
pip install -r ../../requirements/requirements.txt
```

### 실행
```bash
# Producer 실행
python3 Producer.py

# Consumer 실행
python3 Consumer.py
```

## 📝 테스트 시나리오

### 1. 기본 Producer/Consumer 테스트

터미널 1: Consumer 실행
```bash
mvn exec:java -Dexec.mainClass="bigdata.kafka.demo.Consumer"
```

터미널 2: Producer 실행
```bash
mvn exec:java -Dexec.mainClass="bigdata.kafka.demo.Producer"
```

### 2. Callback Producer 테스트

```bash
mvn exec:java -Dexec.mainClass="bigdata.kafka.demo.CallbackProducer"
```

### 3. Keyed Producer 테스트

```bash
mvn exec:java -Dexec.mainClass="bigdata.kafka.demo.KeyedCallbackProducer"
```

같은 키를 가진 메시지가 같은 파티션으로 전송되는지 확인합니다.

### 4. Partitioned Consumer 테스트

```bash
mvn exec:java -Dexec.mainClass="bigdata.kafka.demo.PartitionedConsumer"
```

특정 파티션(기본값: partition 0)에서만 메시지를 읽습니다.

## ⚠️ 주의사항

1. **Kafka 서버 실행**: 모든 예제를 실행하기 전에 Kafka 서버가 실행 중이어야 합니다.
2. **토픽 생성**: `test` 토픽이 존재하지 않으면 자동으로 생성됩니다 (auto.create.topics.enable=true인 경우).
3. **Consumer Group**: 같은 Consumer Group ID를 사용하면 메시지가 분산되어 수신됩니다.
4. **Partitioned Consumer**: `assign()`을 사용하면 Consumer Group 기능을 사용할 수 없습니다.

## 📖 참고 자료

- [Apache Kafka 공식 문서](https://kafka.apache.org/documentation/)
- 강의 슬라이드 내용
- `../cluster_setup_guide.md`: 클러스터 설정 가이드

