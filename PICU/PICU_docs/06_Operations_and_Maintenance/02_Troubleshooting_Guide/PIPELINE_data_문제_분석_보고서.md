# 데이터 파이프라인 동작 불가 문제 분석 보고서

**작성일**: 2025-12-06
**분석 대상**: Spider → Kafka → HDFS 데이터 파이프라인
**상태**: 🔴 **중요 문제 발견**

---

## 📋 요약

GUI에서 모든 서비스를 실행했으나 실제 데이터가 파이프라인을 통해 흐르지 않는 문제가 확인되었습니다. 각 단계별 확인 결과, **Kafka Consumer가 메시지를 소비하지 않는 것이 핵심 문제**입니다.

---

## 🔍 순차 확인 결과

### ✅ 1단계: Spider 데이터 수집

**상태**: 정상 동작

- **확인 방법**: Scrapy 로그 분석
- **결과**:
  ```
  'item_scraped_count': 9
  'items_per_minute': 270.0
  ```
- **결론**: Spider가 정상적으로 9개 아이템을 수집했습니다.

---

### ✅ 2단계: Spider → Kafka 전송

**상태**: 정상 동작

- **확인 방법**: Scrapy 로그에서 Kafka Pipeline 로그 확인
- **결과**:
  ```
  2025-12-06 14:10:07 [cointicker.pipelines.kafka_pipeline] INFO:
  Sent 9/9 items to Kafka topic: cointicker.raw.upbit_trends
  ```
- **Kafka 토픽 확인**:
  ```
  토픽 목록:
    - cointicker.raw.upbit_trends
    - cointicker.raw.perplexity
    - cointicker.raw.saveticker
  ```
- **Kafka 메시지 수**: **270개 메시지가 쌓여있음**
- **결론**: Spider가 Kafka로 정상적으로 데이터를 전송하고 있습니다.

---

### ❌ 3단계: Kafka Consumer 메시지 소비

**상태**: **문제 발견**

- **확인 방법**:

  1. Consumer Groups 확인
  2. Kafka 메시지 수 확인
  3. 프로세스 실행 상태 확인

- **결과**:

  ```
  Consumer Groups: 없음
  Kafka 메시지 수: 270개 (소비되지 않음)
  Kafka Consumer 프로세스: 실행 중 (PID 98471)
  ```

- **문제점**:

  1. **Consumer Groups가 생성되지 않음**: Kafka Consumer가 토픽을 구독하지 못하고 있음
  2. **메시지가 소비되지 않음**: 270개 메시지가 계속 쌓이고 있음
  3. **GUI 표시**: "Kafka: 중지됨" (실제로는 프로세스는 실행 중)

- **원인 분석**:
  - Kafka Consumer가 `cointicker.raw.*` 패턴으로 구독을 시도하지만 실제로는 구독에 실패
  - `KafkaConsumerClient.connect()` 메서드의 패턴 구독 로직 문제 가능성
  - Consumer가 시작되었지만 메시지 소비 루프가 실행되지 않음

---

### ❌ 4단계: HDFS 저장

**상태**: **데이터 없음**

- **확인 방법**: HDFS 디렉토리 확인
- **결과**:
  ```
  hdfs dfs -ls /raw
  ls: `/raw': No such file or directory
  ```
- **임시 파일 확인**:
  ```
  /PICU/cointicker/data/temp/20251206/ (비어있음)
  ```
- **결론**: Kafka Consumer가 메시지를 소비하지 않아 HDFS에 저장되지 않음

---

## 🔴 핵심 문제

### 문제 1: Kafka Consumer가 메시지를 소비하지 않음

**증상**:

- Kafka Consumer 프로세스는 실행 중 (PID 98471)
- 하지만 Consumer Groups가 생성되지 않음
- Kafka에 270개 메시지가 쌓여있지만 소비되지 않음

**가능한 원인**:

1. **토픽 패턴 구독 실패**: `cointicker.raw.*` 패턴 구독이 제대로 동작하지 않음
2. **Consumer 연결 실패**: Kafka 브로커에 연결은 되지만 구독 실패
3. **메시지 소비 루프 미실행**: `consume()` 메서드가 호출되지 않거나 블로킹됨

**영향**:

- Spider → Kafka 전송은 정상이나, Kafka → HDFS 저장이 이루어지지 않음
- 데이터가 Kafka에만 쌓이고 HDFS로 전달되지 않음

---

### 문제 2: HDFS 저장 경로 확인 필요

**현재 상태**:

- HDFS는 실행 중 (포트 9000)
- `/raw` 디렉토리가 존재하지 않음
- `HDFSUploadManager`가 데이터를 받지 못해 저장할 기회가 없음

**예상 동작**:

- Kafka Consumer가 메시지를 받으면 → `_save_to_hdfs()` 호출
- `HDFSUploadManager.save_to_hdfs()` 실행
- HDFS 경로: `/raw/{source}/{YYYYMMDD}/` 형식으로 저장

---

## 🔧 해결 방안

### ✅ 해결 완료 (2025-12-06)

#### 1. 패턴 구독 버그 수정

**문제**: `kafka_client.py`의 `connect()` 메서드에서 패턴을 정규식 객체(`re.compile()`)로 변환하여 `KafkaConsumer.subscribe(pattern=...)`에 전달하고 있었습니다. 하지만 `subscribe()` 메서드는 문자열 패턴을 받아야 합니다.

**수정 내용**:

- `re.compile()`을 사용하여 정규식 객체로 변환하는 로직 제거
- 원래 문자열 패턴을 그대로 `subscribe(pattern=...)`에 전달하도록 수정
- 파일: `PICU/cointicker/shared/kafka_client.py` (라인 308-331)

#### 2. Consumer 타임아웃 문제 해결

**문제**: `consumer_timeout_ms`가 `self.timeout * 1000` (기본 10초)로 설정되어 있어, 메시지가 없으면 타임아웃되어 루프가 종료되었습니다.

**수정 내용**:

- `consumer_timeout_ms=None`으로 설정하여 무한 대기하도록 변경
- Consumer가 메시지를 기다리는 동안 계속 실행되도록 수정
- 파일: `PICU/cointicker/shared/kafka_client.py` (라인 328, 350)

#### 3. 로깅 및 검증 개선

**수정 내용**:

- 구독 상태 확인 로직 추가 (`subscription()` 확인)
- 메시지 소비 루프 시작/종료 로깅 추가
- 예외 발생 시 상세한 스택 트레이스 출력 (`exc_info=True`)
- Consumer 시작 시 구독 상태 확인 및 로깅
- 파일:
  - `PICU/cointicker/shared/kafka_client.py` (라인 336-339, 352-355, 377-399)
  - `PICU/cointicker/worker-nodes/kafka/kafka_consumer.py` (라인 90-127)

#### 4. 테스트 결과

```python
# 패턴 구독 테스트 성공
Message 1: topic=cointicker.raw.perplexity, partition=0, offset=0
Message 2: topic=cointicker.raw.perplexity, partition=0, offset=1
Message 3: topic=cointicker.raw.perplexity, partition=0, offset=2
Total messages consumed: 5
```

✅ **패턴 구독이 정상적으로 동작함을 확인**

### ✅ 추가 개선 사항 완료 (2025-12-06)

#### 1. 모니터링 개선

**구현 내용**:

- **Consumer Groups 상태 GUI 표시**: `KafkaConsumerClient.get_consumer_groups()` 메서드 추가
  - 구독된 토픽 목록
  - 할당된 파티션 정보
  - Consumer Group ID
- **메시지 소비율 추적**: `KafkaConsumerService`에 실시간 소비율 계산 로직 추가
  - 1초마다 메시지 소비율 계산 (`messages_per_second`)
  - GUI 대시보드에 "소비율: X.XX msg/s" 형태로 표시
- **GUI 통합**: `dashboard_tab.py`에 Consumer Groups 상태와 소비율 표시 추가
  - `kafka_rate_label`: 메시지 소비율 표시
  - `kafka_groups_label`: Consumer Groups 정보 표시

**파일**:

- `PICU/cointicker/shared/kafka_client.py` - `get_consumer_groups()` 메서드 추가
- `PICU/cointicker/worker-nodes/kafka/kafka_consumer.py` - 소비율 추적 로직 추가, `get_stats()` 메서드 추가
- `PICU/cointicker/gui/modules/kafka_module.py` - `get_consumer_groups` 명령어 추가
- `PICU/cointicker/gui/app.py` - Consumer Groups 상태 수집 로직 추가
- `PICU/cointicker/gui/ui/dashboard_tab.py` - GUI 표시 추가
- `PICU/cointicker/gui/modules/process_monitor.py` - Kafka Consumer 로그 파싱 개선

#### 2. 에러 처리 강화

**구현 내용**:

- **Consumer 연결 재시도 로직**: `KafkaConsumerClient.connect()` 메서드에 재시도 로직 추가
  - 기본 최대 재시도 횟수: 3회
  - 재시도 지연 시간: 2초 (지수 백오프 적용)
  - `execute_with_retry` 유틸리티 사용
- **구독 실패 시 명확한 에러 메시지**: 구독 상태 확인 및 로깅 개선
  - 구독 실패 시 "Consumer subscription is empty!" 경고
  - 상세한 예외 정보 로깅 (`exc_info=True`)

**파일**:

- `PICU/cointicker/shared/kafka_client.py` - `connect()` 메서드에 재시도 로직 추가, `_connect_internal()` 분리
- `PICU/cointicker/worker-nodes/kafka/kafka_consumer.py` - 구독 상태 확인 로직 개선

---

## 📊 데이터 흐름 현황

### 수정 전 (문제 상태)

```
Spider (✅ 정상)
  ↓
KafkaPipeline (✅ 정상) → Kafka 토픽 (✅ 270개 메시지)
  ↓
KafkaConsumer (❌ 문제) → 메시지 소비 실패
  ↓
HDFSUploadManager (❌ 데이터 없음)
  ↓
HDFS (❌ 저장 안됨)
```

### 수정 후 (예상 상태)

```
Spider (✅ 정상)
  ↓
KafkaPipeline (✅ 정상) → Kafka 토픽 (✅ 메시지 쌓임)
  ↓
KafkaConsumer (✅ 수정됨) → 메시지 소비 성공
  ↓
HDFSUploadManager (✅ 데이터 수신)
  ↓
HDFS (✅ 저장됨)
```

**참고**: 수정 사항 적용 후 GUI에서 Kafka Consumer를 재시작해야 합니다.

---

## 🎯 MapReduce 관련

**MapReduce는 작업(job) 형태**이므로 자동으로 실행되지 않습니다. 이는 정상 동작입니다.

- HDFS에 데이터가 쌓인 후
- 사용자가 수동으로 MapReduce 작업을 실행해야 합니다
- GUI의 "제어" 탭에서 MapReduce 작업을 실행할 수 있습니다

---

## 📝 다음 단계

### 즉시 실행 사항

1. **GUI에서 Kafka Consumer 재시작**

   - 제어 탭에서 Kafka Consumer 중지 후 재시작
   - 로그에서 메시지 소비 확인

2. **메시지 소비 확인**
   - Kafka Consumer 로그에서 "Received message" 메시지 확인
   - HDFS에 데이터가 저장되는지 확인

### 향후 개선 사항

1. **Consumer Groups 모니터링** - GUI에 Consumer Groups 상태 표시 추가
2. **에러 처리 강화** - Consumer 연결 실패 시 재시도 로직 추가
3. **성능 모니터링** - 메시지 소비율(consumption rate) 모니터링

---

## 🔗 관련 파일

- `PICU/cointicker/worker-nodes/kafka/kafka_consumer.py` - Kafka Consumer 서비스
- `PICU/cointicker/shared/kafka_client.py` - Kafka 클라이언트 (패턴 구독 로직)
- `PICU/cointicker/shared/hdfs_upload_manager.py` - HDFS 업로드 매니저
- `PICU/cointicker/worker-nodes/cointicker/pipelines/kafka_pipeline.py` - Kafka Pipeline

---

**보고서 작성자**: Juns AI Assistant
**최초 작성일**: 2025-12-06
**최종 업데이트**: 2025-12-06 (Kafka Consumer 버그 수정 완료)
