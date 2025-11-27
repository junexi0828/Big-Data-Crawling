# 테스트 디렉토리

코인티커 프로젝트의 모든 테스트 파일과 스크립트가 포함되어 있습니다.

## 📁 파일 구조

- `test_spiders.py` - Spider 모듈 테스트
- `test_utils.py` - 유틸리티 함수 테스트
- `test_mapreduce.py` - MapReduce 작업 테스트
- `test_backend.py` - Backend API 및 서비스 테스트
- `test_integration.py` - 통합 파이프라인 테스트
- `run_tests.sh` - 기본 테스트 스크립트 (의존성 없이 구조 검사)
- `run_integration_tests.sh` - 통합 테스트 스크립트 (가상환경 + 의존성 설치 + 전체 테스트)

## 🚀 사용 방법

### 통합 테스트 실행 (권장)

```bash
bash tests/run_integration_tests.sh
```

### 기본 테스트 실행

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
- `test_results.txt` - 테스트 결과 요약
- `test_log.txt` - 상세 테스트 로그

---

**테스트 디렉토리 안내**

