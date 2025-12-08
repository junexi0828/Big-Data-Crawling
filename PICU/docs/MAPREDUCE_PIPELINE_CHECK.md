# MapReduce 파이프라인 점검 보고서

## 📋 전체 파이프라인 흐름

```
1. Scrapy Spider (크롤링)
   ↓
2. Kafka Pipeline → Kafka 토픽 (cointicker.raw.*)
   ↓
3. Kafka Consumer → HDFS (/raw/YYYYMMDD/)
   ↓
4. MapReduce 정제 (run_cleaner.sh) → HDFS (/cleaned/YYYYMMDD/)
   ↓
5. DataLoader → MariaDB (raw_news, market_trends, fear_greed_index)
   ↓
6. Backend API → Frontend
```

## ✅ 연결 상태 점검 결과

### 1. 데이터 운반: Kafka → HDFS

**위치**: `worker-nodes/kafka/kafka_consumer.py`

**상태**: ✅ 정상 연결
- Kafka Consumer가 `cointicker.raw.*` 토픽 구독
- `HDFSUploadManager`를 통해 HDFS에 저장
- 저장 경로: `/raw/{source}/{YYYYMMDD}/`
- 자동 재시도 로직 포함

**코드 위치**:
```python
# kafka_consumer.py:324
success = self.upload_manager.save_to_hdfs(
    items=[data],
    source=source,
    date=datetime.now(),
)
```

### 2. 데이터 정제: MapReduce (run_cleaner.sh)

**위치**: `worker-nodes/mapreduce/run_cleaner.sh`

**상태**: ✅ 정상 연결
- 입력 경로: `/raw/*/{YYYYMMDD}/*`
- 출력 경로: `/cleaned/{YYYYMMDD}/cleaned_{YYYYMMDD}.json`
- Mapper/Reducer: `cleaner_mapper.py`, `cleaner_reducer.py`
- HADOOP_HOME 자동 감지 로직 포함

**실행 경로**:
1. `orchestrator.py` → `run_mapreduce()` → `run_cleaner.sh`
2. `MapReduceModule` → `run_cleaner()` → `run_cleaner.sh`
3. GUI Control Tab → `run_mapreduce()` → `run_cleaner.sh`

**문제점**: ⚠️ `orchestrator.py`에서 `capture_output=True` 사용 → launchctl 환경에서 "Bad file descriptor" 오류 가능

**수정 완료**: `stdout=subprocess.DEVNULL, stderr=subprocess.PIPE`로 변경

### 3. 데이터 적재: HDFS → MariaDB

**위치**: `scripts/run_pipeline.py`, `backend/services/data_loader.py`

**상태**: ✅ 정상 연결
- `DataLoader.load_from_hdfs()` 메서드 사용
- HDFS 경로: `/cleaned/{YYYYMMDD}/cleaned_{YYYYMMDD}.json`
- DB 테이블: `raw_news`, `market_trends`, `fear_greed_index`
- 중복 체크 포함

**실행 경로**:
1. `orchestrator.py` → `run_data_loader()` → `run_pipeline.py`
2. GUI Control Tab → `run_data_loader()` → `run_pipeline.py`

**문제점**: ⚠️ `orchestrator.py`에서 `capture_output=True` 사용 → launchctl 환경에서 "Bad file descriptor" 오류 가능

**수정 완료**: `stdout=subprocess.DEVNULL, stderr=subprocess.PIPE`로 변경

### 4. 전체 파이프라인 오케스트레이션

**위치**: `master-node/orchestrator.py`

**상태**: ✅ 정상 연결
- `run_full_pipeline()` 메서드로 전체 파이프라인 실행
- Step 1: `run_crawlers()` - 크롤링
- Step 2: `run_mapreduce()` - MapReduce 정제
- Step 3: `run_data_loader()` - DB 적재

**스케줄링**:
- 크롤링: 2분마다 (`schedule.every(2).minutes`)
- 전체 파이프라인: 5분마다 (`schedule.every(5).minutes`)
- 공포·탐욕 지수: 매일 자정 (`schedule.every().day.at("00:00")`)

## 🔍 모듈 간 연결 확인

### MapReduceModule ↔ Orchestrator

**상태**: ✅ 정상
- `MapReduceModule`은 독립적으로 실행 가능
- `orchestrator.py`는 직접 `run_cleaner.sh` 실행
- 두 경로 모두 정상 동작

### MapReduceModule ↔ GUI

**상태**: ✅ 정상
- GUI Control Tab에서 MapReduce 실행 가능
- `app.py`의 `run_mapreduce()` 메서드 사용
- 상태 모니터링: `MapReduceModule.get_status()` 사용

### DataLoader ↔ HDFSClient

**상태**: ✅ 정상
- `DataLoader`가 `HDFSClient.get_cleaned_path()` 사용
- HDFS 경로 자동 구성

## ⚠️ 발견된 문제점 및 수정 사항

### 1. launchctl 환경에서 stdout/stderr 처리

**문제**: `orchestrator.py`의 `run_mapreduce()`와 `run_data_loader()`에서 `capture_output=True` 사용 시 launchctl 서비스 환경에서 "Bad file descriptor" 오류 발생 가능

**수정**:
- `stdout=subprocess.DEVNULL`로 변경
- `stderr=subprocess.PIPE`로 에러만 캡처

### 2. MapReduce 상태 모니터링

**문제**: 대시보드에서 MapReduce 상태가 항상 `{"running": False}`로 표시됨

**수정**: `app.py`에서 `MapReduceModule.get_status()`를 직접 호출하도록 변경

## 📊 데이터 경로 확인

### HDFS 경로 구조

```
/raw/
  ├── upbit_trends/
  │   └── 20251208/
  │       └── upbit_trends_*.json
  ├── coinness/
  │   └── 20251208/
  │       └── coinness_*.json
  └── ...

/cleaned/
  └── 20251208/
      └── cleaned_20251208.json
```

### 로컬 임시 경로

```
worker-nodes/mapreduce/data/
  ├── input_20251208/
  │   └── *.json (HDFS에서 다운로드)
  └── output_20251208.json (정제 결과)
```

## ✅ 최종 점검 결과

| 단계 | 모듈 | 상태 | 연결 확인 |
|------|------|------|-----------|
| 1. 크롤링 | Scrapy Spider | ✅ | Kafka Pipeline 연결됨 |
| 2. 메시지 큐 | Kafka | ✅ | Consumer 연결됨 |
| 3. HDFS 저장 | Kafka Consumer | ✅ | HDFSUploadManager 연결됨 |
| 4. 데이터 정제 | MapReduce | ✅ | run_cleaner.sh 정상 동작 |
| 5. DB 적재 | DataLoader | ✅ | HDFSClient 연결됨 |
| 6. 오케스트레이션 | Orchestrator | ✅ | 전체 파이프라인 통합됨 |

## 🎯 권장 사항

1. **로그 모니터링**: MapReduce 실행 시 로그 파일 확인 (`logs/orchestrator.log`)
2. **HDFS 경로 확인**: 정제 전/후 데이터 경로 정확성 확인
3. **에러 처리**: MapReduce 실패 시 재시도 로직 추가 고려
4. **성능 최적화**: 대용량 데이터 처리 시 MapReduce 병렬화 고려

