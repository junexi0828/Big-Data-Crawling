# GUI HDFS API 연결 완료 보고서

**작성일**: 2025-12-06
**작업 내용**: GUI에 누락된 HDFS/Hadoop 관련 API 및 기능 연결
**상태**: ✅ **완료**

---

## 📋 요약

GUI에서 HDFS 데몬을 제어하고 모니터링하기 위한 모든 API와 기능을 연결했습니다. 이전에는 ControlTab에 HDFS 개별 제어 버튼이 없었고, 일부 기능이 누락되어 있었습니다.

---

## ✅ 구현 완료 사항

### 1. ControlTab에 HDFS 개별 제어 기능 추가

**추가된 UI 요소**:

- **HDFS 시작 버튼**: HDFS 데몬 시작
- **HDFS 중지 버튼**: HDFS 데몬 중지
- **HDFS 재시작 버튼**: HDFS 데몬 재시작
- **HDFS 상태 정보 라벨**: 실시간 상태 표시

**파일**: `PICU/cointicker/gui/ui/control_tab.py`

**구현 내용**:

```python
def start_hdfs(self):
    """HDFS 데몬 시작"""
    # app.py의 start_hdfs() 호출 또는 PipelineOrchestrator를 통한 시작

def stop_hdfs(self):
    """HDFS 데몬 중지"""
    # app.py의 stop_hdfs() 호출 또는 PipelineOrchestrator를 통한 중지

def restart_hdfs(self):
    """HDFS 데몬 재시작"""
    # 중지 후 2초 대기 후 시작
```

---

### 2. app.py에 HDFS 제어 메서드 추가

**추가된 메서드**:

- `start_hdfs()`: HDFS 데몬 시작
- `stop_hdfs()`: HDFS 데몬 중지
- `restart_hdfs()`: HDFS 데몬 재시작
- `_update_hdfs_stats()`: HDFS 통계 업데이트 (신규)

**파일**: `PICU/cointicker/gui/app.py`

**주요 기능**:

- PipelineOrchestrator를 통한 HDFS 데몬 제어
- 비동기 처리 (threading.Thread 사용)
- UI 업데이트 (QTimer를 통한 메인 스레드 실행)
- 에러 처리 및 사용자 알림 (QMessageBox)

---

### 3. HDFSModule 명령어 확장

**기존 명령어**:

- `get_status`: HDFS 상태 조회
- `upload`: 파일 업로드
- `download`: 파일 다운로드
- `list_files`: 파일 목록 조회
- `get_pending_files_count`: 대기 파일 수 조회

**새로 추가된 명령어**:

- `get_auto_upload_status`: 자동 업로드 상태 조회
- `list_directories`: 디렉토리 목록 조회

**파일**: `PICU/cointicker/gui/modules/hdfs_module.py`

**구현 내용**:

```python
elif command == "get_auto_upload_status":
    # 자동 업로드 상태 조회 (대기 파일 수 기반)
    # HDFSUploadManager는 실제로는 KafkaConsumer나 HDFSPipeline에서 관리됨

elif command == "list_directories":
    # HDFS 디렉토리 목록 조회
    # 디렉토리만 필터링하여 반환
```

---

### 4. Backend API 엔드포인트 추가

**추가된 엔드포인트**:

- `GET /api/pipeline/hdfs/status`: HDFS 상태 조회
- `POST /api/pipeline/hdfs/start`: HDFS 데몬 시작
- `POST /api/pipeline/hdfs/stop`: HDFS 데몬 중지
- `POST /api/pipeline/hdfs/restart`: HDFS 데몬 재시작
- `GET /api/pipeline/hdfs/stats`: HDFS 통계 조회
- `GET /api/pipeline/hdfs/files`: HDFS 파일 목록 조회

**파일**: `PICU/cointicker/backend/api/pipeline.py`

**통합**: 이미 `pipeline.router`에 포함되어 있음

**참고**: 현재 GUI는 PipelineOrchestrator를 통해 직접 HDFSManager를 호출하므로, Backend API는 선택사항입니다. 향후 REST API를 통한 제어가 필요할 때 사용할 수 있습니다.

---

### 5. HDFS 통계 업데이트 추가

**추가 내용**:

- HDFS 연결 상태 확인
- NameNode 정보 표시
- 대기 파일 수 표시
- ControlTab의 HDFS 상태 정보 라벨 업데이트

**파일**: `PICU/cointicker/gui/app.py` - `_update_hdfs_stats()` 메서드

**표시 정보**:

- 상태: "실행 중 (연결됨)" / "중지됨 (연결 안됨)"
- NameNode 주소
- 대기 파일 수

---

## 📊 API 연결 현황

### GUI → HDFSModule (ModuleManager를 통한 직접 호출)

| 기능                 | 명령어                    | 상태      |
| -------------------- | ------------------------- | --------- |
| 상태 조회            | `get_status`              | ✅ 연결됨 |
| 파일 업로드          | `upload`                  | ✅ 연결됨 |
| 파일 다운로드        | `download`                | ✅ 연결됨 |
| 파일 목록 조회       | `list_files`              | ✅ 연결됨 |
| 대기 파일 수 조회    | `get_pending_files_count` | ✅ 연결됨 |
| 자동 업로드 상태 조회 | `get_auto_upload_status`  | ✅ 연결됨 (신규) |
| 디렉토리 목록 조회   | `list_directories`        | ✅ 연결됨 (신규) |

### GUI → PipelineOrchestrator → HDFSManager (데몬 제어)

| 기능           | 메서드              | 상태      |
| -------------- | ------------------- | --------- |
| 데몬 시작      | `start_process("hdfs")` | ✅ 연결됨 |
| 데몬 중지      | `stop_process("hdfs")`  | ✅ 연결됨 |
| 실행 상태 확인  | `check_running()`       | ✅ 연결됨 |

### GUI → Backend API (선택사항)

| 기능           | 엔드포인트                        | 상태      |
| -------------- | --------------------------------- | --------- |
| 상태 조회      | `GET /api/pipeline/hdfs/status`   | ✅ 추가됨 |
| 데몬 시작      | `POST /api/pipeline/hdfs/start`   | ✅ 추가됨 |
| 데몬 중지      | `POST /api/pipeline/hdfs/stop`    | ✅ 추가됨 |
| 데몬 재시작    | `POST /api/pipeline/hdfs/restart` | ✅ 추가됨 |
| 통계 조회      | `GET /api/pipeline/hdfs/stats`    | ✅ 추가됨 |
| 파일 목록 조회 | `GET /api/pipeline/hdfs/files`    | ✅ 추가됨 |

---

## 🔗 연결된 GUI 컴포넌트

### 1. ControlTab (제어 탭)

**추가된 기능**:

- HDFS 시작/중지/재시작 버튼
- HDFS 상태 정보 라벨 (실시간 업데이트)

**연결된 메서드**:

- `start_hdfs()` → `app.py.start_hdfs()`
- `stop_hdfs()` → `app.py.stop_hdfs()`
- `restart_hdfs()` → `app.py.restart_hdfs()`

### 2. DashboardTab (대시보드 탭)

**기존 기능** (이미 연결됨):

- HDFS 상태 표시
- 대기 파일 수 표시
- 연결 상태 표시

**데이터 소스**: `app.py._update_pipeline_monitoring()` → `HDFSModule.get_status()`

### 3. app.py (메인 애플리케이션)

**추가/개선된 메서드**:

- `start_hdfs()`: HDFS 데몬 시작
- `stop_hdfs()`: HDFS 데몬 중지
- `restart_hdfs()`: HDFS 데몬 재시작
- `_update_hdfs_stats()`: HDFS 통계 업데이트 (신규)

**호출 주기**: `_update_all_stats()`에서 주기적으로 호출

---

## 📝 수정된 파일 목록

1. **`PICU/cointicker/gui/ui/control_tab.py`**

   - HDFS 제어 버튼 추가
   - HDFS 상태 정보 라벨 추가
   - `start_hdfs()`, `stop_hdfs()`, `restart_hdfs()` 메서드 추가

2. **`PICU/cointicker/gui/app.py`**

   - `start_hdfs()`, `stop_hdfs()`, `restart_hdfs()` 메서드 추가
   - `_update_hdfs_stats()` 메서드 추가
   - `_update_all_stats()`에서 `_update_hdfs_stats()` 호출 추가

3. **`PICU/cointicker/gui/modules/hdfs_module.py`**

   - `get_auto_upload_status` 명령어 추가
   - `list_directories` 명령어 추가
   - `get_status` 명령어 개선 (namenode 정보 안전하게 반환)

4. **`PICU/cointicker/backend/api/pipeline.py`**

   - HDFS 관련 REST API 엔드포인트 추가

---

## 🎯 사용 방법

### GUI에서 HDFS 제어

1. **제어 탭**에서:

   - "HDFS 시작" 버튼 클릭 → 데몬 시작
   - "HDFS 중지" 버튼 클릭 → 데몬 중지
   - "HDFS 재시작" 버튼 클릭 → 데몬 재시작
   - 상태 정보는 실시간으로 업데이트됨

2. **대시보드 탭**에서:

   - HDFS 상태, 대기 파일 수, 연결 상태 확인

### Backend API 사용 (선택사항)

```bash
# HDFS 데몬 시작
curl -X POST http://localhost:5001/api/pipeline/hdfs/start

# HDFS 상태 조회
curl http://localhost:5001/api/pipeline/hdfs/status

# HDFS 파일 목록 조회
curl http://localhost:5001/api/pipeline/hdfs/files?hdfs_path=/raw

# HDFS 통계 조회
curl http://localhost:5001/api/pipeline/hdfs/stats
```

---

## ✅ 검증 사항

- [x] ControlTab에 HDFS 제어 버튼 추가
- [x] app.py에 HDFS 제어 메서드 추가
- [x] HDFSModule에 추가 명령어 구현
- [x] Backend에 HDFS API 엔드포인트 추가
- [x] HDFS 통계 업데이트 추가
- [x] 모든 명령어가 GUI와 연결됨

---

## 🔗 관련 파일

- `PICU/cointicker/gui/ui/control_tab.py` - ControlTab UI 및 제어 메서드
- `PICU/cointicker/gui/app.py` - 메인 애플리케이션, HDFS 제어 메서드
- `PICU/cointicker/gui/modules/hdfs_module.py` - HDFSModule 명령어
- `PICU/cointicker/gui/modules/managers/hdfs_manager.py` - HDFSManager (데몬 제어)
- `PICU/cointicker/backend/api/pipeline.py` - Backend HDFS API
- `PICU/cointicker/backend/app.py` - Backend 메인 애플리케이션

---

**보고서 작성자**: Juns AI Assistant
**최종 업데이트**: 2025-12-06

