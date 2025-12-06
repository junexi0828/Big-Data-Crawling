# 하둡 설계 및 파이프라인 연결 로직 검토 보고서

## 📋 개요

PICU 프로젝트의 하둡 설계, 파이프라인 연결 로직, 하둡 실행 로직을 종합적으로 검토합니다.

## 🏗️ 하둡 설계 구조

### 1. 계층 구조

```
┌─────────────────────────────────────────┐
│         Scrapy Spider (데이터 수집)      │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│      HDFSPipeline (Scrapy Pipeline)     │
│  - 배치 처리 (batch_size=100)            │
│  - 로컬 임시 파일 저장                   │
│  - HDFS 업로드 시도                      │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│         HDFSClient (shared/)            │
│  - Java 기반 (pyarrow.fs) 우선           │
│  - CLI 폴백 (hdfs dfs 명령어)            │
│  - 자동 환경 설정 (setup_hadoop_env)    │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│      HDFSManager (GUI 모듈)             │
│  - HADOOP_HOME 자동 감지                 │
│  - 단일/클러스터 모드 설정               │
│  - 데몬 시작/중지 관리                   │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│      Hadoop/HDFS 서비스                 │
│  - NameNode (포트: 9000, 웹 UI: 9870)   │
│  - DataNode                              │
│  - SecondaryNameNode                     │
└─────────────────────────────────────────┘
```

### 2. 주요 컴포넌트

#### 2.1. HDFSPipeline (`worker-nodes/cointicker/pipelines.py`)

**역할**: Scrapy 아이템을 HDFS에 저장하는 파이프라인

**동작 흐름**:

1. `open_spider()`: HDFSClient 초기화 (namenode 설정에서 가져옴)
2. `process_item()`: 아이템을 배치에 추가 (배치 크기: 100)
3. `_save_batch()`:
   - 로컬 임시 파일에 저장 (`data/temp/YYYYMMDD/`)
   - HDFS 경로 생성 (`/raw/{source}/{YYYYMMDD}/`)
   - HDFS 디렉토리 생성
   - HDFS 업로드 시도
   - 성공 시 로컬 파일 삭제, 실패 시 로컬 파일 유지
4. `close_spider()`: 남은 배치 저장

**특징**:

- HDFS 실패 시에도 로컬 파일에 저장하여 데이터 손실 방지
- 배치 처리로 성능 최적화
- HDFS 미실행 시에도 정상 동작 (로컬 저장)

#### 2.2. HDFSClient (`shared/hdfs_client.py`)

**역할**: HDFS와의 실제 통신 담당

**구현 방식**:

1. **Java 기반 (우선)**: `pyarrow.fs.HadoopFileSystem` 사용
   - 장점: 네이티브 성능, Java FileSystem API 직접 사용
   - 단점: pyarrow 설치 필요, HDFS 서비스 실행 필요
2. **CLI 폴백**: `hdfs dfs` 명령어 사용
   - 장점: pyarrow 없이도 동작, 간단한 구현
   - 단점: subprocess 오버헤드, HDFS 서비스 실행 필요

**자동 환경 설정**:

- `setup_hadoop_env()`: HADOOP_HOME 자동 감지 및 PATH 설정
- `get_hadoop_home()`: 여러 경로에서 Hadoop 자동 검색
  1. HADOOP_HOME 환경변수
  2. cluster_config.yaml 설정 파일
  3. hadoop 명령어 위치에서 추론
  4. 프로젝트 인접 경로 (`hadoop_project/hadoop-*`)
  5. 표준 설치 경로 (`/opt/hadoop`, `/usr/local/hadoop`, etc.)

**주요 메서드**:

- `put()`: 로컬 → HDFS 업로드
- `get()`: HDFS → 로컬 다운로드
- `mkdir()`: HDFS 디렉토리 생성
- `exists()`: HDFS 경로 존재 확인
- `get_raw_path()`: 원시 데이터 경로 생성 (`/raw/{source}/{YYYYMMDD}`)

#### 2.3. HDFSManager (`gui/modules/managers/hdfs_manager.py`)

**역할**: HDFS 서비스 관리 및 설정

**주요 기능**:

1. **HADOOP_HOME 자동 감지** (`check_and_start()`):

   - 프로젝트 루트 기반 경로 검색
   - 표준 설치 경로 검색
   - GUI와 테스트 스크립트에서 동일한 로직 사용

2. **모드 설정**:

   - **단일 노드 모드** (`setup_single_node_mode()`):
     - `core-site.xml`: `fs.defaultFS = hdfs://localhost:9000`
     - `hdfs-site.xml`: `dfs.replication = 1`
   - **클러스터 모드** (`setup_cluster_mode()`):
     - `core-site.xml`: 클러스터 namenode URL
     - `hdfs-site.xml`: `dfs.replication = 3` (기본값)
     - `workers` 파일: 워커 노드 목록
     - `master` 파일: SecondaryNameNode 호스트

3. **데몬 시작**:

   - **SSH 기반** (`start-dfs.sh`): 클러스터 모드
   - **직접 시작** (`start_daemons_direct()`): 단일 노드 모드
     - NameNode 포맷 (필요시)
     - NameNode 데몬 시작
     - DataNode 데몬 시작
     - SecondaryNameNode 데몬 시작
     - 포트 확인 (9000, 9870)

4. **실행 상태 확인** (`check_running()`):
   - 포트 체크 (9000: NameNode, 9870: 웹 UI)
   - 소켓 연결 테스트

## 🔄 파이프라인 연결 로직

### 1. Scrapy → HDFS 파이프라인

**설정 위치**: `worker-nodes/cointicker/settings.py`

```python
ITEM_PIPELINES = {
    "cointicker.pipelines.ValidationPipeline": 300,
    "cointicker.pipelines.DuplicatesPipeline": 400,
    "cointicker.pipelines.HDFSPipeline": 500,
    "cointicker.pipelines.kafka_pipeline.KafkaPipeline": 600,
}
```

**파이프라인 순서**:

1. ValidationPipeline (300): 데이터 유효성 검사
2. DuplicatesPipeline (400): 중복 제거
3. HDFSPipeline (500): HDFS 저장
4. KafkaPipeline (600): Kafka 전송 (선택적)

**HDFS 설정**:

- `HDFS_NAMENODE`: 기본값 `hdfs://localhost:9000`
- 환경변수나 설정 파일로 오버라이드 가능

### 2. HDFS → MapReduce 파이프라인

**데이터 흐름**:

1. HDFS에 원시 데이터 저장: `/raw/{source}/{YYYYMMDD}/`
2. MapReduce 작업 실행: `run_cleaner.sh` 또는 `run_mapreduce.sh`
3. 정제된 데이터 저장: `/cleaned/{YYYYMMDD}/`
4. DataLoader가 정제된 데이터를 DB에 적재

**MapReduce 스크립트**:

- **로컬 모드**: `worker-nodes/mapreduce/run_cleaner.sh`
- **클러스터 모드**: `scripts/run_mapreduce.sh` (HDFS 필요)

### 3. Kafka → HDFS 파이프라인 (선택적)

**KafkaConsumerService** (`worker-nodes/kafka/kafka_consumer.py`):

- Kafka 메시지 수신
- HDFSClient를 사용하여 HDFS에 저장
- HDFSPipeline과 동일한 경로 구조 사용

## ⚙️ 하둡 실행 로직

### 1. 자동 시작 흐름 (`HDFSManager.check_and_start()`)

```
1. HDFS 실행 상태 확인 (포트 체크)
   ├─ 실행 중 → 종료 (성공 반환)
   └─ 미실행 → 다음 단계

2. 클러스터 설정 확인
   ├─ 클러스터 설정 있음 → 멀티노드 모드 시도
   │   ├─ SSH 연결 성공 → 클러스터 모드 설정
   │   └─ SSH 연결 실패 → 사용자 확인 → 단일 노드 모드
   └─ 클러스터 설정 없음 → 단일 노드 모드

3. HADOOP_HOME 자동 감지
   ├─ 환경변수 확인
   ├─ 프로젝트 인접 경로 검색
   └─ 표준 설치 경로 검색

4. 모드 설정
   ├─ 단일 노드 모드: setup_single_node_mode()
   └─ 클러스터 모드: setup_cluster_mode()

5. SSH 연결 확인
   ├─ SSH 성공 → start-dfs.sh 실행
   └─ SSH 실패 → start_daemons_direct() 실행

6. 데몬 시작
   ├─ NameNode 포맷 (필요시)
   ├─ NameNode 시작
   ├─ DataNode 시작
   ├─ SecondaryNameNode 시작
   └─ 포트 확인 (최대 30초 대기)

7. 결과 반환
   ├─ 성공 → {"success": True, "message": "..."}
   └─ 실패 → {"success": False, "error": "..."}
```

### 2. 단일 노드 모드 데몬 시작 (`start_daemons_direct()`)

**단계**:

1. HADOOP_HOME 경로 검증
2. NameNode 포맷 (디렉토리 없거나 비어있을 때)
3. NameNode 데몬 시작 (`hdfs --daemon start namenode`)
4. DataNode 데몬 시작 (`hdfs --daemon start datanode`)
5. SecondaryNameNode 데몬 시작 (`hdfs --daemon start secondarynamenode`)
6. 포트 확인 (9000, 9870)
7. **Safe Mode 해제 대기** (`hdfs dfsadmin -safemode wait`) - ✅ 추가됨

**특징**:

- `subprocess.Popen`으로 백그라운드 실행
- `start_new_session=True`로 세션 분리
- 환경변수 전달 (HADOOP_HOME, PATH 등)
- 타임아웃 설정 (30초)

### 3. 환경 변수 설정

**자동 설정** (`shared/path_utils.py`):

- `setup_hadoop_env()`: 모듈 import 시 자동 실행
- HADOOP_HOME 자동 감지 및 설정
- PATH에 `$HADOOP_HOME/bin`, `$HADOOP_HOME/sbin` 추가

**수동 설정**:

- 환경변수 `HADOOP_HOME` 직접 설정
- `cluster_config.yaml`에 `hadoop.home` 설정

## 🔍 발견된 문제점 및 개선 사항

### 1. Syntax Error (수정 완료)

**위치**: `run_all_tests.sh` 883번 줄
**문제**: Kafka 브로커 확인 블록의 `fi` 누락
**수정**: 747번 줄에 `fi` 추가

### 2. HDFS 미실행 시 동작

**현재 상태**: ✅ 개선 완료 (Self-healing 기능 구현)

- HDFS 실패 시 로컬 임시 파일에 저장
- **Exponential Backoff 재시도 로직** 구현
- **에러 분류 및 처리** (일시적 vs 영구적 오류)
- **HDFS 재연결 시 자동 업로드** 기능 구현
- 스파이더는 정상 동작

**구현 내용**:

1. **HDFSUploadManager 모듈 생성** (`shared/hdfs_upload_manager.py`)

   - Exponential Backoff 재시도 로직 (2초 → 4초 → 8초)
   - 에러 분류: 일시적 오류 (네트워크, HDFS 일시 다운) vs 영구적 오류 (설정 오류, 권한 문제)
   - HDFS 상태 확인 및 자동 업로드 스레드
   - 대기 중인 파일 관리 및 자동 업로드

2. **HDFSPipeline 통합** (`worker-nodes/cointicker/pipelines.py`)

   - HDFSUploadManager를 사용하여 자동 재업로드 기능 통합
   - Spider 시작 시 자동 업로드 스레드 시작
   - Spider 종료 시 자동 업로드 스레드 중지

3. **KafkaConsumer 통합** (`worker-nodes/kafka/kafka_consumer.py`)

   - HDFSUploadManager를 사용하여 자동 재업로드 기능 통합
   - Consumer 시작 시 자동 업로드 스레드 시작
   - Consumer 종료 시 자동 업로드 스레드 중지

4. **설정 추가** (`worker-nodes/cointicker/settings.py`)
   - `HDFS_MAX_RETRIES`: 최대 재시도 횟수 (기본값: 3)
   - `HDFS_INITIAL_DELAY`: 초기 재시도 지연 시간 (기본값: 2.0초)
   - `HDFS_BACKOFF_FACTOR`: 재시도 간격 증가 배수 (기본값: 2.0)
   - `HDFS_HEALTH_CHECK_INTERVAL`: HDFS 상태 확인 간격 (기본값: 300초)

**동작 방식**:

1. **데이터 저장 시도**:

   - HDFS에 데이터 저장 시도
   - 실패 시 Exponential Backoff로 재시도 (2초, 4초, 8초)
   - 재시도 실패 시 로컬 임시 파일에 저장하고 대기 목록에 추가

2. **에러 분류**:

   - **일시적 오류** (Connection refused, Timeout 등): 대기 목록에 추가, 자동 재업로드 시도
   - **영구적 오류** (Permission denied, Invalid configuration 등): 즉시 중단, 관리자 알림 필요

3. **자동 업로드**:
   - HDFS 연결 실패 상태일 때 주기적으로 (5분마다) HDFS 상태 확인
   - 연결 복구 시 대기 중인 파일들을 순차적으로 업로드
   - 업로드 완료된 파일은 자동 삭제

**개선 효과**:

- ✅ **Self-healing 구조**: 시스템이 스스로 문제를 해결
- ✅ **데이터 손실 방지**: HDFS 다운 타임 중에도 데이터 수집 계속
- ✅ **자동 복구**: HDFS 재연결 시 자동으로 대기 파일 업로드
- ✅ **안정성 향상**: 일시적 네트워크 오류에 대한 자동 재시도
- ✅ **관리 편의성**: 별도 스크립트 관리 불필요

### 3. HADOOP_HOME 자동 감지 및 캐싱 (✅ 개선 완료)

**현재 상태**: ✅ 개선됨

- GUI와 테스트 스크립트에서 동일한 로직 사용
- 여러 경로에서 자동 검색
- **캐싱 메커니즘 추가**: 한 번 감지한 경로를 메모리 및 설정 파일에 저장
- **설정 파일 저장**: `cluster_config.yaml`의 `hadoop.cached_home`에 저장

**구현 내용**:

1. **메모리 캐싱**: `_cached_hadoop_home` 변수에 저장
2. **설정 파일 캐싱**: `ConfigManager`를 통해 `cluster_config.yaml`에 저장
3. **우선순위**: 환경변수 → 캐시된 경로 → 자동 검색
4. **자동 저장**: 자동 감지된 경로는 자동으로 캐시에 저장

**개선 효과**:

- HADOOP_HOME 감지 속도 향상 (캐시된 경로 우선 사용)
- 설정 파일에 경로 저장으로 재시작 후에도 유지
- 사용자가 수동으로 설정 파일에 경로 지정 가능

### 3-1. 환경 의존성 및 권한 문제 (✅ 해결 완료)

**문제점**:

- HADOOP_HOME 자동 감지가 실패할 수 있음
- Hadoop 관련 디렉토리(로그, 데이터 등)에 대한 현재 사용자의 쓰기 권한이 없을 경우 데몬 시작에 실패할 수 있음
- 스크립트를 실행하는 사용자 계정이 Hadoop을 설치하고 HDFS를 포맷한 사용자와 동일한지 확인 필요

**해결 방법**:

1. **권한 확인 로직 추가** (`_check_hadoop_permissions()`):

   - `logs/` 디렉토리 쓰기 권한 확인
   - `tmp/` 디렉토리 쓰기 권한 확인
   - `tmp/dfs/` 디렉토리 쓰기 권한 확인
   - 현재 사용자 계정 정보 출력

2. **권한 확인 시점**:

   - `check_and_start()`: HADOOP_HOME 확인 후 권한 확인
   - `start_daemons_direct()`: 데몬 시작 전 권한 확인

3. **에러 처리**:
   - 권한 문제 감지 시 경고 로그 출력
   - 권한 문제가 있어도 계속 진행 (sudo로 해결 가능할 수 있음)
   - 상세한 권한 문제 정보 제공

**구현 위치**:

- `gui/modules/managers/hdfs_manager.py`의 `_check_hadoop_permissions()` 메서드
- `check_and_start()` 및 `start_daemons_direct()` 함수에 권한 확인 로직 추가

**개선 효과**:

- 권한 문제를 사전에 감지하여 사용자에게 명확한 오류 메시지 제공
- 권한 문제 해결 방법 안내 가능
- 데몬 시작 실패 원인 파악 용이

### 4. HDFS Safe Mode 이슈 (✅ 해결 완료)

**문제점**:

- HDFSManager가 NameNode와 DataNode를 시작한 직후, HDFSPipeline이 바로 데이터 쓰기를 시도하면 실패할 수 있음
- NameNode는 시작 직후 블록 정보를 확인하는 'Safe Mode' 상태에 있음
- Safe Mode 상태에서는 파일 쓰기/수정/삭제가 불가능
- 포트가 열렸다고 해서 바로 쓰기 작업이 가능한 것은 아님

**해결 방법**:

- `start_daemons_direct()` 함수에 Safe Mode 해제 대기 로직 추가
- `hdfs dfsadmin -safemode wait` 명령어 실행 (Safe Mode 해제까지 대기)
- 타임아웃 설정 (기본 60초, `hdfs.safemode_wait_timeout` 설정 가능)
- Safe Mode 상태 직접 확인 (`hdfs dfsadmin -safemode get`)
- Safe Mode 해제 실패 시에도 경고만 출력하고 계속 진행 (Safe Mode는 자동으로 해제됨)

**구현 위치**:

- `gui/modules/managers/hdfs_manager.py`의 `start_daemons_direct()` 함수
- `gui/core/timing_config.py`에 Safe Mode 관련 타이밍 설정 추가

### 5. 에러 처리

**현재 상태**: ✅ 양호

- Java 기반 실패 시 CLI 폴백
- HDFS 실패 시 로컬 저장
- 상세한 로깅
- Safe Mode 해제 대기 로직 추가

**개선 제안**:

- 재시도 로직 추가 (일시적 네트워크 오류 대응)
- 에러 분류 (일시적/영구적)

## 📊 파이프라인 우선순위

1. **HDFS** (우선순위: 높음)

   - 데이터 저장소, 필수 구성요소
   - 미실행 시에도 로컬 저장으로 대체 가능

2. **Kafka** (우선순위: 낮음)

   - 선택적 기능, 메시지 큐
   - 미실행 시에도 스파이더 정상 동작

3. **MapReduce** (우선순위: 중간)

   - HDFS에 데이터가 있을 때 실행
   - 로컬/클러스터 모드 지원

4. **DB 적재** (우선순위: 중간)
   - MapReduce 정제 후 실행
   - Backend API 필요

## ✅ 결론

### 설계 평가

1. **모듈화**: ✅ 우수

   - HDFSPipeline, HDFSClient, HDFSManager로 역할 분리
   - 각 컴포넌트가 독립적으로 동작 가능

2. **안정성**: ✅ 우수

   - Java 기반 우선, CLI 폴백
   - HDFS 실패 시 로컬 저장
   - 상세한 에러 처리

3. **자동화**: ✅ 우수

   - HADOOP_HOME 자동 감지
   - 단일/클러스터 모드 자동 전환
   - 데몬 자동 시작

4. **유연성**: ✅ 우수
   - 단일 노드/클러스터 모드 지원
   - HDFS 미실행 시에도 동작
   - 설정 파일/환경변수로 오버라이드 가능

### 권장 사항

1. ✅ 현재 설계는 잘 구성되어 있음
2. 💡 로컬 임시 파일 자동 업로드 기능 추가 고려
3. 💡 HADOOP_HOME 경로 캐싱 추가 고려
4. 💡 재시도 로직 추가 고려 (일시적 오류 대응)
