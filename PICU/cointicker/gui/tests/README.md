# GUI 테스트

GUI 애플리케이션의 테스트 파일을 포함하는 디렉토리입니다.

## 📋 테스트 파일

### `test_refactoring.py` ⚠️ 비활성화됨

리팩토링 후 모듈 구조 및 import 테스트

**⚠️ 주의**: 리팩토링이 완료되어 통합 테스트 스크립트(`run_all_tests.sh`)에서 자동 실행되지 않습니다.
필요시 수동으로 실행할 수 있습니다: `python3 gui/tests/test_refactoring.py`

- UI 탭 모듈 import 테스트
- 매니저 모듈 import 테스트
- 매니저 인스턴스 생성 테스트
- PipelineOrchestrator 테스트
- UI 탭 클래스 구조 테스트
- 매니저 메서드 테스트
- app.py 구조 테스트

### `test_integration.py`

실제 기능 동작 통합 테스트

- PipelineOrchestrator 통합 테스트
- 매니저 메서드 호출 테스트
- UI 탭 구조 테스트

### `test_tier2_monitor.py`

Tier2Monitor 단위 테스트

- 헬스 체크 테스트
- 대시보드 요약 조회 테스트
- 포트 파일 읽기 테스트
- 재시도 메커니즘 테스트

### `test_config_manager.py`

ConfigManager 단위 테스트

- 설정 로드/저장 테스트
- 설정 값 가져오기/설정하기 테스트
- 기본 설정 생성 테스트
- 설정 유효성 검사 테스트
- 캐싱 테스트

### `test_module_manager.py`

ModuleManager 단위 테스트

- 모듈 등록 테스트
- 모듈 로드 테스트
- 모듈 상태 조회 테스트
- 명령어 실행 테스트
- 캐싱 테스트

## 🚀 실행 방법

### 개별 테스트 실행

```bash
# 리팩토링 테스트 (수동 실행, 통합 테스트에서는 자동 실행되지 않음)
python gui/tests/test_refactoring.py

# 통합 테스트
python gui/tests/test_integration.py

# Tier2Monitor 테스트
python gui/tests/test_tier2_monitor.py

# ConfigManager 테스트
python gui/tests/test_config_manager.py

# ModuleManager 테스트
python gui/tests/test_module_manager.py
```

### pytest로 실행

```bash
# 모든 GUI 테스트 실행
pytest gui/tests/ -v

# 특정 테스트 파일 실행
pytest gui/tests/test_refactoring.py -v  # 수동 실행 가능 (통합 테스트에서는 자동 실행되지 않음)
pytest gui/tests/test_integration.py -v
pytest gui/tests/test_tier2_monitor.py -v
pytest gui/tests/test_config_manager.py -v
pytest gui/tests/test_module_manager.py -v
```

## 📝 테스트 결과

테스트 실행 시 다음을 확인합니다:

- ✅ 모든 모듈이 정상적으로 import되는지
- ✅ 인스턴스 생성이 정상적으로 작동하는지
- ✅ 메서드가 올바르게 정의되어 있는지
- ✅ 통합 기능이 정상적으로 작동하는지

## 🔗 통합 테스트 연동

GUI 테스트는 상위 통합 테스트 스크립트(`tests/run_all_tests.sh`)에 자동으로 포함되어 있습니다.

### 통합 테스트에서 GUI 테스트 실행

```bash
# 전체 테스트 실행 (GUI 테스트 포함)
bash tests/run_all_tests.sh

# GUI 테스트만 포함하여 Unit 테스트 실행
bash tests/run_all_tests.sh --skip-integration --skip-process
```

### 통합 테스트에서 GUI 테스트 제외

```bash
# GUI 테스트 제외하고 실행
bash tests/run_all_tests.sh --skip-unit
# 또는 Unit 테스트는 실행하되 GUI 테스트만 제외하려면
# run_all_tests.sh를 수정하여 GUI 테스트 섹션을 주석 처리
```

---

**참고**:

- 프로젝트 전체 테스트는 `tests/` 디렉토리를 참고하세요.
- `tests/run_all_tests.sh`는 `tests/`와 `gui/tests/` 디렉토리의 모든 테스트를 자동으로 실행합니다.
