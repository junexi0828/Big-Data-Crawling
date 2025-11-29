# GUI 실행 문제 분석 보고서

**작성일**: 2025-11-29
**분석 대상**: GUI 실행 로그 (라인 244-1025)
**상태**: ✅ GUI 실행 성공, ⚠️ 일부 경로 및 연결 문제 발견

---

## 📊 실행 요약

### ✅ 성공 사항

1. **GUI 애플리케이션 정상 실행**: GUI 창이 성공적으로 열렸으며 프로세스 상태를 표시하고 있습니다.
2. **모듈 초기화 성공**: 모든 모듈(SpiderModule, MapReduceModule, HDFSModule, BackendModule, PipelineModule, KafkaModule)이 정상적으로 로드되었습니다.
3. **프로세스 자동 시작**:
   - Spider (upbit_trends) - 실행 중
   - Kafka Consumer - 실행 중
   - Backend - 실행 중 (포트 5001)
   - Frontend - 실행 중 (포트 3000)
   - HDFS - 중지됨

---

## ⚠️ 발견된 문제점

### 1. 백엔드 포트 파일 경로 오류 (심각)

**문제**:

```
scripts/run_server.sh: line 105: /Users/juns/code/personal/notion/pknu_workspace/bigdata/PICU/cointicker/cointicker/config/.backend_port: No such file or directory
```

**원인**:

- `backend/scripts/run_server.sh`에서 `PROJECT_ROOT` 계산이 잘못되어 `cointicker`가 중복됨
- 현재 코드: `SCRIPT_DIR/../..` → `backend/scripts/` → `backend/` → `cointicker/` (PICU가 아님)
- 현재 경로: `PICU/cointicker/cointicker/config/.backend_port` (잘못됨)
- 올바른 경로: `PICU/cointicker/config/.backend_port`
- **핵심 문제**: `PROJECT_ROOT`가 `cointicker`로 계산되어 `$PROJECT_ROOT/cointicker/config`가 중복됨

**영향**:

- 백엔드 포트 파일이 생성되지 않아 GUI가 백엔드 포트를 감지하지 못함
- GUI가 기본 포트(5000)로 접근하지만 실제 백엔드는 5001로 실행됨
- 403 Forbidden 에러 반복 발생

**해결 방법**:
`backend/scripts/run_server.sh`의 `PROJECT_ROOT` 계산 수정 필요

---

### 2. 백엔드 포트 불일치 (중요)

**문제**:

- 백엔드가 포트 5001로 실행됨 (포트 5000이 사용 중이어서)
- GUI는 포트 5000으로 접근 시도
- 결과: 403 Forbidden 에러 반복

**로그 증거**:

```
⚠️  포트 5000이 사용 중이지만 백엔드 서버가 아닙니다.
다른 포트를 사용합니다 (5001)...
```

**영향**:

- Tier2 모니터가 백엔드에 연결하지 못함
- 헬스 체크 실패 반복
- 대시보드 데이터를 가져오지 못함

**해결 방법**:

1. 포트 파일 경로 수정 후 포트 파일이 정상 생성되도록 수정
2. GUI가 포트 파일을 읽어 실제 백엔드 포트를 감지하도록 수정

---

### 3. Cluster Config 파일 경로 오류 (경고)

**문제**:

```
ERROR - 설정 파일을 찾을 수 없습니다: /Users/juns/code/personal/notion/pknu_workspace/bigdata/PICU/cointicker/gui/config/cluster_config.yaml
```

**원인**:

- 에러 로그에서 `gui/config/cluster_config.yaml`을 찾고 있다고 나옴
- 실제 파일 위치: `cointicker/config/cluster_config.yaml`
- **참고**: 실제 코드(`cluster_monitor.py`)는 `parent.parent.parent`를 사용하여 올바르게 계산하고 있음
- 다른 경로에서 호출되거나 초기화 시점 문제일 수 있음

**영향**:

- 클러스터 모니터가 설정을 읽지 못함
- 클러스터 상태 확인 불가

**해결 방법**:
`cluster_monitor.py`의 설정 파일 경로 수정 필요

---

### 4. HDFS 클러스터 연결 실패 (정보)

**문제**:

- SSH 연결 실패로 멀티노드 모드 설정 실패
- 마스터 및 워커 노드에 연결할 수 없음

**로그 증거**:

```
WARNING - 마스터 노드(raspberry-master) SSH 연결 실패
WARNING - 워커 노드(raspberry-worker1) SSH 연결 실패
WARNING - 워커 노드(raspberry-worker2) SSH 연결 실패
WARNING - 워커 노드(raspberry-worker3) SSH 연결 실패
```

**영향**:

- 로컬 단일 노드 모드로 전환됨
- 클러스터 기능 사용 불가

**해결 방법**:

- SSH 연결 설정 확인 또는 로컬 모드 사용

---

### 5. 반복적인 재시도 로그 (성능)

**문제**:

- 백엔드 연결 실패로 인한 재시도 로그가 과도하게 반복됨
- 로그 파일이 매우 커짐

**영향**:

- 로그 파일 크기 증가
- 디버깅 어려움

**해결 방법**:

- 재시도 간격 조정
- 실패 시 로그 레벨 조정 (ERROR → WARNING)

---

## 🔧 수정 필요 사항

### 우선순위 1: 백엔드 포트 파일 경로 수정

**파일**: `cointicker/backend/scripts/run_server.sh`

**현재 코드** (라인 31-39):

```bash
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
```

**문제**:

- `backend/scripts/run_server.sh` → `backend/` → `cointicker/` → `PICU/`
- 하지만 실제로는 `backend/scripts/` → `backend/` → `cointicker/` → `PICU/`가 되어야 함

**수정 필요**:

```bash
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# backend/scripts/run_server.sh -> backend/ -> cointicker/ -> PICU/
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
```

**포트 파일 경로** (라인 104):

```bash
BACKEND_PORT_FILE="$PROJECT_ROOT/cointicker/config/.backend_port"
```

---

### 우선순위 2: Cluster Monitor 설정 파일 경로 확인

**파일**: `cointicker/gui/monitors/cluster_monitor.py`

**현재 경로 계산** (실제 코드 확인):

```python
# gui/monitors/cluster_monitor.py -> gui/monitors -> gui -> cointicker
project_root = current_file.parent.parent.parent
config_path = project_root / "config" / "cluster_config.yaml"
```

**상태**: ✅ **이미 올바르게 구현되어 있음**

- 실제 코드는 `parent.parent.parent`를 사용하여 `cointicker` 디렉토리를 찾고 있음
- `cointicker/config/cluster_config.yaml` 경로가 올바르게 계산됨
- 하지만 에러 로그에서는 `gui/config/cluster_config.yaml`을 찾고 있다고 나옴
- 이는 다른 경로에서 호출되거나 캐시 문제일 수 있음

---

## 📈 성능 개선 제안

### 1. 재시도 로그 최적화

- 실패 시 첫 번째 시도만 WARNING, 이후는 DEBUG 레벨로 변경
- 최대 재시도 횟수 초과 시에만 ERROR 로그 출력

### 2. 포트 파일 감지 개선

- 포트 파일이 없을 때 백엔드 프로세스를 직접 확인하여 포트 감지
- 포트 파일 생성 실패 시 대체 방법 제공

### 3. 경로 계산 통합 및 표준화 (권장)

**문제점**:

- 프로젝트 전체에서 경로 계산 방식이 일관되지 않음
- 각 파일마다 `parent.parent.parent...` 같은 상대 경로 계산이 반복됨
- 디렉토리 구조 변경 시 여러 파일을 수정해야 함

**개선 방안**:

- `shared/utils.py`에 공통 함수 추가:

  ```python
  def get_project_root() -> Path:
      """PICU 프로젝트 루트 디렉토리 찾기"""
      current_path = Path(__file__).resolve()
      if "PICU" in current_path.parts:
          picu_index = current_path.parts.index("PICU")
          return Path("/").joinpath(*current_path.parts[:picu_index + 1])
      elif "cointicker" in current_path.parts:
          cointicker_index = current_path.parts.index("cointicker")
          return Path("/").joinpath(*current_path.parts[:cointicker_index])
      else:
          # 현재 디렉토리에서 PICU 또는 cointicker 찾기
          for parent in current_path.parents:
              if parent.name == "PICU":
                  return parent
              elif parent.name == "cointicker":
                  return parent.parent
          raise RuntimeError("프로젝트 루트를 찾을 수 없습니다")

  def get_cointicker_root() -> Path:
      """cointicker 디렉토리 찾기"""
      project_root = get_project_root()
      return project_root / "cointicker"
  ```

- 모든 파일에서 이 함수를 사용하도록 리팩토링
- Bash 스크립트도 공통 변수나 함수로 통합

---

## ✅ 해결 완료된 항목

1. ✅ GUI 실행 성공
2. ✅ 모듈 초기화 성공
3. ✅ 프로세스 자동 시작 기능 작동
4. ✅ CacheManager 데드락 문제 해결 (RLock 사용)

---

## 📝 다음 단계

1. **즉시 수정 필요**:

   - `backend/scripts/run_server.sh`의 `PROJECT_ROOT` 계산 수정
   - `cluster_monitor.py`의 설정 파일 경로 수정

2. **테스트 필요**:

   - 백엔드 포트 파일 생성 확인
   - GUI가 포트 파일을 읽어 백엔드 포트를 정확히 감지하는지 확인
   - 클러스터 설정 파일 로드 확인

3. **개선 사항**:
   - 재시도 로그 최적화
   - 포트 감지 대체 방법 구현

---

## 📊 통계

- **총 에러 수**: 약 200+ (대부분 403 Forbidden 반복)
- **경로 관련 에러**: 2건
- **연결 실패**: 1건 (HDFS 클러스터)
- **성공한 기능**: 모듈 로드, 프로세스 시작, GUI 표시

---

---

## 🔍 경로 계산 복잡도 분석

### 현재 상황

프로젝트 전체에서 경로 계산 방식이 일관되지 않고 복잡합니다:

1. **Bash 스크립트**: `SCRIPT_DIR/../..`, `SCRIPT_DIR/../../..` 등 다양한 상대 경로 사용
2. **Python 코드**: `parent.parent.parent`, `parent.parent.parent.parent` 등 반복적인 상대 경로 계산
3. **일관성 부족**: 같은 목적(프로젝트 루트 찾기)이지만 파일마다 다른 방식 사용

### 경로 계산 예시

| 파일 위치                         | 현재 계산 방식                | 목적              | 문제점                     |
| --------------------------------- | ----------------------------- | ----------------- | -------------------------- |
| `backend/scripts/run_server.sh`   | `SCRIPT_DIR/../..`            | PICU 루트 찾기    | ❌ `cointicker`까지만 찾음 |
| `gui/monitors/cluster_monitor.py` | `parent.parent.parent`        | `cointicker` 찾기 | ✅ 올바름                  |
| `gui/modules/pipeline_module.py`  | `parent.parent.parent`        | `cointicker` 찾기 | ✅ 올바름                  |
| `gui/modules/backend_module.py`   | `parent.parent.parent.parent` | PICU 루트 찾기    | ⚠️ 깊이에 따라 다름        |

### 권장 해결책

**공통 유틸리티 함수 도입**으로 모든 경로 계산을 표준화하는 것이 가장 효과적입니다.

---

**보고서 작성자**: AI Assistant
**검토 필요**: 백엔드 포트 파일 경로 수정 후 재테스트 권장
**추가 권장사항**: 경로 계산 통합 및 표준화 작업 진행 권장
