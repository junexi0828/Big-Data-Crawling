# 테스트 문서

이 디렉토리에는 CoinTicker 프로젝트의 테스트 관련 문서가 포함되어 있습니다.

## 📚 문서 목록

### 테스트 가이드
- **[실사용자 흐름 테스트 가이드](TEST_USER_FLOW.md)**: 실제 사용자 흐름에 따른 전체 시스템 테스트 가이드
- **[빠른 테스트 가이드](QUICK_TEST.md)**: 핵심 기능만 빠르게 테스트하는 가이드

### 테스트 스크립트
- **`test_user_flow.sh`**: PICU 루트에 위치한 실사용자 흐름 테스트 스크립트
- **`run_integration_tests.sh`**: `cointicker/tests/` 디렉토리에 위치한 통합 테스트 스크립트
- **`run_tests.sh`**: `cointicker/tests/` 디렉토리에 위치한 단위 테스트 스크립트

## 🚀 빠른 시작

### 전체 시스템 테스트
```bash
# PICU 루트에서
bash test_user_flow.sh
```

### 빠른 테스트
```bash
# PICU 루트에서
source venv/bin/activate
bash run_gui.sh
```

## 📖 상세 문서

각 테스트 가이드의 상세 내용은 해당 문서를 참고하세요.

