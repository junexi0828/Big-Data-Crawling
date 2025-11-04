# Kafka 클러스터 테스트 프로젝트

강의 슬라이드를 기반으로 한 Kafka 클러스터 테스트 실습 프로젝트입니다.

## 📁 프로젝트 구조

```
kafka_project/
├── README.md                    # 이 파일
├── cluster_setup_guide.md       # 3-node 클러스터 설정 가이드
├── KAFKA_TEST_RESULTS.md        # 기본 테스트 결과
│
├── run_cluster_tests.sh         # 통합 테스트 스크립트
├── test_cluster_topics.sh       # Topic with partitions 테스트
├── test_producer_config.sh      # Producer 설정 테스트
├── test_consumer_groups.sh      # Consumer Groups 테스트
├── test_offset_management.sh   # Offset Management 테스트
└── test_kafka.sh                # 기본 Producer/Consumer 테스트
```

## 🚀 빠른 시작

### 1. Kafka 서버 시작

**macOS (Homebrew 설치):**
```bash
/opt/homebrew/opt/kafka/bin/kafka-server-start /opt/homebrew/etc/kafka/server.properties &
```

**Linux (바이너리 설치):**
```bash
cd kafka_2.13-4.0.0
bin/kafka-server-start.sh config/server.properties &
```

### 2. 통합 테스트 실행

```bash
cd kafka_project
./run_cluster_tests.sh
```

### 3. 개별 테스트 실행

```bash
# Topic with partitions 테스트
./test_cluster_topics.sh

# Producer 설정 테스트
./test_producer_config.sh

# Consumer Groups 테스트
./test_consumer_groups.sh

# Offset Management 테스트
./test_offset_management.sh
```

## 📚 테스트 항목

### 1. Topic with Partitions
- Topic 생성 (replication-factor 3)
- Topic 상세 정보 조회
- 자동 생성 토픽 테스트

**관련 강의 슬라이드:** Topic with partitions

### 2. Producer 설정
- `compression.type=gzip`: 메시지 압축
- `partitioner.class=RoundRobinPartitioner`: 라운드 로빈 파티셔닝
- `linger.ms=100`: 버퍼링 시간
- `acks=all`: 모든 replica 확인

**관련 강의 슬라이드:** Producer with custom properties

### 3. Consumers and Consumer Groups
- 기본 Consumer (그룹 없이)
- Consumer Groups를 통한 로드 밸런싱
- 그룹별 메시지 분산 수신

**관련 강의 슬라이드:** Consumers and Consumer Groups

### 4. Offset Management
- Consumer Group 상태 조회
- Offset 리셋 (earliest, shift-by)
- 지연된 메시지 수신

**관련 강의 슬라이드:** Offset Management

## 🔧 클러스터 설정

3-node 클러스터 설정은 `cluster_setup_guide.md`를 참고하세요.

**주요 내용:**
- KRaft Quorum 설정 (Static/Dynamic)
- server.properties 구성
- 클러스터 초기화 및 시작

## 🛠️ 환경 설정

### macOS (Homebrew)
```bash
brew install kafka

# Kafka 명령어 경로
export PATH="/opt/homebrew/bin:$PATH"
```

### Linux
```bash
# Kafka 다운로드
wget https://dlcdn.apache.org/kafka/4.0.0/kafka_2.13-4.0.0.tgz
tar -xvf kafka_2.13-4.0.0.tgz
cd kafka_2.13-4.0.0
```

### Bootstrap 서버 설정
기본값은 `localhost:9092`입니다. 다른 서버를 사용하려면:

```bash
export BOOTSTRAP_SERVER=192.168.0.20:9092
./test_cluster_topics.sh
```

## 📝 주요 명령어 예시

### Topic 관리
```bash
# Topic 생성
kafka-topics --create --topic bigdata \
  --replication-factor 3 --partitions 3 \
  --bootstrap-server localhost:9092

# Topic 상세 정보
kafka-topics --describe --topic bigdata \
  --bootstrap-server localhost:9092

# Topic 리스트
kafka-topics --list --bootstrap-server localhost:9092
```

### Producer
```bash
# 기본 Producer
kafka-console-producer --topic test \
  --bootstrap-server localhost:9092

# 커스텀 설정 사용
kafka-console-producer --topic test \
  --producer.config config/producer.properties \
  --bootstrap-server localhost:9092
```

### Consumer
```bash
# 기본 Consumer (이후 메시지)
kafka-console-consumer --topic test \
  --bootstrap-server localhost:9092

# 처음부터 모든 메시지
kafka-console-consumer --topic test \
  --bootstrap-server localhost:9092 --from-beginning

# Consumer Group 사용
kafka-console-consumer --topic test \
  --group graduates \
  --bootstrap-server localhost:9092
```

### Consumer Groups 관리
```bash
# 그룹 목록
kafka-consumer-groups --list \
  --bootstrap-server localhost:9092

# 그룹 상세 정보
kafka-consumer-groups --describe \
  --group graduates \
  --bootstrap-server localhost:9092

# Offset 리셋 (earliest)
kafka-consumer-groups --topic test \
  --group graduates \
  --bootstrap-server localhost:9092 \
  --reset-offsets --to-earliest --execute
```

## ⚠️ 주의사항

1. **Topic 삭제**: Windows 서버에서 토픽 삭제 시 서버가 크래시될 수 있습니다.
2. **서버 재시작**: 서버를 재시작하려면 `logs` 디렉토리를 삭제하고 다시 포맷해야 합니다.
3. **클러스터 테스트**: 실제 3-node 클러스터 테스트는 `cluster_setup_guide.md`를 참고하세요.

## 📖 참고 자료

- [Apache Kafka 공식 문서](https://kafka.apache.org/documentation/)
- 강의 슬라이드 내용
- `cluster_setup_guide.md`: 클러스터 설정 상세 가이드

## ✅ 테스트 결과

기본 테스트 결과는 `KAFKA_TEST_RESULTS.md`를 참고하세요.

