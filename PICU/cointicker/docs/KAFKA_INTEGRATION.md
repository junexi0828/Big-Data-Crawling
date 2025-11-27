# Kafka 통합 가이드

CoinTicker 프로젝트에 Kafka Producer/Consumer를 통합하여 실시간 데이터 스트리밍을 구현합니다.

## 📋 개요

Kafka는 Scrapy Spider에서 수집한 데이터를 실시간으로 스트리밍하고, Consumer를 통해 데이터를 처리하는 역할을 합니다.

### 데이터 흐름

```
Scrapy Spider
    ↓
Kafka Producer (KafkaPipeline)
    ↓
Kafka Topic (cointicker.raw.*)
    ↓
Kafka Consumer (kafka_consumer.py)
    ↓
HDFS 저장 또는 Backend 처리
```

## 🚀 빠른 시작

### 1. Kafka 서버 설정

Kafka 서버가 실행 중이어야 합니다. 자세한 내용은 `kafka_project/README.md`를 참고하세요.

```bash
# Kafka 서버 시작 (예시)
cd kafka_project
./kafka_streams/start_kafka.sh
```

### 2. 설정 파일 생성

```bash
cd PICU/cointicker/config
cp kafka_config.yaml.example kafka_config.yaml
# kafka_config.yaml을 편집하여 실제 Kafka 브로커 주소 설정
```

### 3. Kafka Pipeline 활성화

`worker-nodes/cointicker/settings.py`에서 Kafka Pipeline을 활성화:

```python
ITEM_PIPELINES = {
    "cointicker.pipelines.ValidationPipeline": 300,
    "cointicker.pipelines.DuplicatesPipeline": 400,
    "cointicker.pipelines.HDFSPipeline": 500,
    "cointicker.pipelines.kafka_pipeline.KafkaPipeline": 600,  # 추가
}
```

또는 환경 변수로 설정:

```bash
export KAFKA_BOOTSTRAP_SERVERS="localhost:9092"
export KAFKA_TOPIC_PREFIX="cointicker"
```

### 4. Kafka Consumer 실행

```bash
# 스크립트 사용
bash worker-nodes/run_kafka_consumer.sh

# 또는 직접 실행
python worker-nodes/kafka_consumer.py \
    --bootstrap-servers localhost:9092 \
    --topics cointicker.raw.* \
    --group-id cointicker-consumer \
    --hdfs-namenode hdfs://localhost:9000
```

## 📦 구성 요소

### 1. Kafka Client (`shared/kafka_client.py`)

Kafka Producer와 Consumer를 위한 공통 클라이언트:

- `KafkaProducerClient`: 메시지 전송
- `KafkaConsumerClient`: 메시지 수신

### 2. Kafka Pipeline (`worker-nodes/cointicker/pipelines/kafka_pipeline.py`)

Scrapy Pipeline으로 구현된 Kafka Producer:

- Spider에서 수집한 데이터를 Kafka로 전송
- 배치 처리 지원 (기본 10개)
- 자동 재시도 및 오류 처리

### 3. Kafka Consumer (`worker-nodes/kafka_consumer.py`)

Kafka에서 데이터를 수신하여 처리하는 서비스:

- 실시간 메시지 수신
- HDFS 저장
- 통계 및 모니터링

## ⚙️ 설정

### Kafka 설정 파일 (`config/kafka_config.yaml`)

```yaml
kafka:
  bootstrap_servers:
    - "localhost:9092"

  topics:
    raw_prefix: "cointicker.raw"
    processed_prefix: "cointicker.processed"
    insights_prefix: "cointicker.insights"

  producer:
    acks: "all"
    retries: 3
    batch_size: 10
    timeout: 10

  consumer:
    group_id: "cointicker-consumer"
    auto_offset_reset: "earliest"
    enable_auto_commit: true
    timeout: 10
```

### Scrapy 설정 (`worker-nodes/cointicker/settings.py`)

```python
# Kafka 브로커 주소
KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"  # 또는 리스트

# 토픽 접두사
KAFKA_TOPIC_PREFIX = "cointicker"
```

## 🔧 사용 예시

### Producer 사용 (Pipeline 자동)

Kafka Pipeline이 활성화되면 Spider 실행 시 자동으로 Kafka로 데이터가 전송됩니다:

```bash
cd worker-nodes
scrapy crawl upbit_trends
```

### Consumer 사용

```bash
# 기본 실행
python worker-nodes/kafka_consumer.py

# 커스텀 설정
python worker-nodes/kafka_consumer.py \
    --bootstrap-servers "192.168.1.100:9092,192.168.1.101:9092" \
    --topics "cointicker.raw.upbit_trends" "cointicker.raw.coinness" \
    --group-id "my-consumer-group" \
    --hdfs-namenode "hdfs://192.168.1.100:9000"
```

### Python 코드에서 직접 사용

```python
from shared.kafka_client import KafkaProducerClient, KafkaConsumerClient

# Producer
producer = KafkaProducerClient(
    bootstrap_servers=["localhost:9092"]
)
producer.connect()
producer.send("cointicker.raw.test", {"key": "value"})
producer.close()

# Consumer
consumer = KafkaConsumerClient(
    bootstrap_servers=["localhost:9092"],
    group_id="test-consumer"
)
consumer.connect(["cointicker.raw.test"])

def process_message(message):
    print(f"Received: {message.value}")

consumer.consume(callback=process_message)
consumer.close()
```

## 📊 토픽 구조

### 원시 데이터 토픽

- `cointicker.raw.upbit_trends`: Upbit 트렌드 데이터
- `cointicker.raw.coinness`: Coinness 뉴스 데이터
- `cointicker.raw.saveticker`: SaveTicker 데이터
- `cointicker.raw.perplexity`: Perplexity 분석 데이터
- `cointicker.raw.cnn_fear_greed`: CNN Fear & Greed Index

### 처리된 데이터 토픽

- `cointicker.processed.*`: MapReduce로 정제된 데이터

### 인사이트 토픽

- `cointicker.insights.*`: Backend에서 생성된 인사이트

## 🐛 문제 해결

### Kafka 연결 실패

1. **Kafka 서버 확인**:
   ```bash
   # Kafka 서버가 실행 중인지 확인
   ps aux | grep kafka
   ```

2. **네트워크 확인**:
   ```bash
   # 브로커 주소 확인
   telnet localhost 9092
   ```

3. **설정 확인**:
   - `bootstrap_servers`가 올바른지 확인
   - 방화벽 설정 확인

### Consumer가 메시지를 받지 못함

1. **토픽 확인**:
   ```bash
   # 토픽 목록 확인
   kafka-topics.sh --list --bootstrap-server localhost:9092
   ```

2. **Consumer Group 확인**:
   ```bash
   # Consumer Group 상태 확인
   kafka-consumer-groups.sh --bootstrap-server localhost:9092 --list
   ```

3. **오프셋 확인**:
   ```bash
   # Consumer Group 오프셋 확인
   kafka-consumer-groups.sh --bootstrap-server localhost:9092 \
       --group cointicker-consumer --describe
   ```

### 메시지 손실

1. **Producer ACK 설정 확인**: `acks: "all"` 권장
2. **재시도 설정 확인**: `retries: 3` 이상 권장
3. **Consumer 자동 커밋 확인**: `enable_auto_commit: true`

## 📚 추가 리소스

- [Kafka 프로젝트 README](../../../kafka_project/README.md)
- [Kafka 공식 문서](https://kafka.apache.org/documentation/)
- [kafka-python 문서](https://kafka-python.readthedocs.io/)

