# Kafka Consumer 하이브리드 패턴 구독 구현

## 개요

Kafka Consumer의 와일드카드 패턴 구독을 개선하여 **하이브리드 방식**을 구현했습니다.

- **초기 스캔**: AdminClient로 즉시 토픽 목록 확인 (디버깅 및 로깅)
- **실제 구독**: Kafka 네이티브 패턴 사용 (자동 업데이트 활성화)

## 문제점

### 기존 수동 방식의 한계

```python
# ❌ 기존 방식: AdminClient로 토픽 조회 → 리스트로 구독
all_topics = admin_client.list_topics()
matched_topics = [t for t in all_topics if pattern.match(t)]
consumer.subscribe(matched_topics)  # 고정된 리스트
```

**단점:**
- 새로운 토픽이 생성되어도 자동으로 구독하지 않음
- Consumer 재시작 필요
- 사용자 개입 필요

## 해결책: 하이브리드 방식

### 구현 코드

```python
# shared/kafka_client.py의 _connect_internal() 메서드

# 🔍 1단계: AdminClient로 초기 토픽 스캔 (디버깅 및 로깅용)
admin_client = KafkaAdminClient(bootstrap_servers=self.bootstrap_servers)
all_topics = admin_client.list_topics()

# 패턴 매칭 및 로깅
pattern_regex = pattern_str.replace(".", r"\.").replace("*", ".*")
compiled_pattern = re.compile(f"^{pattern_regex}$")
initial_matched_topics = [t for t in all_topics if compiled_pattern.match(t)]

logger.info(
    f"🔍 Initial pattern matching: {pattern_str} -> "
    f"{len(initial_matched_topics)} topics found: {initial_matched_topics}"
)

# 🚀 2단계: Kafka 네이티브 패턴 구독 (자동 업데이트)
consumer = KafkaConsumer(...)
kafka_pattern = f"^{pattern_str.replace('.', r'\\.').replace('*', '.*')}$"
consumer.subscribe(pattern=kafka_pattern)

logger.info(
    f"🎯 Kafka Consumer subscribed with pattern: {kafka_pattern}, "
    f"mode=AUTO-UPDATE"
)
```

## 동작 방식

### 시나리오: Consumer 시작

```
⏰ T=0: Consumer 시작
├─ 🔍 1단계: AdminClient로 즉시 토픽 조회
│   └─ 로그: "🔍 Initial pattern matching: cointicker.raw.*
│             -> 3 topics found: [upbit_trends, saveticker, perplexity]"
│
└─ 🚀 2단계: Kafka 네이티브 패턴으로 구독
    └─ 로그: "🎯 Kafka Consumer subscribed with pattern: ^cointicker\.raw\..*$,
              mode=AUTO-UPDATE"
```

### 시나리오: 새 토픽 생성

```
⏰ T=30분: 새로운 스파이더 시작 (coinness)
├─ 🕷️  Scrapy coinness 스파이더 시작
│   └─ 새 토픽 생성: cointicker.raw.coinness
│
└─ 🔄 Kafka Consumer의 자동 반응 (사용자 개입 없음!)
    ├─ Kafka가 메타데이터 업데이트 감지 (약 5초 이내)
    ├─ 자동으로 새 토픽 구독
    └─ 메시지 수신 시작
```

## 장점

### 1. 즉시 피드백 (초기 스캔)
- AdminClient로 즉시 어떤 토픽이 매칭되는지 확인
- 로그에 토픽 목록 출력
- GUI에 표시 가능

### 2. 자동 업데이트 (네이티브 패턴)
- 새로운 토픽이 생성되면 자동으로 구독
- Consumer 재시작 불필요
- 사용자 개입 불필요

### 3. 두 방식의 장점 결합
| 기능 | 수동 방식 | 네이티브 방식 | 하이브리드 |
|------|-----------|---------------|------------|
| 즉시 토픽 확인 | ✅ | ❌ | ✅ |
| 자동 업데이트 | ❌ | ✅ | ✅ |
| 디버깅 용이 | ✅ | ❌ | ✅ |
| 코드 복잡도 | 높음 | 낮음 | 중간 |

## 로그 출력 예시

### Consumer 시작 시

```
2025-12-06 20:30:00 - INFO - 🔍 Initial pattern matching: ['cointicker.raw.*']
                             -> 3 topics found: ['cointicker.raw.upbit_trends',
                             'cointicker.raw.saveticker', 'cointicker.raw.perplexity']

2025-12-06 20:30:00 - INFO - 🎯 Kafka Consumer subscribed with pattern:
                             ^cointicker\.raw\..*$, group_id=cointicker-consumer,
                             mode=AUTO-UPDATE

2025-12-06 20:30:00 - INFO - ✅ Kafka Consumer subscription confirmed: set()
                             (will auto-update as new topics are created)
```

### 메시지 수신 후 (poll 호출 후)

```
# subscription이 자동으로 업데이트됨
subscription = consumer.subscription()
# Output: {'cointicker.raw.upbit_trends', 'cointicker.raw.saveticker',
#          'cointicker.raw.perplexity'}
```

### 새 토픽 생성 시

```
# Scrapy에서 coinness 스파이더 시작
2025-12-06 21:00:00 - INFO - Starting spider: coinness

# Kafka Consumer가 자동으로 감지 (약 5초 후)
# 별도 로그 없이 자동으로 메시지 수신 시작
[1234] 📨 cointicker.raw.coinness | offset=0
```

## GUI 통합

### Dashboard에서의 표시

```
┌─────────────────────────────────────────┐
│ 📊 Kafka Consumer Status                │
├─────────────────────────────────────────┤
│ Status: ✅ RUNNING                      │
│ Pattern: cointicker.raw.*               │
│ Mode: 🔄 AUTO-UPDATE                    │
│                                         │
│ Initial Topics: 3                       │
│   • cointicker.raw.upbit_trends         │
│   • cointicker.raw.saveticker           │
│   • cointicker.raw.perplexity           │
│                                         │
│ Currently Subscribed: 4 🆕              │
│   • cointicker.raw.upbit_trends         │
│   • cointicker.raw.saveticker           │
│   • cointicker.raw.perplexity           │
│   • cointicker.raw.coinness 🆕          │
└─────────────────────────────────────────┘
```

### 새 토픽 감지 알림

```python
# GUI 코드 예시 (kafka_module.py)
def _check_subscription_updates(self):
    """구독 상태를 주기적으로 확인하여 새 토픽 감지"""
    current_subscription = self.consumer.consumer.subscription()

    if current_subscription != self.last_subscription:
        new_topics = current_subscription - self.last_subscription

        if new_topics:
            self.logger.info(f"🆕 New topics auto-subscribed: {new_topics}")
            # GUI 알림 표시
            self.show_notification(
                f"New topic detected: {', '.join(new_topics)}"
            )

        self.last_subscription = current_subscription
```

## 사용 방법

### 기본 사용

```python
from shared.kafka_client import KafkaConsumerClient

# Consumer 생성
consumer = KafkaConsumerClient(
    bootstrap_servers=['localhost:9092'],
    group_id='my-consumer-group',
    auto_offset_reset='latest'
)

# 와일드카드 패턴으로 연결
topics = ['cointicker.raw.*']
consumer.connect(topics)

# 메시지 수신
for msg in consumer.consumer:
    print(f"Received: {msg.topic} | {msg.value}")
```

### 구독 상태 확인

```python
# 초기 매칭된 토픽 확인 (로그 참조)
# 로그: "🔍 Initial pattern matching: ... -> 3 topics found: [...]"

# 현재 구독 상태 확인 (poll 후)
subscription = consumer.consumer.subscription()
print(f"Currently subscribed topics: {subscription}")
```

## 테스트

### 단위 테스트

```bash
cd /Users/juns/code/personal/notion/pknu_workspace/bigdata/PICU/cointicker
source venv/bin/activate

python -c "
from shared.kafka_client import KafkaConsumerClient

consumer = KafkaConsumerClient(
    bootstrap_servers=['localhost:9092'],
    group_id='test-consumer'
)

# 패턴 구독
consumer.connect(['cointicker.raw.*'])

# 구독 확인
consumer.consumer.poll(timeout_ms=2000)
subscription = consumer.consumer.subscription()
print(f'✅ Subscribed topics: {subscription}')

consumer.close()
"
```

### 통합 테스트

1. **Consumer 시작**: `python worker-nodes/kafka/kafka_consumer.py`
2. **새 스파이더 실행**: `scrapy crawl coinness`
3. **자동 구독 확인**: Consumer 로그에서 새 토픽의 메시지 수신 확인

## 주의사항

### 1. poll() 호출 전 subscription 상태

```python
# ⚠️ poll() 호출 전에는 subscription이 빈 set일 수 있음
subscription_before_poll = consumer.subscription()  # set()

# poll() 또는 메시지 수신 후 자동 업데이트
consumer.poll(timeout_ms=1000)
subscription_after_poll = consumer.subscription()  # {'topic1', 'topic2', ...}
```

### 2. 메타데이터 업데이트 지연

- 새 토픽이 생성된 후 자동 구독까지 약 5초 소요
- Kafka의 메타데이터 갱신 주기에 따라 다를 수 있음

### 3. Java 정규식 문법

```python
# Kafka는 Java 정규식을 사용
# Python 와일드카드를 Java 정규식으로 변환 필요

# 입력: "cointicker.raw.*"
# 변환: "^cointicker\\.raw\\..*$"
```

## 관련 파일

- **구현**: `shared/kafka_client.py:327-445`
- **테스트**: `tests/test_kafka_client.py`
- **문서**: `PICU_docs/03_Implementation/Kafka_Consumer_Hybrid_Pattern_Implementation.md`
- **가이드**: `PICU_docs/06_Operations_and_Maintenance/02_Troubleshooting_Guide/Manual_Pipeline_Execution_Guide.md`

## 버전 정보

- **구현일**: 2025-12-06
- **버전**: 1.0.0
- **상태**: ✅ 프로덕션 준비 완료
- **테스트**: ✅ 통과

---

**작성자**: Claude Code
**마지막 수정**: 2025-12-06
