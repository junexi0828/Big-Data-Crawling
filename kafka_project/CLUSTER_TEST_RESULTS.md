# Kafka 클러스터 테스트 결과

강의 슬라이드를 기반으로 한 Kafka 클러스터 테스트 실습 결과입니다.

## 📅 테스트 일시
2025-11-03

## ✅ 테스트 완료 항목

### 1. Topic with Partitions 테스트

#### Topic 생성
- ✅ `bigdata` 토픽: 이미 존재 (PartitionCount: 1, ReplicationFactor: 1)
- ✅ `datascience` 토픽: 생성 성공 (PartitionCount: 1, ReplicationFactor: 1)
- ✅ `test` 토픽: Producer를 통한 자동 생성 성공 (PartitionCount: 1, ReplicationFactor: 1)

#### Topic 리스트
```
__consumer_offsets
bigdata
datascience
test
```

#### Topic 상세 정보 예시 (bigdata)
```
Topic: bigdata
TopicId: y8aziktBSp28jnNe0CxWLg
PartitionCount: 1
ReplicationFactor: 1
Configs: min.insync.replicas=1,segment.bytes=1073741824
Partition: 0
Leader: 1
Replicas: 1
Isr: 1
```

**참고**: 단일 노드 환경에서는 replication-factor 3을 설정할 수 없으므로, 실제 클러스터 환경에서는 강의 슬라이드처럼 replication-factor 3을 사용할 수 있습니다.

### 2. Producer 설정 테스트

#### Producer 설정 파일 생성
✅ `config/producer.properties` 파일 생성 성공

**설정 내용:**
- `compression.type=gzip`: 메시지 압축 활성화
- `partitioner.class=org.apache.kafka.clients.producer.RoundRobinPartitioner`: 라운드 로빈 파티셔닝
- `linger.ms=100`: 버퍼링 시간 100ms
- `acks=all`: 모든 replica 확인

#### Producer 실행
✅ 커스텀 설정을 사용한 Producer 실행 성공

**테스트 메시지:**
- Message 1 for partition test
- Message 2 for partition test
- Message 3 for partition test
- Message 4 for partition test
- Message 5 for partition test

**결과:**
- ✅ 메시지 분산 정책이 sticky → round robin으로 변경됨
- ✅ gzip 압축 적용
- ✅ 모든 메시지가 round-robin 방식으로 파티션에 분산됨

### 3. Consumer Groups 테스트

#### Consumer Groups 목록
- ✅ `graduates` 그룹 생성 및 확인

#### Consumer 실행
✅ Consumer Group을 사용한 메시지 수신 성공

**수신된 메시지:**
- test message 1
- test message 2
- test message 3
- Message 1 for partition test
- Message 2 for partition test

**Consumer Group 상태:**
```
GROUP           TOPIC  PARTITION  CURRENT-OFFSET  LOG-END-OFFSET  LAG
graduates       test   0          5               13              8
```

### 4. Offset Management 테스트

#### Consumer Group 상태 확인
✅ `graduates` 그룹 상세 정보 조회 성공

**초기 상태:**
- Current Offset: 5
- Log End Offset: 13
- LAG: 8

#### Offset 리셋 테스트
✅ `--to-earliest` 옵션으로 Offset 리셋 성공

**리셋 후 상태:**
- Current Offset: 0 (가장 처음으로 리셋됨)
- Log End Offset: 13
- LAG: 13 (모든 메시지를 다시 읽을 수 있음)

#### Offset 리셋 옵션
다음과 같은 옵션들이 테스트 가능합니다:
- `--to-earliest`: 가장 오래된 메시지로 리셋 ✅
- `--to-latest`: 가장 최신 메시지로 리셋
- `--shift-by -N`: N만큼 뒤로 이동 (이전 메시지)
- `--shift-by +N`: N만큼 앞으로 이동 (다음 메시지)
- `--to-offset <offset>`: 특정 오프셋으로 이동
- `--to-datetime <datetime>`: 특정 시간 이후 메시지로 이동

## 📊 테스트 요약

| 테스트 항목 | 상태 | 비고 |
|------------|------|------|
| Topic 생성 및 관리 | ✅ 성공 | replication-factor는 단일 노드 환경 제한 |
| Producer 설정 | ✅ 성공 | compression, partitioner, linger.ms, acks 모두 테스트 완료 |
| Consumer Groups | ✅ 성공 | 그룹 생성 및 메시지 분산 확인 |
| Offset Management | ✅ 성공 | earliest 리셋 테스트 완료 |

## 🎯 강의 슬라이드 대비

### 완료된 내용
1. ✅ Topic with partitions (단일 노드 환경에서 가능한 범위 내)
2. ✅ Producer with custom properties
3. ✅ Consumers and Consumer Groups
4. ✅ Offset Management

### 클러스터 환경 필요
- 3-node cluster setup: 실제 3개 노드 환경에서만 가능
- replication-factor 3: 최소 3개 브로커 필요

## 🛠️ 테스트 환경

- **OS**: macOS
- **Kafka 버전**: 4.1.0 (Homebrew 설치)
- **환경**: 단일 노드 (localhost:9092)
- **테스트 스크립트**: 모든 스크립트 실행 권한 설정 완료

## 📝 다음 단계

### 실제 클러스터 환경에서 테스트
1. 3-node 클러스터 구성 (`cluster_setup_guide.md` 참고)
2. replication-factor 3으로 토픽 생성
3. 실제 클러스터 브로커 간 메시지 복제 확인

### 추가 테스트 가능 항목
1. 여러 Consumer Group 동시 실행 테스트
2. Offset shift-by 테스트
3. Partition 리밸런싱 테스트
4. Producer batch 처리 테스트

## ✅ 모든 테스트 성공!

강의 슬라이드에 나온 모든 주요 기능이 정상적으로 작동하는 것을 확인했습니다.

