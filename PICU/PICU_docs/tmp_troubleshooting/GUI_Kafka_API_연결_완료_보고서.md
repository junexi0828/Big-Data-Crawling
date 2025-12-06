# GUI Kafka API 연결 완료 보고서

**작성일**: 2025-12-06
**작업 내용**: GUI에 누락된 Kafka 관련 API 및 기능 연결
**상태**: ✅ **완료**

---

## 📋 요약

GUI에서 Kafka Consumer를 제어하고 모니터링하기 위한 모든 API와 기능을 연결했습니다. 이전에는 ControlTab에 Kafka 개별 제어 버튼이 없었고, 일부 기능이 누락되어 있었습니다.

---

## ✅ 구현 완료 사항

### 1. ControlTab에 Kafka 개별 제어 기능 추가

**추가된 UI 요소**:

- **Kafka 시작 버튼**: Kafka Consumer 시작
- **Kafka 중지 버튼**: Kafka Consumer 중지
- **Kafka 재시작 버튼**: Kafka Consumer 재시작
- **Kafka 상태 정보 라벨**: 실시간 상태 표시

**파일**: `PICU/cointicker/gui/ui/control_tab.py`

**구현 내용**:

```python
def start_kafka(self):
    """Kafka Consumer 시작"""
    # app.py의 start_kafka() 호출 또는 PipelineOrchestrator를 통한 시작

def stop_kafka(self):
    """Kafka Consumer 중지"""
    # app.py의 stop_kafka() 호출 또는 PipelineOrchestrator를 통한 중지

def restart_kafka(self):
    """Kafka Consumer 재시작"""
    # 중지 후 2초 대기 후 시작
```

---

### 2. app.py에 Kafka 제어 메서드 추가

**추가된 메서드**:

- `start_kafka()`: Kafka Consumer 시작
- `stop_kafka()`: Kafka Consumer 중지
- `restart_kafka()`: Kafka Consumer 재시작
- `_update_kafka_stats()`: Kafka 통계 업데이트 (개선)

**파일**: `PICU/cointicker/gui/app.py`

**주요 기능**:

- ModuleManager를 통한 KafkaModule 명령어 실행
- 비동기 처리 (threading.Thread 사용)
- UI 업데이트 (QTimer를 통한 메인 스레드 실행)
- 에러 처리 및 사용자 알림 (QMessageBox)

---

### 3. KafkaModule 명령어 확장

**기존 명령어**:

- `start_consumer`: Consumer 시작
- `stop_consumer`: Consumer 중지
- `restart_consumer`: Consumer 재시작
- `get_status`: Consumer 상태 조회
- `get_stats`: Consumer 통계 조회
- `get_consumer_groups`: Consumer Groups 상태 조회
- `get_logs`: Consumer 로그 조회

**새로 추가된 명령어**:

- `get_topics`: 구독 가능한 토픽 목록 조회

**파일**: `PICU/cointicker/gui/modules/kafka_module.py`

**구현 내용**:

```python
elif command == "get_topics":
    # Kafka Consumer를 통해 토픽 목록 조회
    # 패턴 매칭 (cointicker.raw.*)
    # 모든 토픽과 매칭된 토픽 반환
```

---

### 4. Backend API 엔드포인트 추가

**새로 생성된 파일**: `PICU/cointicker/backend/api/pipeline.py`

**추가된 엔드포인트**:

- `GET /api/pipeline/kafka/status`: Kafka Consumer 상태 조회
- `POST /api/pipeline/kafka/start`: Kafka Consumer 시작
- `POST /api/pipeline/kafka/stop`: Kafka Consumer 중지
- `POST /api/pipeline/kafka/restart`: Kafka Consumer 재시작
- `GET /api/pipeline/kafka/stats`: Kafka Consumer 통계 조회
- `GET /api/pipeline/kafka/topics`: Kafka 토픽 목록 조회
- `GET /api/pipeline/kafka/consumer-groups`: Consumer Groups 상태 조회

**통합**: `PICU/cointicker/backend/app.py`에 `pipeline.router` 등록

**참고**: 현재 GUI는 ModuleManager를 통해 직접 모듈을 호출하므로, Backend API는 선택사항입니다. 향후 REST API를 통한 제어가 필요할 때 사용할 수 있습니다.

---

### 5. Kafka 통계 업데이트 개선

**개선 내용**:

- 프로세스 상태와 실제 연결 상태를 구분하여 표시
- 소비율(messages_per_second) 정보 추가
- Consumer Groups 정보 표시
- ControlTab의 Kafka 상태 정보 라벨 업데이트

**파일**: `PICU/cointicker/gui/app.py` - `_update_kafka_stats()` 메서드

**표시 정보**:

- 상태: "실행 중 (연결됨)" / "실행 중 (연결 중...)" / "중지됨"
- 처리 메시지 수
- 에러 수
- 소비율 (msg/s)

---

## 📊 API 연결 현황

### GUI → KafkaModule (ModuleManager를 통한 직접 호출)

| 기능                 | 명령어                | 상태             |
| -------------------- | --------------------- | ---------------- |
| Consumer 시작        | `start_consumer`      | ✅ 연결됨        |
| Consumer 중지        | `stop_consumer`       | ✅ 연결됨        |
| Consumer 재시작      | `restart_consumer`    | ✅ 연결됨        |
| 상태 조회            | `get_status`          | ✅ 연결됨        |
| 통계 조회            | `get_stats`           | ✅ 연결됨        |
| Consumer Groups 조회 | `get_consumer_groups` | ✅ 연결됨        |
| 로그 조회            | `get_logs`            | ✅ 연결됨        |
| 토픽 목록 조회       | `get_topics`          | ✅ 연결됨 (신규) |

### GUI → Backend API (선택사항)

| 기능                 | 엔드포인트                                | 상태      |
| -------------------- | ----------------------------------------- | --------- |
| 상태 조회            | `GET /api/pipeline/kafka/status`          | ✅ 추가됨 |
| Consumer 시작        | `POST /api/pipeline/kafka/start`          | ✅ 추가됨 |
| Consumer 중지        | `POST /api/pipeline/kafka/stop`           | ✅ 추가됨 |
| Consumer 재시작      | `POST /api/pipeline/kafka/restart`        | ✅ 추가됨 |
| 통계 조회            | `GET /api/pipeline/kafka/stats`           | ✅ 추가됨 |
| 토픽 목록 조회       | `GET /api/pipeline/kafka/topics`          | ✅ 추가됨 |
| Consumer Groups 조회 | `GET /api/pipeline/kafka/consumer-groups` | ✅ 추가됨 |

---

## 🔗 연결된 GUI 컴포넌트

### 1. ControlTab (제어 탭)

**추가된 기능**:

- Kafka 시작/중지/재시작 버튼
- Kafka 상태 정보 라벨 (실시간 업데이트)

**연결된 메서드**:

- `start_kafka()` → `app.py.start_kafka()`
- `stop_kafka()` → `app.py.stop_kafka()`
- `restart_kafka()` → `app.py.restart_kafka()`

### 2. DashboardTab (대시보드 탭)

**기존 기능** (이미 연결됨):

- Kafka 상태 표시
- 처리 메시지 수 표시
- 소비율 표시
- Consumer Groups 상태 표시

**데이터 소스**: `app.py._update_pipeline_monitoring()` → `KafkaModule.get_status()`, `get_stats()`, `get_consumer_groups()`

### 3. app.py (메인 애플리케이션)

**추가/개선된 메서드**:

- `start_kafka()`: Kafka Consumer 시작
- `stop_kafka()`: Kafka Consumer 중지
- `restart_kafka()`: Kafka Consumer 재시작
- `_update_kafka_stats()`: Kafka 통계 업데이트 (개선)

**호출 주기**: `_update_all_stats()`에서 주기적으로 호출

---

## 📝 수정된 파일 목록

1. **`PICU/cointicker/gui/ui/control_tab.py`**

   - Kafka 제어 버튼 추가
   - Kafka 상태 정보 라벨 추가
   - `start_kafka()`, `stop_kafka()`, `restart_kafka()` 메서드 추가

2. **`PICU/cointicker/gui/app.py`**

   - `start_kafka()`, `stop_kafka()`, `restart_kafka()` 메서드 추가
   - `_update_kafka_stats()` 메서드 개선 (연결 상태, 소비율 추가)

3. **`PICU/cointicker/gui/modules/kafka_module.py`**

   - `get_topics` 명령어 추가
   - 명령어 문서 업데이트

4. **`PICU/cointicker/backend/api/pipeline.py`** (신규)

   - Kafka 관련 REST API 엔드포인트 추가

5. **`PICU/cointicker/backend/app.py`**
   - `pipeline.router` 등록

---

## 🎯 사용 방법

### GUI에서 Kafka 제어

1. **제어 탭**에서:

   - "Kafka 시작" 버튼 클릭 → Consumer 시작
   - "Kafka 중지" 버튼 클릭 → Consumer 중지
   - "Kafka 재시작" 버튼 클릭 → Consumer 재시작
   - 상태 정보는 실시간으로 업데이트됨

2. **대시보드 탭**에서:
   - Kafka 상태, 처리 메시지 수, 소비율, Consumer Groups 정보 확인

### Backend API 사용 (선택사항)

```bash
# Kafka Consumer 시작
curl -X POST http://localhost:5001/api/pipeline/kafka/start

# Kafka Consumer 상태 조회
curl http://localhost:5001/api/pipeline/kafka/status

# Kafka 토픽 목록 조회
curl http://localhost:5001/api/pipeline/kafka/topics

# Consumer Groups 조회
curl http://localhost:5001/api/pipeline/kafka/consumer-groups
```

---

## ✅ 검증 사항

- [x] ControlTab에 Kafka 제어 버튼 추가
- [x] app.py에 Kafka 제어 메서드 추가
- [x] KafkaModule에 토픽 조회 기능 추가
- [x] Backend에 Kafka API 엔드포인트 추가
- [x] Kafka 통계 업데이트 개선
- [x] 모든 명령어가 GUI와 연결됨

---

## 🔗 관련 파일

- `PICU/cointicker/gui/ui/control_tab.py` - ControlTab UI 및 제어 메서드
- `PICU/cointicker/gui/app.py` - 메인 애플리케이션, Kafka 제어 메서드
- `PICU/cointicker/gui/modules/kafka_module.py` - KafkaModule 명령어
- `PICU/cointicker/backend/api/pipeline.py` - Backend Kafka API
- `PICU/cointicker/backend/app.py` - Backend 메인 애플리케이션

---

**보고서 작성자**: Juns AI Assistant
**최종 업데이트**: 2025-12-06
