# Kafka Consumer 디버깅 보고서

**작성일:** 2025년 12월 7일

---

## 1. 문제 현상

- **시스템:** Kafka Consumer (`PICU/cointicker/shared/kafka_client.py`)
- **증상:** Kafka 토픽에 메시지가 정상적으로 전송(Produce)되고 있음에도 불구하고, Consumer가 메시지를 전혀 소비(Consume)하지 못하고 대기 상태에 머무는 현상 발생.

## 2. 원인 분석

- Consumer 애플리케이션 시작 직후, Kafka 클러스터로부터 **파티션(Partition)을 할당받기 전에 메시지 소비를 시도**하는 로직 상의 경쟁 조건(Race Condition)이 원인으로 파악됨.
- Kafka Consumer는 Consumer Group에 참여한 뒤, Group Coordinator로부터 파티션을 할당받는 '리밸런싱(Rebalancing)' 과정을 거쳐야 메시지를 소비할 수 있음.
- 기존 `consume` 메서드는 이러한 리밸런싱 대기 시간 없이 즉시 메시지 수신을 시도하여, 할당된 파티션이 없으므로 영구 대기 상태에 빠짐.
- `poll()` 메서드는 메시지 수신 외에도 파티션 할당을 트리거하고 멤버십을 유지하는 '하트비트' 역할을 수행하는데, 이 특성이 제대로 활용되지 않았음.

## 3. 해결 방안

`PICU/cointicker/shared/kafka_client.py`의 `KafkaConsumerClient.consume` 메서드를 다음과 같이 수정함.

### 3.1. 파티션 할당 대기 로직 추가

- 메시지 소비 루프에 진입하기 전, **최대 30초** 동안 파티션이 할당될 때까지 대기하는 로직을 추가.
- `while` 루프 내에서 `consumer.assignment()`를 호출하여 파티션 할당 여부를 지속적으로 확인.
- 파티션이 할당되지 않았을 경우, `consumer.poll(timeout_ms=1000)`을 호출하여 클러스터에 파티션 할당을 능동적으로 요청하고 하트비트를 전송.

### 3.2. `poll()` 기반의 안정적인 소비 루프 구현

- 파티션 할당이 완료된 후, 메인 소비 루프에서 `consumer.poll()`을 주기적으로 호출하여 메시지 배치를 가져오도록 변경.
- `poll()`의 타임아웃을 설정하여, 수신할 메시지가 없더라도 블로킹되지 않고 다음 `poll()`을 시도할 수 있도록 하여 안정성을 높임.

## 4. 검증 내역

- **Spider → Kafka:** 메시지 전송 정상 확인.
- **HDFS 저장:** 데이터 저장 정상 확인.
- **Kafka Consumer:**
    - **수정 전:** 파티션 할당 문제로 메시지 소비 실패.
    - **수정 후:** 파티션 할당 대기 로직이 정상 동작하여, 초기 지연 후 메시지를 안정적으로 소비하는 것을 확인함.

## 5. 관련 파일

- `/Users/juns/code/personal/notion/pknu_workspace/bigdata/PICU/cointicker/shared/kafka_client.py`

---
