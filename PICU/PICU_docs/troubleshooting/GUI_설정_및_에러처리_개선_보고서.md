# 설정 관리 및 에러 처리 개선 보고서

**작업 일시**: 2025-11-29
**작업 범위**: 매직 넘버 제거 및 재시도 메커니즘 구현
**작업 결과**: ✅ 성공적으로 완료

---

## 📋 작업 개요

GUI 점검 보고서의 2, 3번 항목을 개선했습니다:

1. **설정 관리**: 매직 넘버를 설정 파일로 이동
2. **에러 처리**: 재시도 메커니즘 구현 및 적용

---

## 🔧 1. 설정 관리 개선

### 생성된 파일

#### `gui/core/timing_config.py`

- 타이밍 관련 설정을 중앙에서 관리하는 클래스
- 설정 파일에서 값을 읽어오고, 없으면 기본값 사용
- 모든 타이밍 관련 매직 넘버를 대체

#### 주요 기능

- `TimingConfig.get(key, default)`: 설정 값 가져오기
- `TimingConfig.set(key, value)`: 설정 값 설정
- GUI, HDFS, Kafka, SSH, Spider, Pipeline, Retry 등 모든 타이밍 설정 관리

### 설정 파일 업데이트

#### `gui/core/config_manager.py`

- `create_default_configs()` 메서드에 타이밍 및 재시도 설정 추가
- 기본값:
  - GUI 타이밍: auto_start_delay, process_status_update_delay, initial_refresh_delay 등
  - HDFS 타이밍: port_check_retry_interval, daemon_start_delay 등
  - Kafka 타이밍: broker_start_delay
  - 재시도 설정: default_max_retries, default_delay, backoff_factor

### 매직 넘버 교체

#### `app.py`

- `QTimer.singleShot(1000, ...)` → `TimingConfig.get("gui.auto_start_delay", 1000)`
- `QTimer.singleShot(2000, ...)` → `TimingConfig.get("gui.process_status_update_delay", 2000)`
- `QTimer.singleShot(5000, ...)` → `TimingConfig.get("gui.initial_refresh_delay", 5000)`
- `time.sleep(0.2)` → `TimingConfig.get("gui.dialog_wait_delay", 0.2)`
- `stats_timer.start(2000)` → `TimingConfig.get("gui.stats_update_interval", 2000)`

#### `managers/hdfs_manager.py`

- `time.sleep(2)` → `TimingConfig.get("hdfs.daemon_start_delay", 2)`
- `time.sleep(3)` → `TimingConfig.get("hdfs.secondary_namenode_delay", 3)`
- `max_retries=15` → `TimingConfig.get("hdfs.port_check_max_retries", 15)`
- `retry_interval=2` → `TimingConfig.get("hdfs.port_check_retry_interval", 2)`

#### `managers/kafka_manager.py`

- `time.sleep(3)` → `TimingConfig.get("kafka.broker_start_delay", 3)`

#### `managers/ssh_manager.py`

- `time.sleep(2)` → `TimingConfig.get("ssh.server_start_delay", 2)`

#### `modules/pipeline_orchestrator.py`

- `time.sleep(1)` → `TimingConfig.get("pipeline.process_stop_delay", 1)`
- `time.sleep(0.5)` → `TimingConfig.get("pipeline.process_check_delay", 0.5)`

#### `modules/spider_module.py`

- `time.sleep(2)` → `TimingConfig.get("spider.status_check_delay", 2)`

---

## 🔄 2. 에러 처리 개선

### 생성된 파일

#### `gui/core/retry_utils.py`

- 재시도 메커니즘을 제공하는 유틸리티 함수
- 자동 재시도, 백오프 전략, 예외 타입 지정 지원

#### 주요 함수

1. **`execute_with_retry()`**

   - 함수 실행 시 자동 재시도 메커니즘 적용
   - 매개변수:
     - `max_retries`: 최대 재시도 횟수 (기본: 3)
     - `delay`: 초기 재시도 지연 시간 (기본: 1.0초)
     - `backoff_factor`: 재시도 간격 증가 배수 (기본: 1.5)
     - `exceptions`: 재시도할 예외 타입
     - `on_retry`: 재시도 시 호출할 콜백 함수

2. **`retry_decorator()`**

   - 함수에 재시도 메커니즘을 적용하는 데코레이터

3. **`execute_with_retry_async()`**
   - 비동기 함수 실행 시 자동 재시도 메커니즘 적용

### 재시도 메커니즘 적용

#### `managers/kafka_manager.py`

- Kafka 브로커 포트 확인에 재시도 메커니즘 적용
- 네트워크 오류 시 자동 재시도 (최대 3회)

#### `tier2_monitor.py`

- `check_health()`: 헬스 체크 API 호출에 재시도 메커니즘 적용
- `get_dashboard_summary()`: 대시보드 요약 API 호출에 재시도 메커니즘 적용
- 네트워크 오류나 일시적 서버 오류 시 자동 재시도

---

## 📊 개선 효과

### 코드 품질

- ✅ **유지보수성**: 매직 넘버 제거로 설정 변경이 용이
- ✅ **가독성**: 설정 값의 의미가 명확해짐
- ✅ **안정성**: 재시도 메커니즘으로 일시적 오류에 대한 복구력 향상

### 개발 생산성

- ✅ **설정 관리**: 모든 타이밍 설정을 한 곳에서 관리
- ✅ **에러 복구**: 자동 재시도로 수동 개입 감소
- ✅ **테스트 용이성**: 설정 값을 변경하여 다양한 시나리오 테스트 가능

---

## 📝 변경 사항 요약

### 새로 생성된 파일

- `gui/core/timing_config.py`: 타이밍 설정 관리 클래스
- `gui/core/retry_utils.py`: 재시도 메커니즘 유틸리티

### 수정된 파일

- `gui/core/config_manager.py`: 기본 설정에 타이밍 및 재시도 설정 추가
- `gui/app.py`: 매직 넘버를 설정 값으로 교체
- `gui/modules/managers/hdfs_manager.py`: 매직 넘버 교체
- `gui/modules/managers/kafka_manager.py`: 매직 넘버 교체 및 재시도 메커니즘 적용
- `gui/modules/managers/ssh_manager.py`: 매직 넘버 교체
- `gui/modules/pipeline_orchestrator.py`: 매직 넘버 교체
- `gui/modules/spider_module.py`: 매직 넘버 교체
- `gui/tier2_monitor.py`: 재시도 메커니즘 적용

---

## ✅ 검증 완료

- [x] 모든 모듈 import 성공
- [x] 린터 오류 수정 완료
- [x] 타입 힌트 정확성 확인
- [x] 설정 파일 구조 확인

---

## 🎯 다음 단계

1. **추가 재시도 적용**

   - ClusterMonitor의 SSH 연결에 재시도 메커니즘 적용
   - 기타 네트워크 요청에 재시도 메커니즘 적용

2. **설정 UI 개선**

   - GUI 설정 탭에 타이밍 설정 추가
   - 재시도 설정을 GUI에서 조정 가능하도록

3. **모니터링 강화**
   - 재시도 횟수 및 실패율 모니터링
   - 설정 변경 이력 추적

---

**작성자**: Juns_AI_mcp
**작업 완료 시간**: 약 1시간
**개선 항목**: 매직 넘버 제거 (13개 위치), 재시도 메커니즘 적용 (3개 위치)
