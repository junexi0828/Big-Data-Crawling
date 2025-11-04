# Kafka 테스트 결과

## ✅ 강의 슬라이드에 따른 테스트 완료

### 1. Kafka 서버 시작
```bash
# Kafka 서버 시작 (백그라운드)
/opt/homebrew/opt/kafka/bin/kafka-server-start /opt/homebrew/etc/kafka/server.properties &
```
**결과**: ✅ Kafka 서버 정상 시작 (포트 9092)

### 2. Topic 관리

#### Topic 생성
```bash
kafka-topics --create --topic bigdata --bootstrap-server localhost:9092
```
**결과**: ✅ Created topic bigdata.

#### Topic 리스트
```bash
kafka-topics --list --bootstrap-server localhost:9092
```
**결과**: ✅ bigdata

#### Topic 상세 정보
```bash
kafka-topics --describe --topic bigdata --bootstrap-server localhost:9092
```
**결과**: ✅
- Topic: bigdata
- PartitionCount: 1
- ReplicationFactor: 1
- Leader: 1

### 3. 메시지 송수신

#### Producer로 메시지 전송
```bash
echo -e "Hello Kafka\nThis is a test message\nBig Data is awesome!" | \
  kafka-console-producer --topic bigdata --bootstrap-server localhost:9092
```
**결과**: ✅ 메시지 전송 성공

#### Consumer로 메시지 수신
```bash
kafka-console-consumer --topic bigdata --bootstrap-server localhost:9092 \
  --from-beginning --max-messages 3
```
**결과**: ✅
```
Hello Kafka
This is a test message
Big Data is awesome!
Processed a total of 3 messages
```

## 📝 macOS vs Windows 명령어 차이

### Windows (강의 슬라이드)
- `bin\windows\kafka-topics.sh`
- `bin\windows\kafka-server-start.sh`

### macOS (brew 설치)
- `/opt/homebrew/bin/kafka-topics`
- `/opt/homebrew/bin/kafka-console-producer`
- `/opt/homebrew/bin/kafka-console-consumer`

## 🎯 모든 테스트 성공!

### 다음 단계
1. Kafka 서버 중지: `kafka-server-stop.sh` 또는 `CTRL+C`
2. Topic 삭제 (선택): `kafka-topics --delete --topic bigdata --bootstrap-server localhost:9092`

