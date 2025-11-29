# 테스트 디렉토리

코인티커 프로젝트의 모든 테스트 파일과 스크립트가 포함되어 있습니다.

## 📁 파일 구조

### 테스트 스크립트

- `run_all_tests.sh` - **통합 테스트 스크립트 (권장)** - 모든 테스트를 단계별로 실행
- `run_tests.sh` - 기본 테스트 스크립트 (의존성 없이 구조 검사)
- `run_integration_tests.sh` - 레거시 통합 테스트 스크립트 (호환성 유지)

### Unit 테스트 파일

**기본 테스트 (`tests/` 디렉토리):**

- `test_spiders.py` - Spider 모듈 테스트
- `test_utils.py` - 유틸리티 함수 테스트
- `test_mapreduce.py` - MapReduce 작업 테스트
- `test_backend.py` - Backend API 및 서비스 테스트
- `test_integration.py` - 통합 파이프라인 테스트

**GUI 테스트 (`gui/tests/` 디렉토리):**

- `test_tier2_monitor.py` - Tier2Monitor 단위 테스트
- `test_config_manager.py` - ConfigManager 단위 테스트
- `test_module_manager.py` - ModuleManager 단위 테스트
- `test_integration.py` - GUI 통합 테스트 (PipelineOrchestrator 등)
- `test_refactoring.py` - GUI 리팩토링 테스트 (모듈 import 및 구조 확인)

> **참고**: `run_all_tests.sh`는 `tests/`와 `gui/tests/` 디렉토리의 모든 테스트를 자동으로 실행합니다.

## 🚀 사용 방법

### 통합 테스트 실행 (권장)

#### 1. 일반 모드 (기본): 상태만 확인

```bash
# 전체 테스트 실행 (서비스 상태만 확인)
bash tests/run_all_tests.sh
```

**일반 모드 특징:**

- ✅ 서비스가 실행 중인지 상태만 확인
- ✅ 서비스가 없으면 스크립트 경로 안내
- ✅ WARNING은 실패가 아닌 보류(스킵)로 처리
- ✅ 빠르고 안전한 테스트 (서비스 실행 없음)

#### 2. 서비스 자동 시작 모드: 실제 실행

```bash
# 서비스 자동 시작 모드 (실제 실행)
bash tests/run_all_tests.sh --start-services
```

**서비스 자동 시작 모드 특징:**

- 🚀 Backend, Frontend 서비스를 실제로 시작
- 🚀 Kafka Consumer, MapReduce 스크립트 실행
- 🚀 Spider 실제 실행 및 결과 확인
- ⚠️ WARNING과 ERROR는 모두 실패로 기록
- ⚠️ 서비스가 이미 실행 중이면 건너뜀

#### 3. 기타 옵션

```bash
# 빠른 테스트 (환경 설정 및 일부 테스트 스킵)
bash tests/run_all_tests.sh --quick

# 특정 테스트만 스킵
bash tests/run_all_tests.sh --skip-unit --skip-process

# 서비스 자동 시작 + 상세 출력
bash tests/run_all_tests.sh --start-services --verbose
```

### 옵션 설명

- `-s, --start-services`: **서비스 자동 시작 모드** - Backend, Frontend, Kafka, MapReduce, Spider를 실제로 실행하고 결과 확인
- `-q, --quick`: 빠른 테스트 모드 (환경 설정 스킵, 기본 테스트만)
- `-e, --skip-env`: 환경 설정 스킵 (가상환경, 의존성)
- `-u, --skip-unit`: Unit 테스트 스킵
- `-i, --skip-integration`: 통합 테스트 스킵
- `-p, --skip-process`: 프로세스 흐름 테스트 스킵
- `-v, --verbose`: 상세 출력
- `-h, --help`: 도움말 표시

### 모드별 차이점

| 항목           | 일반 모드 (기본)   | 서비스 자동 시작 모드 (`--start-services`) |
| -------------- | ------------------ | ------------------------------------------ |
| Backend        | 상태만 확인        | 실제로 실행하고 health check               |
| Frontend       | 상태만 확인        | 실제로 실행하고 접속 확인                  |
| Kafka          | 스크립트 경로 안내 | 실제로 Consumer 실행                       |
| HDFS/MapReduce | 스크립트 경로 안내 | 스크립트 유효성 확인                       |
| Spider         | 프로젝트 구조 확인 | 실제로 Spider 실행 및 결과 확인            |
| WARNING 처리   | 보류(스킵)로 처리  | 실패로 기록                                |
| ERROR 처리     | 실패로 기록        | 실패로 기록                                |

### 기본 테스트 실행 (레거시)

```bash
bash tests/run_tests.sh
```

### 개별 테스트 실행

```bash
# Utils 테스트
python3 -m unittest tests.test_utils

# MapReduce 테스트
python3 -m unittest tests.test_mapreduce

# Backend 테스트
python3 -m unittest tests.test_backend
```

## 📊 테스트 결과

테스트 실행 후 다음 파일들이 생성됩니다:

- `results/test_results.txt` - 테스트 결과 요약
- `results/test_log.txt` - 상세 테스트 로그
- `results/process_flow/` - 프로세스 흐름 테스트 결과

## 🔍 테스트 단계

`run_all_tests.sh`는 다음 단계로 구성됩니다:

1. **환경 설정**: Python 버전 확인, 가상환경 설정, 의존성 설치
2. **코드 품질 검사**: Python 문법 검사, 모듈 Import 테스트, Spider 구조 테스트
3. **Unit 테스트**:
   - `tests/` 디렉토리의 기본 Unit 테스트 (unittest)
   - `gui/tests/` 디렉토리의 GUI Unit 테스트 (unittest.TestCase 기반)
   - GUI 통합 테스트 스크립트 (`test_integration.py`, `test_refactoring.py`)
4. **통합 테스트**:
   - **일반 모드**: Backend, Frontend, Kafka, HDFS 서비스 상태 확인 (실행 안 함)
   - **서비스 자동 시작 모드**: 서비스를 실제로 실행하고 결과 확인
5. **프로세스 흐름 테스트**:
   - **일반 모드**: Spider 프로젝트 구조 확인
   - **서비스 자동 시작 모드**: Spider 실제 실행 및 데이터 수집 테스트

## ⚠️ 주의사항

- **일반 모드**: 서비스를 실행하지 않으므로 안전하고 빠릅니다. WARNING은 보류로 처리됩니다.
- **서비스 자동 시작 모드**: 실제로 서비스를 실행하므로 시간이 오래 걸릴 수 있고, 리소스를 사용합니다. WARNING도 실패로 기록됩니다.
- 서비스가 이미 실행 중이면 자동 시작 모드에서도 건너뜁니다.

---

**테스트 디렉토리 안내**
