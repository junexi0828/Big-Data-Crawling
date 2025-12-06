# 제어 탭 로직 점검 보고서

**작성일**: 2025-12-06
**점검 범위**: 제어 탭 및 각 모듈별 실행 방법, 컴포넌트 전수 조사

## 🔍 발견된 문제점

### 1. 프로세스 이름 불일치 문제 ✅ 해결 완료

**문제**:

- 설정 파일(`config_tab.py`)에서는 `"kafka"`와 `"mapreduce"`를 사용
- `pipeline_orchestrator.py`에서는 `"kafka_consumer"`와 `"hdfs"`를 사용
- 로그에서 "⚠️ kafka 자동 시작 실패: 알 수 없는 프로세스: kafka" 오류 발생

**해결 방법**:

- `_normalize_process_name()` 함수 추가하여 프로세스 이름 매핑
  - `"kafka"` → `"kafka_consumer"`
  - `"mapreduce"` → `None` (작업 타입이므로 프로세스가 아님)
- `start_process()`, `stop_process()`, `start_all()`, `stop_all()`에서 프로세스 이름 정규화 적용
- `_auto_start_essential_services()`에서 `mapreduce` 건너뛰기 로직 추가

### 2. HDFS 중지 로직 개선 ✅ 해결 완료

**문제**:

- HDFS 중지 시 `hdfs_manager.stop_all_daemons()`를 호출하지 않음
- 직접 프로세스 종료만 시도하여 데몬이 제대로 종료되지 않을 수 있음

**해결 방법**:

- `stop_process()`에서 HDFS 중지 시 `hdfs_manager.stop_all_daemons()` 호출
- HADOOP_HOME 경로 자동 감지 및 캐시된 경로 사용

### 3. Kafka Consumer 중지 로직 개선 ✅ 해결 완료

**문제**:

- Kafka Consumer 중지 시 `stop_consumer` 명령어를 사용하지 않음

**해결 방법**:

- `stop_process()`에서 Kafka Consumer 중지 시 `stop_consumer` 명령어 사용
- 모듈의 `stop()` 메서드도 정상 동작 확인

## 📋 각 모듈별 실행 방법 검증

### 1. BackendModule ✅ 정상

**시작 방법**:

- `start()`: `backend/scripts/run_server.sh` 실행
- `AUTO_PORT_SWITCH=true` 환경변수 설정
- 포트 파일 자동 생성 (`config/.backend_port`)

**중지 방법**:

- `stop()`: 프로세스 종료 + `pkill -f 'uvicorn app:app'`

**상태**: ✅ 정상 동작

### 2. FrontendModule ✅ 정상

**시작 방법**:

- `start()`: `frontend/scripts/run_dev.sh` 실행
- 백엔드 포트 파일 자동 읽기

**중지 방법**:

- `stop()`: 프로세스 종료 + `pkill -f 'vite'` + `pkill -f 'npm run dev'`

**상태**: ✅ 정상 동작

### 3. KafkaModule ✅ 정상

**시작 방법**:

- `start()`: `kafka_consumer.py` 실행
- 프로세스 모니터링 자동 시작
- PID 기반 프로세스 ID 생성

**중지 방법**:

- `stop()`: 프로세스 `terminate()` → `wait(timeout=5)` → `kill()` (필요 시)
- 프로세스 모니터링 자동 중지

**상태**: ✅ 정상 동작

### 4. SpiderModule ✅ 정상

**시작 방법**:

- `start()`: 모듈 활성화
- `start_spider()`: 개별 Spider 시작
- 기본 Spider 자동 시작 기능 (`upbit_trends`)

**중지 방법**:

- `stop()`: 모든 실행 중인 Spider 중지
- `stop_spider()`: 개별 Spider 중지

**상태**: ✅ 정상 동작

### 5. HDFSModule ✅ 정상

**시작 방법**:

- `start()`: 모듈 활성화
- 실제 HDFS 시작은 `hdfs_manager.check_and_start()` 사용

**중지 방법**:

- `stop()`: 모듈 비활성화
- 실제 HDFS 중지는 `hdfs_manager.stop_all_daemons()` 사용

**상태**: ✅ 정상 동작 (중지 로직 개선 완료)

### 6. MapReduceModule ✅ 정상

**시작 방법**:

- `start()`: 모듈 활성화 (작업 타입이므로 프로세스가 아님)

**중지 방법**:

- `stop()`: 모듈 비활성화

**상태**: ✅ 정상 동작 (작업 타입으로 처리)

## 🔧 수정된 파일 목록

1. **`gui/modules/pipeline_orchestrator.py`**

   - `_normalize_process_name()` 함수 추가
   - `start_process()`: 프로세스 이름 정규화 적용
   - `stop_process()`: HDFS/Kafka 중지 로직 개선, 프로세스 이름 정규화 적용
   - `start_all()`: 프로세스 이름 정규화 적용
   - `stop_all()`: 프로세스 이름 정규화 적용

2. **`gui/app.py`**
   - `_auto_start_essential_services()`: `mapreduce` 건너뛰기 로직 추가

## ✅ 검증 완료 사항

### 프로세스 이름 매핑

- ✅ `kafka` → `kafka_consumer` 매핑 정상 동작
- ✅ `mapreduce` 작업 타입 처리 정상 동작
- ✅ 다른 프로세스 이름은 그대로 사용

### 각 모듈의 start/stop 메서드

- ✅ BackendModule: 정상
- ✅ FrontendModule: 정상
- ✅ KafkaModule: 정상
- ✅ SpiderModule: 정상
- ✅ HDFSModule: 정상 (중지 로직 개선)
- ✅ MapReduceModule: 정상

### 의존성 체크

- ✅ Kafka Consumer는 Kafka 브로커 의존성 확인
- ✅ Kafka 브로커 자동 시작 기능 정상 동작
- ✅ 의존성 실패 시 적절한 오류 메시지 출력

### 프로세스 상태 관리

- ✅ 프로세스 상태 Enum 사용 (STOPPED, STARTING, RUNNING, STOPPING, ERROR)
- ✅ 프로세스 상태 테이블 업데이트 정상 동작
- ✅ 시작 시간 기록 정상 동작

## 🎯 개선 효과

1. **프로세스 이름 일관성**: 설정 파일과 실제 프로세스 이름 간 매핑 자동 처리
2. **HDFS 중지 안정성**: HDFS 데몬이 제대로 종료되도록 개선
3. **Kafka Consumer 중지 안정성**: 명령어 기반 중지로 안정성 향상
4. **오류 메시지 개선**: 명확한 오류 메시지로 디버깅 용이

## 📝 권장 사항

1. **프로세스 이름 통일**: 향후 모든 설정에서 `kafka_consumer` 사용 권장
2. **MapReduce 처리**: MapReduce는 작업 타입이므로 프로세스 목록에서 제외 고려
3. **로그 개선**: 프로세스 이름 매핑 시 로그 출력으로 추적 가능

## 🔍 추가 확인 사항

### 정상 동작 확인

- ✅ 프로세스 시작/중지 로직 정상
- ✅ 프로세스 상태 테이블 업데이트 정상
- ✅ 의존성 체크 정상
- ✅ 오류 처리 정상

### 개선 완료

- ✅ 프로세스 이름 매핑 추가
- ✅ HDFS 중지 로직 개선
- ✅ Kafka Consumer 중지 로직 개선
- ✅ MapReduce 처리 개선

---

**결론**: 제어 탭의 모든 로직이 정상적으로 동작하며, 발견된 문제점은 모두 해결되었습니다.

- Juns Mcp 2025.12.06
