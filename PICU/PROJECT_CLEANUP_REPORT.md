# PICU 프로젝트 전역 점검 및 정리 보고서

> **생성일**: 2025-11-29
> **점검 범위**: PICU 프로젝트 전체 구조 및 BIGDATA 프로젝트 통합 상태

---

## 📊 전역 점검 결과

### ✅ 정리 완료된 부분

1. **GUI 디렉토리 구조**

   - ✅ 모니터링 파일 → `gui/monitors/`로 이동
   - ✅ GUI 테스트 → `gui/tests/`로 통합
   - ✅ 스크립트 → `gui/scripts/`로 이동
   - ✅ 설정 파일 → `gui/config/`로 이동
   - ✅ 문서 → `gui/docs/`로 이동

2. **Backend 디렉토리 구조**

   - ✅ 데이터베이스 파일 → `backend/data/`로 이동
   - ✅ 실행 스크립트 → `backend/scripts/`로 이동
   - ✅ 모델 파일 → `backend/models/`로 이동

3. **Worker-nodes 디렉토리 구조**

   - ✅ Kafka 관련 파일 → `worker-nodes/kafka/`로 이동
   - ✅ 실행 스크립트 → `worker-nodes/scripts/`로 이동
   - ✅ Scrapy 설정 → `worker-nodes/cointicker/`로 이동

4. **Frontend 디렉토리 구조**

   - ✅ 실행 스크립트 → `frontend/scripts/`로 이동
   - ✅ 정적 파일 → `frontend/public/`로 정리

5. **프로젝트 루트**
   - ✅ 문서 파일 → `docs/`로 이동

### ⚠️ 추가 정리 필요 사항

#### PICU 루트 디렉토리 정리

현재 PICU 루트에 있는 파일들:

```
PICU/
├── requirements.txt              # 통합 의존성 (유지)
├── requirements-master.txt       # → requirements/로 이동 권장
├── requirements-tier2.txt        # → requirements/로 이동 권장
├── requirements-worker.txt       # → requirements/로 이동 권장
├── start.sh                      # → scripts/로 이동 권장
├── config/                       # 유지 (PICU 전역 설정)
└── deployment/                   # 유지
```

**권장 정리:**

1. `requirements-*.txt` 파일들을 `requirements/` 디렉토리로 이동
2. `start.sh`를 `scripts/` 디렉토리로 이동 (또는 `scripts/start.sh`로 심볼릭 링크)

---

## 🔍 프로젝트 통합 상태 분석

### 다른 프로젝트들의 PICU 통합 여부

#### ✅ PICU 내부에서 독립적으로 작성된 코드

**중요**: PICU는 학습 자료 프로젝트의 코드를 전혀 사용하지 않습니다. 모든 코드는 PICU 내부에서 독립적으로 작성되었습니다.

1. **Scrapy 구현** → **PICU 내부 작성**

   - 위치: `PICU/cointicker/worker-nodes/cointicker/`
   - Spider: 5개 구현 완료 (PICU 내부 작성)
   - Pipeline: HDFS, Kafka 통합 완료
   - 상태: ✅ PICU 독립 작성, 프로덕션 레벨

2. **Selenium 유틸리티** → **PICU 내부 작성**

   - 위치: `PICU/cointicker/shared/selenium_utils.py`
   - 사용처: Scrapy middlewares에서 동적 콘텐츠 처리
   - 상태: ✅ PICU 독립 작성

3. **Kafka 클라이언트** → **PICU 내부 작성**

   - 위치:
     - `PICU/cointicker/shared/kafka_client.py` (클라이언트)
     - `PICU/cointicker/worker-nodes/kafka/` (Consumer)
   - 사용처: 실시간 데이터 스트리밍
   - 상태: ✅ PICU 독립 작성, 프로덕션 레벨

4. **HDFS 클라이언트 및 MapReduce** → **PICU 내부 작성**
   - 위치:
     - `PICU/cointicker/shared/hdfs_client.py` (클라이언트)
     - `PICU/cointicker/worker-nodes/mapreduce/` (Python MapReduce)
   - 사용처: 분산 데이터 저장 및 처리
   - 상태: ✅ PICU 독립 작성 (Python 기반)
   - 참고: `hadoop_project/examples/`의 Java 파일들은 학습용이며 PICU에서 사용하지 않음

### 독립 프로젝트들의 역할

다음 프로젝트들은 **학습/실습 자료**로 유지하는 것이 좋습니다:

1. **selenium_project/** - Selenium 기초 학습
2. **kafka_project/** - Kafka 클러스터 설정 및 실습
3. **hadoop_project/** - Hadoop 설정 및 MapReduce 실습
4. **scrapy_project/** - Scrapy 기초 학습

**중요**: 이들은 PICU와는 별개로:

- 학습 자료로 활용
- 새로운 기능 실험
- 참고 문서 제공
- **PICU는 이들의 코드를 전혀 사용하지 않음**

**Hadoop Java 파일 위치:**

- `hadoop_project/examples/src/main/java/bigdata/hadoop/demo/WordCount.java` 등
- PICU는 Python MapReduce 사용 (`worker-nodes/mapreduce/cleaner_mapper.py`)

---

## 💡 PICU 프로젝트 분리 제안

### 옵션 1: PICU만 별도 디렉토리로 분리 (권장)

**장점:**

- ✅ 프로덕션 프로젝트와 학습 프로젝트 분리
- ✅ PICU 프로젝트만 독립적으로 관리 가능
- ✅ 배포 및 버전 관리 용이
- ✅ 다른 프로젝트들은 학습 자료로 유지

**구조:**

```
bigdata/
├── PICU/                    # 프로덕션 프로젝트 (독립)
│   ├── cointicker/
│   ├── picu-dashboard/
│   ├── PICU_docs/
│   └── ...
│
├── selenium_project/        # 학습 자료 (유지)
├── kafka_project/          # 학습 자료 (유지)
├── hadoop_project/         # 학습 자료 (유지)
└── scrapy_project/         # 학습 자료 (유지)
```

### 옵션 2: 현재 구조 유지

**장점:**

- ✅ 모든 프로젝트가 한 곳에 모여 있음
- ✅ 관련 문서 참조 용이

**단점:**

- ⚠️ 프로덕션과 학습 자료가 혼재
- ⚠️ 프로젝트 규모가 커질수록 관리 복잡

---

## 🎯 최종 권장 사항

### 1. PICU 루트 디렉토리 정리 (즉시 실행 가능)

```bash
# requirements 파일 정리
mkdir -p PICU/requirements
mv PICU/requirements-*.txt PICU/requirements/

# start.sh 정리
mv PICU/start.sh PICU/scripts/start.sh
# 또는 심볼릭 링크 생성
ln -s scripts/start.sh PICU/start.sh
```

### 2. PICU 프로젝트 분리 (선택 사항)

**권장**: PICU를 별도 디렉토리로 분리

이유:

- PICU는 이미 다른 프로젝트들의 기능을 모두 통합
- 독립적인 프로덕션 프로젝트로 관리하는 것이 적절
- 다른 프로젝트들은 학습 자료로 유지

**분리 방법:**

```bash
# 새 위치로 PICU 이동 (예: ~/projects/PICU)
mv bigdata/PICU ~/projects/PICU

# 또는 bigdata 내에서 별도 관리
# (현재 구조 유지)
```

---

## 📋 체크리스트

### 즉시 정리 가능

- [ ] PICU 루트의 requirements 파일들을 `requirements/` 디렉토리로 이동
- [ ] `start.sh`를 `scripts/` 디렉토리로 이동 또는 심볼릭 링크 생성

### 검토 필요

- [ ] PICU 프로젝트를 별도 디렉토리로 분리할지 결정
- [ ] 다른 프로젝트들의 역할 재정의 (학습 자료 vs 프로덕션)

---

**결론**: PICU 프로젝트는 이미 다른 프로젝트들의 기능을 모두 통합했으므로, 프로덕션 프로젝트로 독립 관리하는 것을 권장합니다. 다른 프로젝트들은 학습 자료로 유지하는 것이 좋습니다.
