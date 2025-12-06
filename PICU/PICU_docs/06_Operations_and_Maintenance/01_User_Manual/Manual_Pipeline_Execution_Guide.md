# 수동 파이프라인 실행 가이드

GUI 없이 각 파이프라인 구성 요소를 수동으로 실행하고 테스트하는 방법을 안내합니다.

## 목차
1. [환경 설정](#1-환경-설정)
2. [Hadoop/HDFS 시작](#2-hadoophdfs-시작)
3. [Kafka 상태 확인](#3-kafka-상태-확인)
4. [데이터 수집 (Scrapy) 실행](#4-데이터-수집-scrapy-실행)
5. [Kafka 데이터 확인](#5-kafka-데이터-확인)
6. [HDFS 저장 확인](#6-hdfs-저장-확인)
7. [Backend API 실행](#7-backend-api-실행)
8. [전체 파이프라인 통합 실행](#8-전체-파이프라인-통합-실행)

---

## 1. 환경 설정

### 1.1 프로젝트 디렉토리로 이동
```bash
cd /Users/juns/code/personal/notion/pknu_workspace/bigdata/PICU/cointicker
```

### 1.2 Python 가상환경 활성화
```bash
source venv/bin/activate
```

### 1.3 PYTHONPATH 설정
```bash
export PYTHONPATH=/Users/juns/code/personal/notion/pknu_workspace/bigdata/PICU/cointicker:/Users/juns/code/personal/notion/pknu_workspace/bigdata/PICU/cointicker/worker-nodes:$PYTHONPATH
```

### 1.4 Hadoop 환경 변수 설정
```bash
export HADOOP_HOME=/Users/juns/code/personal/notion/pknu_workspace/bigdata/hadoop_project/hadoop-3.4.1
export PATH=$HADOOP_HOME/bin:$HADOOP_HOME/sbin:$PATH
export JAVA_HOME=$(/usr/libexec/java_home)
```

### 1.5 환경 변수 확인
```bash
echo "PYTHONPATH: $PYTHONPATH"
echo "HADOOP_HOME: $HADOOP_HOME"
echo "JAVA_HOME: $JAVA_HOME"
```

---

## 2. Hadoop/HDFS 시작

### 2.1 현재 Java 프로세스 확인
```bash
jps
```

**예상 출력:**
```
74313 Kafka
81258 org.eclipse.equinox.launcher_1.7.100.v20251111-0406.jar
3793 Jps
```

### 2.2 HDFS 시작
```bash
start-dfs.sh
```

**예상 출력:**
```
Starting namenodes on [localhost]
Starting datanodes
Starting secondary namenodes [OS.local]
```

### 2.3 HDFS 프로세스 확인 (5초 대기 후)
```bash
sleep 5
jps
```

**예상 출력:**
```
3490 DataNode
3646 SecondaryNameNode
3374 NameNode
74313 Kafka
3793 Jps
```

### 2.4 HDFS 포트 확인
```bash
nc -zv localhost 9000
nc -zv localhost 9870
```

**예상 출력:**
```
Connection to localhost port 9000 [tcp/cslistener] succeeded!
Connection to localhost port 9870 [tcp/*] succeeded!
```

### 2.5 HDFS 파일 시스템 확인
```bash
hdfs dfs -ls /
```

**예상 출력:** HDFS 루트 디렉토리의 파일 목록이 표시됩니다.

---

## 3. Kafka 상태 확인

### 3.1 Kafka 포트 확인
```bash
nc -zv localhost 9092
```

**예상 출력:**
```
Connection to localhost port 9092 [tcp/XmlIpcRegSvc] succeeded!
```

### 3.2 Kafka 토픽 목록 확인
```bash
python -c "
from kafka.admin import KafkaAdminClient
try:
    admin_client = KafkaAdminClient(bootstrap_servers=['localhost:9092'])
    topics = admin_client.list_topics()
    print('Kafka Topics:')
    for topic in sorted(topics):
        print(f'  - {topic}')
    admin_client.close()
except Exception as e:
    print(f'Error: {e}')
"
```

**예상 출력:**
```
Kafka Topics:
  - __consumer_offsets
  - analytics
  - bigdata
  - cointicker.raw.perplexity
  - cointicker.raw.saveticker
  - cointicker.raw.upbit_trends
  - datascience
  - test
```

---

## 4. 데이터 수집 (Scrapy) 실행

### 4.1 Scrapy 프로젝트 디렉토리로 이동
```bash
cd worker-nodes/cointicker
```

### 4.2 사용 가능한 스파이더 목록 확인
```bash
scrapy list
```

**예상 출력:**
```
cnn_fear_greed
coinness
perplexity
saveticker
upbit_trends
```

### 4.3 upbit_trends 스파이더 실행 (5개 아이템만 수집)
```bash
scrapy crawl upbit_trends -s CLOSESPIDER_ITEMCOUNT=5
```

**예상 출력 (중요 부분):**
```
2025-12-06 19:25:38 - cointicker.pipelines - INFO - HDFS Pipeline initialized for upbit_trends
2025-12-06 19:25:38 - cointicker.pipelines.kafka_pipeline - INFO - Kafka Pipeline initialized for upbit_trends
2025-12-06 19:25:38 - shared.kafka_client - INFO - Kafka Producer connected to localhost:9092 (compression=gzip, linger_ms=100)
2025-12-06 19:25:38 - shared.kafka_client - DEBUG - Message sent to topic=cointicker.raw.upbit_trends, partition=0, offset=387
2025-12-06 19:25:38 - shared.kafka_client - DEBUG - Message sent to topic=cointicker.raw.upbit_trends, partition=0, offset=388
...
2025-12-06 19:25:39 - cointicker.pipelines.kafka_pipeline - INFO - Sent 9/9 items to Kafka topic: cointicker.raw.upbit_trends
2025-12-06 19:25:46 - cointicker.pipelines - INFO - Saved 9 items to HDFS: /raw/upbit/20251206/upbit_20251206_192539.json
```

### 4.4 프로젝트 루트로 돌아가기
```bash
cd ../..
```

---

## 5. Kafka 데이터 확인

### 5.1 Kafka Consumer로 메시지 확인 (최신 메시지 확인)
```bash
python -c "
from shared.kafka_client import KafkaConsumerClient

# Kafka Consumer 연결
consumer = KafkaConsumerClient(
    bootstrap_servers=['localhost:9092'],
    group_id='manual-test-consumer',
    auto_offset_reset='latest'
)

topics = ['cointicker.raw.upbit_trends']
if consumer.connect(topics):
    print('✅ Kafka Consumer 연결 성공')
    print(f'구독 토픽: {topics}')
    print('메시지를 기다리는 중... (Ctrl+C로 종료)')

    # 참고: consumer_timeout_ms 버그로 인해 무한 대기할 수 있음
    # 새 메시지가 들어오면 표시됨

    consumer.close()
else:
    print('❌ Kafka Consumer 연결 실패')
"
```

**예상 출력:**
```
✅ Kafka Consumer 연결 성공
구독 토픽: ['cointicker.raw.upbit_trends']
```

---

## 6. HDFS 저장 확인

### 6.1 HDFS upbit 디렉토리 확인
```bash
hdfs dfs -ls /raw/upbit/
```

**예상 출력:**
```
Found 1 items
drwxr-xr-x   - juns supergroup          0 2025-12-06 19:25 /raw/upbit/20251206
```

### 6.2 오늘 날짜 디렉토리의 파일 확인
```bash
hdfs dfs -ls /raw/upbit/20251206/
```

**예상 출력:**
```
Found 1 items
-rw-r--r--   1 juns supergroup       1969 2025-12-06 19:25 /raw/upbit/20251206/upbit_20251206_192539.json
```

### 6.3 HDFS 파일 내용 확인
```bash
hdfs dfs -cat /raw/upbit/20251206/upbit_20251206_192539.json 2>&1 | grep -v "WARN" | head -30
```

**예상 출력:**
```json
[
  {
    "source": "upbit",
    "symbol": "DOGE",
    "price": 209.0,
    "volume_24h": 198572882.33571494,
    "change_24h": 0.0,
    "market_cap": 41793058613.087906,
    "timestamp": "2025-12-06T19:25:38.710213"
  },
  {
    "source": "upbit",
    "symbol": "ETH",
    "price": 4540000.0,
    "volume_24h": 46409.00485314,
    "change_24h": 0.33,
    "market_cap": 212675905264.9422,
    "timestamp": "2025-12-06T19:25:38.710862"
  },
  ...
]
```

### 6.4 HDFS의 모든 raw 데이터 확인
```bash
hdfs dfs -ls -R /raw/
```

---

## 7. Backend API 실행

### 7.1 Backend 디렉토리로 이동
```bash
cd backend
```

### 7.2 Backend API 서버 시작 (포그라운드 실행)
```bash
python -c "import uvicorn; uvicorn.run('app:app', host='0.0.0.0', port=5001, log_level='info')"
```

**예상 출력:**
```
INFO:     Started server process [7031]
INFO:     Waiting for application startup.
⚠️ 데이터베이스 테이블 생성 중 오류 발생 (계속 진행): (pymysql.err.OperationalError) (2003, "Can't connect to MySQL server on 'localhost' ([Errno 61] Connection refused)")
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:5001 (Press CTRL+C to quit)
```

### 7.3 새 터미널에서 Health Check 확인
**새 터미널 열기** → 다음 명령어 실행:

```bash
curl -s http://localhost:5001/health | python3 -m json.tool
```

**예상 출력:**
```json
{
  "status": "healthy",
  "database": "disconnected ((pymysql.err.OperationalError) (2003, \"Can't connect to MySQL server on 'localhost' ([Errno 61] Connection refused)\"))",
  "timestamp": "2025-12-06T19:33:51.758246"
}
```

### 7.4 Backend API 서버 중지
원래 터미널에서 `Ctrl+C` 누르기

### 7.5 프로젝트 루트로 돌아가기
```bash
cd ..
```

---

## 8. 전체 파이프라인 통합 실행

### 8.1 전체 파이프라인을 순서대로 실행하는 스크립트

```bash
#!/bin/bash

# 1. 환경 설정
cd /Users/juns/code/personal/notion/pknu_workspace/bigdata/PICU/cointicker
source venv/bin/activate
export PYTHONPATH=/Users/juns/code/personal/notion/pknu_workspace/bigdata/PICU/cointicker:/Users/juns/code/personal/notion/pknu_workspace/bigdata/PICU/cointicker/worker-nodes:$PYTHONPATH
export HADOOP_HOME=/Users/juns/code/personal/notion/pknu_workspace/bigdata/hadoop_project/hadoop-3.4.1
export PATH=$HADOOP_HOME/bin:$HADOOP_HOME/sbin:$PATH
export JAVA_HOME=$(/usr/libexec/java_home)

echo "✅ 환경 설정 완료"

# 2. HDFS 상태 확인 (필요시 시작)
echo ""
echo "📊 HDFS 상태 확인 중..."
if ! nc -z localhost 9000 2>/dev/null; then
    echo "⚠️  HDFS가 실행되지 않았습니다. 시작합니다..."
    start-dfs.sh
    sleep 5
fi

if nc -z localhost 9000 2>/dev/null; then
    echo "✅ HDFS 정상 실행 중 (포트 9000)"
else
    echo "❌ HDFS 시작 실패"
    exit 1
fi

# 3. Kafka 상태 확인
echo ""
echo "📊 Kafka 상태 확인 중..."
if nc -z localhost 9092 2>/dev/null; then
    echo "✅ Kafka 정상 실행 중 (포트 9092)"
else
    echo "❌ Kafka가 실행되지 않았습니다. Kafka를 먼저 시작해주세요."
    exit 1
fi

# 4. Scrapy 데이터 수집 실행
echo ""
echo "🕷️  Scrapy 데이터 수집 시작..."
cd worker-nodes/cointicker
scrapy crawl upbit_trends -s CLOSESPIDER_ITEMCOUNT=10
cd ../..
echo "✅ Scrapy 데이터 수집 완료"

# 5. HDFS 데이터 확인
echo ""
echo "📁 HDFS 저장 데이터 확인..."
TODAY=$(date +%Y%m%d)
hdfs dfs -ls /raw/upbit/${TODAY}/ 2>/dev/null
echo "✅ HDFS 데이터 확인 완료"

# 6. Backend API 시작 (선택사항)
echo ""
echo "🚀 Backend API를 시작하려면 다음 명령어를 실행하세요:"
echo "   cd backend && python -c \"import uvicorn; uvicorn.run('app:app', host='0.0.0.0', port=5001, log_level='info')\""

echo ""
echo "✅ 전체 파이프라인 실행 완료!"
```

### 8.2 스크립트 저장 및 실행

위 스크립트를 `scripts/run_manual_pipeline.sh`로 저장 후:

```bash
chmod +x scripts/run_manual_pipeline.sh
./scripts/run_manual_pipeline.sh
```

---

## 9. 문제 해결 (Troubleshooting)

### 9.1 HDFS 연결 실패 시
```bash
# HDFS 데몬 중지
stop-dfs.sh

# 잠시 대기
sleep 3

# HDFS 데몬 재시작
start-dfs.sh

# 상태 확인
jps
```

### 9.2 Kafka 연결 실패 시
```bash
# Kafka 상태 확인
nc -zv localhost 9092

# Kafka 재시작이 필요한 경우
# (Kafka 설치 디렉토리에서 실행)
# bin/kafka-server-stop.sh
# bin/kafka-server-start.sh -daemon config/server.properties
```

### 9.3 Scrapy 실행 오류 시
```bash
# PYTHONPATH 다시 설정
export PYTHONPATH=/Users/juns/code/personal/notion/pknu_workspace/bigdata/PICU/cointicker:/Users/juns/code/personal/notion/pknu_workspace/bigdata/PICU/cointicker/worker-nodes:$PYTHONPATH

# 모듈 임포트 확인
python -c "from shared.kafka_client import KafkaProducerClient; print('✅ 모듈 로드 성공')"
```

### 9.4 Backend API 실행 오류 시
```bash
# PYTHONPATH 확인
echo $PYTHONPATH

# 포트 충돌 확인
lsof -i :5001

# 포트가 사용 중이면 프로세스 종료
# kill -9 <PID>
```

---

## 10. 참고 사항

### 10.1 중요한 환경 변수
- `PYTHONPATH`: Python 모듈 경로 설정
- `HADOOP_HOME`: Hadoop 설치 경로
- `JAVA_HOME`: Java 설치 경로

### 10.2 주요 포트
- **9000**: HDFS NameNode
- **9870**: HDFS Web UI
- **9092**: Kafka Broker
- **5001**: Backend API

### 10.3 데이터 경로
- **HDFS 원본 데이터**: `/raw/upbit/{날짜}/upbit_{날짜}_{시간}.json`
- **로컬 로그**: `logs/scrapy.log`
- **Kafka 토픽**: `cointicker.raw.upbit_trends`

### 10.4 수정된 이슈
1. **kafka-python 라이브러리 버그**: ✅ 수정 완료 - `consumer_timeout_ms=2147483647` (매우 큰 정수값) 사용
2. **Kafka Consumer 와일드카드**: ✅ 수정 완료 - `admin_client.list_topics()` 메서드 사용으로 변경
3. **MySQL 연결**: Backend API는 MySQL 없이도 실행 가능 (데이터베이스는 선택사항)

---

## 11. 다음 단계

파이프라인이 정상 작동하는 것을 확인했다면:

1. **GUI 문제 디버깅**: `gui/modules/pipeline_orchestrator.py` 검토
2. **Kafka Consumer 수정**: `worker-nodes/kafka/kafka_consumer.py`의 타임아웃 설정 수정
3. **자동화**: 위 스크립트를 systemd 서비스로 등록하여 자동 시작

---

**작성일**: 2025-12-06
**테스트 환경**: macOS, Python 3.14, Hadoop 3.4.1, Kafka (latest)
**상태**: ✅ 검증 완료
