# Kafka Windows 단일 머신 설정 가이드

강의 슬라이드 Page 11에 따른 Windows 단일 머신에서의 Kafka 서버 설정 가이드입니다.

## 📋 사전 준비사항

- Windows 운영체제
- Java JDK 설치
- Kafka 2.13-4.0.0 다운로드 및 압축 해제

## 🔧 설정 단계

### 1. server.properties 파일 수정

`config/server.properties` 파일을 편집합니다:

```properties
process.roles=broker,controller
node.id=0
listeners=PLAINTEXT://localhost:9092,CONTROLLER://localhost:9093
advertised.listeners=PLAINTEXT://localhost:9092,CONTROLLER://localhost:9093
log.dirs=C:/Server/kafka_2.13-4.0.0/logs
num.partitions=3
```

**⚠️ 중요**: `logs` 디렉토리를 먼저 생성해야 합니다!

```powershell
# logs 디렉토리 생성
mkdir C:\Server\kafka_2.13-4.0.0\logs
```

### 2. 클러스터 UUID 생성

PowerShell 또는 Command Prompt에서:

```powershell
cd C:\Server\kafka_2.13-4.0.0
.\bin\windows\kafka-storage.bat random-uuid
```

**출력 예시:**
```
Generated UUID: 3a4b5c6d-7e8f-9a0b-1c2d-3e4f5a6b7c8d
```

생성된 UUID를 복사하여 다음 단계에서 사용합니다.

### 3. 로그 디렉토리 포맷

생성한 UUID를 사용하여 로그 디렉토리를 포맷합니다:

```powershell
.\bin\windows\kafka-storage.bat format -t <generated-uuid> -c ..\..\config\server.properties --standalone
```

**예시:**
```powershell
.\bin\windows\kafka-storage.bat format -t 3a4b5c6d-7e8f-9a0b-1c2d-3e4f5a6b7c8d -c ..\..\config\server.properties --standalone
```

**⚠️ 주의**: `--standalone` 옵션은 단일 머신 설정에 필요합니다.

### 4. Kafka 서버 시작

```powershell
.\bin\windows\kafka-server-start.bat ..\..\config\server.properties
```

서버가 정상적으로 시작되면 다음과 같은 로그가 출력됩니다:
```
[INFO] Kafka version: 4.0.0
[INFO] Kafka commitId: ...
[INFO] Kafka startTimeMs: ...
```

## 🧪 테스트

### 5. Topic 생성 및 메시지 전송

**새 터미널 창에서:**

#### Topic 생성
```powershell
.\bin\windows\kafka-topics.bat --create --topic bigdata --partitions 3 --bootstrap-server localhost:9092
```

#### 메시지 전송
```powershell
.\bin\windows\kafka-console-producer.bat --topic bigdata --bootstrap-server localhost:9092
```

메시지를 입력하고 `CTRL + C`로 종료합니다.

**예시 입력:**
```
Hello Kafka
This is a test message
Big Data is awesome!
```

### 6. 메시지 읽기

**또 다른 터미널 창에서:**

```powershell
.\bin\windows\kafka-console-consumer.bat --topic bigdata --bootstrap-server localhost:9092 --from-beginning
```

**출력 예시:**
```
Hello Kafka
This is a test message
Big Data is awesome!
```

## 🛑 서버 중지

서버를 중지하려면:
- 서버가 실행 중인 터미널에서 `CTRL + C`를 누릅니다.
- 또는 별도 터미널에서:
  ```powershell
  .\bin\windows\kafka-server-stop.bat
  ```

## 📝 Linux/Mac 단일 머신 설정

Linux 또는 Mac에서 단일 머신 설정을 하려면:

### server.properties
```properties
process.roles=broker,controller
node.id=0
listeners=PLAINTEXT://localhost:9092,CONTROLLER://localhost:9093
advertised.listeners=PLAINTEXT://localhost:9092,CONTROLLER://localhost:9093
log.dirs=/home/bigdata/kafka_2.13-4.0.0/logs
num.partitions=3
```

### 명령어 (Linux/Mac)
```bash
# UUID 생성
bin/kafka-storage.sh random-uuid

# 로그 디렉토리 포맷
bin/kafka-storage.sh format -t <uuid> -c config/server.properties --standalone

# 서버 시작
bin/kafka-server-start.sh config/server.properties

# Topic 생성
bin/kafka-topics.sh --create --topic bigdata --partitions 3 --bootstrap-server localhost:9092

# 메시지 전송
bin/kafka-console-producer.sh --topic bigdata --bootstrap-server localhost:9092

# 메시지 읽기
bin/kafka-console-consumer.sh --topic bigdata --bootstrap-server localhost:9092 --from-beginning
```

## ⚠️ 주의사항

1. **Topic 삭제 시 주의**: Windows 서버에서 토픽 삭제 시 서버가 크래시될 수 있습니다.
2. **서버 재시작**: 서버를 재시작하려면:
   - `logs` 디렉토리 삭제
   - 로그 디렉토리 다시 포맷
   - 서버 시작

## 🔗 관련 문서

- [3-Node Cluster Setup Guide](./cluster_setup_guide.md)
- [Kafka Demo README](./kafka_demo/README.md)

