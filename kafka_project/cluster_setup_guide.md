# Kafka 3-Node Cluster Setup Guide

강의 슬라이드를 기반으로 한 Kafka 3-Node 클러스터 설정 가이드입니다.

## 📋 사전 준비사항

### 1. IP 주소 확인
각 클러스터 노드의 IP 주소를 확인합니다:
```bash
hostname -I
```

**예시 노드 구성:**
- `bigpie2`: node.id=0, IP: 192.168.0.20
- `bigpie3`: node.id=1, IP: 192.168.0.22
- `bigpie4`: node.id=2, IP: 192.168.0.23

### 2. /etc/hosts 파일 편집 (선택사항)
각 노드에서 `/etc/hosts` 파일을 편집하여 호스트명을 IP에 매핑:
```bash
sudo nano /etc/hosts
```

**추가할 내용:**
```
192.168.0.20 bigpie2
192.168.0.22 bigpie3
192.168.0.23 bigpie4
```

## 🔧 1. Java 및 Kafka 설치

### Java JDK 설치
```bash
sudo apt install default-jdk
```

### Kafka 바이너리 다운로드 및 압축 해제
```bash
# Kafka 다운로드
wget https://dlcdn.apache.org/kafka/4.0.0/kafka_2.13-4.0.0.tgz

# 압축 해제
tar -xvf kafka_2.13-4.0.0.tgz

# Kafka 디렉토리로 이동
cd kafka_2.13-4.0.0

# logs 디렉토리 생성
mkdir logs
```

## ⚙️ 2. KRaft Quorum 설정 방식

### Static Quorum Setup (권장)
`controller.quorum.voters` 사용 - 모든 노드의 정보를 명시적으로 설정

### Dynamic Quorum Setup
`controller.quorum.bootstrap.servers` 사용 - 부트스트랩 방식

## 📝 3. server.properties 파일 설정

각 노드별로 `config/server.properties` 파일을 편집합니다.

### Node 0 (bigpie2) 설정
```properties
process.roles=broker,controller
node.id=0
#controller.quorum.bootstrap.servers=localhost:9093
controller.quorum.voters=0@192.168.0.20:9093,1@192.168.0.22:9093,2@192.168.0.23:9093
listeners=PLAINTEXT://192.168.0.20:9092,CONTROLLER://192.168.0.20:9093
advertised.listeners=PLAINTEXT://192.168.0.20:9092,CONTROLLER://192.168.0.20:9093
log.dirs=/home/bigdata/kafka_2.13-4.0.0/logs
num.partitions=3
```

### Node 1 (bigpie3) 설정
```properties
process.roles=broker,controller
node.id=1
#controller.quorum.bootstrap.servers=localhost:9093
controller.quorum.voters=0@192.168.0.20:9093,1@192.168.0.22:9093,2@192.168.0.23:9093
listeners=PLAINTEXT://192.168.0.22:9092,CONTROLLER://192.168.0.22:9093
advertised.listeners=PLAINTEXT://192.168.0.22:9092,CONTROLLER://192.168.0.22:9093
log.dirs=/home/bigdata/kafka_2.13-4.0.0/logs
num.partitions=3
```

### Node 2 (bigpie4) 설정
```properties
process.roles=broker,controller
node.id=2
#controller.quorum.bootstrap.servers=localhost:9093
controller.quorum.voters=0@192.168.0.20:9093,1@192.168.0.22:9093,2@192.168.0.23:9093
listeners=PLAINTEXT://192.168.0.23:9092,CONTROLLER://192.168.0.23:9093
advertised.listeners=PLAINTEXT://192.168.0.23:9092,CONTROLLER://192.168.0.23:9093
log.dirs=/home/bigdata/kafka_2.13-4.0.0/logs
num.partitions=3
```

## 🚀 4. 클러스터 초기화 및 시작

### Step 3: UUID 생성 및 로그 디렉토리 포맷 (bigpie2에서만)
```bash
# UUID 생성 (클러스터 ID로 사용)
bin/kafka-storage.sh random-uuid
# 출력된 UUID를 복사하여 Step 4에서 사용

# 로그 디렉토리 포맷
bin/kafka-storage.sh format -t <generated-uuid> -c config/server.properties
```

### Step 4: 동일한 cluster-id로 로그 디렉토리 포맷 (bigpie3, bigpie4)
```bash
# bigpie2에서 생성한 동일한 UUID 사용
bin/kafka-storage.sh format -t <same-uuid> -c config/server.properties
```

### Step 5: 모든 노드에서 서버 시작
```bash
bin/kafka-server-start.sh config/server.properties
```

### Step 6: Topic 리스트 확인
각 노드에서 로컬 브로커의 IP를 bootstrap-server로 사용:
```bash
# bigpie2
bin/kafka-topics.sh --list --bootstrap-server 192.168.0.20:9092

# bigpie3
bin/kafka-topics.sh --list --bootstrap-server 192.168.0.22:9092

# bigpie4
bin/kafka-topics.sh --list --bootstrap-server 192.168.0.23:9092
```

### Step 7: 서버 중지
모든 노드에서:
```bash
bin/kafka-server-stop.sh
```

## ⚠️ 주의사항

1. **Topic 삭제 시 주의**: Windows 서버에서 토픽 삭제 시 서버가 크래시될 수 있습니다.
2. **서버 재시작**: 서버를 재시작하려면 `logs` 디렉토리를 삭제하고 로그 디렉토리를 다시 포맷해야 합니다.

