# Kafka 통합 완료

Kafka Producer/Consumer 구현이 완료되었습니다.

## ✅ 구현 완료 항목

### 1. Kafka Client (`shared/kafka_client.py`)

- ✅ `KafkaProducerClient`: 메시지 전송 클라이언트
- ✅ `KafkaConsumerClient`: 메시지 수신 클라이언트
- ✅ 배치 전송 지원
- ✅ 자동 재시도 및 오류 처리

### 2. Kafka Producer Pipeline (`worker-nodes/cointicker/pipelines/kafka_pipeline.py`)

- ✅ Scrapy Pipeline으로 구현
- ✅ Spider에서 수집한 데이터를 Kafka로 실시간 전송
- ✅ 배치 처리 지원 (기본 10개)
- ✅ 토픽 자동 생성 (예: `cointicker.raw.upbit_trends`)

### 3. Kafka Consumer (`worker-nodes/kafka_consumer.py`)

- ✅ 실시간 메시지 수신
- ✅ HDFS 저장 지원
- ✅ 통계 및 모니터링
- ✅ 시그널 핸들링 (안전한 종료)

### 4. 설정 파일

- ✅ `config/kafka_config.yaml.example`: Kafka 설정 예제
- ✅ Scrapy settings에 Kafka 설정 추가

### 5. 실행 스크립트

- ✅ `worker-nodes/run_kafka_consumer.sh`: Consumer 실행 스크립트
- ✅ `worker-nodes/kafka_consumer_service.py`: 서비스 래퍼

### 6. GUI 통합

- ✅ `gui/modules/kafka_module.py`: Kafka 모듈
- ✅ `gui/module_mapping.json`에 Kafka 모듈 추가

### 7. 문서

- ✅ `KAFKA_INTEGRATION.md`: 통합 가이드

## 🚀 사용 방법

### 1. 의존성 설치

```bash
# PICU 루트에서
source venv/bin/activate
pip install kafka-python
```

### 2. Kafka 서버 실행

Kafka 서버가 실행 중이어야 합니다. 자세한 내용은 `kafka_project/README.md` 참고.

### 3. 설정 파일 생성

```bash
cd PICU/cointicker/config
cp kafka_config.yaml.example kafka_config.yaml
# kafka_config.yaml 편집
```

### 4. Kafka Pipeline 활성화

`worker-nodes/cointicker/settings.py`에서 주석 해제:

```python
ITEM_PIPELINES = {
    "cointicker.pipelines.ValidationPipeline": 300,
    "cointicker.pipelines.DuplicatesPipeline": 400,
    "cointicker.pipelines.HDFSPipeline": 500,
    "cointicker.pipelines.kafka_pipeline.KafkaPipeline": 600,  # 주석 해제
}
```

### 5. Consumer 실행

```bash
# 스크립트 사용
bash worker-nodes/run_kafka_consumer.sh

# 또는 직접 실행
python worker-nodes/kafka_consumer.py
```

### 6. GUI에서 관리

GUI 애플리케이션의 "모듈 관리" 탭에서 Kafka 모듈을 확인하고 제어할 수 있습니다.

## 📊 데이터 흐름

```
Scrapy Spider
    ↓
Kafka Producer (KafkaPipeline)
    ↓
Kafka Topic (cointicker.raw.*)
    ↓
Kafka Consumer
    ↓
HDFS 저장
```

## 📚 문서

- [Kafka 통합 가이드](KAFKA_INTEGRATION.md)
- [Kafka 프로젝트 README](../../kafka_project/README.md)
