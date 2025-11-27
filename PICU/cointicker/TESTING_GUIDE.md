# 코인티커 프로젝트 테스트 가이드

## 🧪 테스트 개요

코인티커 프로젝트의 통합 테스트는 가상환경 설정부터 모든 테스트 실행까지 자동화되어 있습니다.

## 🚀 빠른 시작

### 통합 테스트 실행 (권장)

```bash
cd cointicker
bash tests/run_integration_tests.sh
```

이 스크립트는 다음을 자동으로 수행합니다:

1. ✅ Python 버전 확인
2. ✅ 가상환경 생성/활성화
3. ✅ pip 업그레이드
4. ✅ 의존성 설치 (`requirements.txt`)
5. ✅ Python 문법 검사
6. ✅ 모듈 Import 테스트
7. ✅ Unit 테스트 실행

### 테스트 결과

테스트 완료 후 다음 파일들이 생성됩니다:

- `tests/test_results.txt` - 테스트 결과 요약
- `tests/test_log.txt` - 상세 테스트 로그

## 📋 수동 테스트

### 1. 가상환경 설정

```bash
# 가상환경 생성
python3 -m venv venv

# 가상환경 활성화
source venv/bin/activate  # Linux/Mac
# 또는
venv\Scripts\activate  # Windows
```

### 2. 의존성 설치

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. 개별 테스트 실행

#### A. Python 문법 검사

```bash
find . -name "*.py" -type f ! -path "*/venv/*" -exec python3 -m py_compile {} \;
```

#### B. Unit 테스트

```bash
# 전체 테스트
python3 -m unittest discover tests -v

# 특정 테스트만 실행
python3 -m unittest tests.test_utils
python3 -m unittest tests.test_mapreduce
```

#### C. Spider 테스트

```bash
cd worker-nodes

# Upbit Trends Spider
scrapy crawl upbit_trends -o output.json

# Coinness Spider
scrapy crawl coinness -o output.json
```

#### D. 백엔드 API 테스트

```bash
cd backend

# 데이터베이스 초기화
python init_db.py

# 서버 실행
python app.py

# 다른 터미널에서 테스트
curl http://localhost:5000/health
curl http://localhost:5000/api/dashboard/summary
```

#### E. MapReduce 테스트

```bash
cd worker-nodes/mapreduce

# 테스트 데이터 생성
echo '{"source":"upbit","symbol":"BTC","price":50000,"timestamp":"2025-11-27T10:00:00"}' > test_input.json

# Mapper 테스트
cat test_input.json | python3 cleaner_mapper.py

# 전체 파이프라인 테스트
cat test_input.json | python3 cleaner_mapper.py | sort | python3 cleaner_reducer.py
```

## 📊 테스트 커버리지

### 구조적 테스트

- ✅ Python 문법 검사 (40개 파일)
- ✅ 모듈 Import 테스트
- ✅ 파일 구조 확인

### 기능 테스트

- ✅ Utils 함수 테스트
- ✅ MapReduce 로직 테스트
- ✅ Spider 구조 테스트
- ✅ Backend 모델 테스트
- ✅ 서비스 레이어 테스트

### 통합 테스트

- ✅ 데이터 파이프라인 테스트
- ✅ API 엔드포인트 테스트
- ✅ 전체 워크플로우 테스트

## 🐛 문제 해결

### 가상환경 오류

```bash
# 가상환경 재생성
rm -rf venv
python3 -m venv venv
source venv/bin/activate
```

### 의존성 설치 오류

```bash
# pip 업그레이드 후 재설치
pip install --upgrade pip
pip install --upgrade -r requirements.txt
```

### Import 오류

```bash
# Python 경로 확인
python3 -c "import sys; print('\n'.join(sys.path))"

# 프로젝트 루트를 PYTHONPATH에 추가
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### 데이터베이스 연결 오류

```bash
# 설정 확인
cat config/database_config.yaml

# SQLite로 테스트 (MariaDB 없을 때)
export DATABASE_TYPE=sqlite
```

## 📝 테스트 파일 구조

```
tests/
├── __init__.py
├── test_spiders.py          # Spider 테스트
├── test_utils.py            # 유틸리티 테스트
├── test_mapreduce.py        # MapReduce 테스트
├── test_backend.py          # Backend 테스트
├── test_integration.py      # 통합 테스트
├── run_tests.sh             # 기본 테스트 스크립트
└── run_integration_tests.sh # 통합 테스트 스크립트 (권장)
```

## ✅ 테스트 체크리스트

### 통합 테스트 실행 전

- [ ] Python 3.8+ 설치 확인
- [ ] 인터넷 연결 확인 (의존성 다운로드)
- [ ] 충분한 디스크 공간 확인

### 통합 테스트 실행 후

- [ ] 모든 문법 검사 통과
- [ ] 모든 모듈 Import 성공
- [ ] Unit 테스트 통과
- [ ] 테스트 결과 파일 생성 확인

## 🎯 CI/CD 통합

통합 테스트 스크립트는 CI/CD 파이프라인에서도 사용할 수 있습니다:

```yaml
# GitHub Actions 예시
- name: Run Integration Tests
  run: |
    bash tests/run_integration_tests.sh
```

---

**테스트 가이드 완료! ✅**
