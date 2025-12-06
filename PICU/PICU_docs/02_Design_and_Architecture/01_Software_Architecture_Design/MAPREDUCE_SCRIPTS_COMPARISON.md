# MapReduce 스크립트 비교 분석

**작성 일시**: 2025-12-03
**목적**: 기존 MapReduce 스크립트와 새로 생성한 스크립트의 차이점 및 통합 방안

---

## 📋 발견된 파일

### 기존 파일

1. **`cointicker/worker-nodes/mapreduce/run_cleaner.sh`**

   - 위치: `worker-nodes/mapreduce/` 디렉토리
   - 목적: 로컬 MapReduce 실행 (Hadoop Streaming 미사용)
   - 방식: HDFS → 로컬 다운로드 → Python 처리 → HDFS 업로드

2. **`cointicker/tests/test_mapreduce.py`**
   - 위치: `tests/` 디렉토리
   - 목적: Mapper/Reducer 함수 단위 테스트
   - 내용: `clean_data()`, `remove_duplicates()` 함수 테스트

### 새로 생성한 파일

1. **`cointicker/scripts/run_mapreduce.sh`**

   - 위치: `scripts/` 디렉토리
   - 목적: Hadoop Streaming을 사용한 클러스터 MapReduce 실행
   - 방식: Hadoop Streaming JAR 사용, 클러스터에서 직접 실행

2. **`cointicker/tests/test_hdfs_connection.py`**
   - 위치: `tests/` 디렉토리
   - 목적: HDFS 연결 및 기본 작업 테스트
   - 내용: 연결, 읽기, 쓰기, 삭제 기능 테스트

---

## 🔍 상세 비교

### 1. MapReduce 실행 스크립트 비교

#### `worker-nodes/mapreduce/run_cleaner.sh` (기존)

**특징**:

- 로컬에서 Python으로 MapReduce 작업 수행
- HDFS에서 데이터를 다운로드하여 로컬에서 처리
- 단일 노드 환경에 적합
- Hadoop Streaming 미사용

**실행 방식**:

```bash
# 1. HDFS에서 데이터 다운로드
hdfs dfs -get /raw/*/${DATE}/* ./data/input_${DATE}/

# 2. 로컬에서 Python으로 처리
cat ./data/input_${DATE}/*.json | \
    python3 cleaner_mapper.py | \
    sort | \
    python3 cleaner_reducer.py > ./data/output_${DATE}.json

# 3. 결과를 HDFS에 업로드
hdfs dfs -put ./data/output_${DATE}.json /cleaned/${DATE}/
```

**장점**:

- Hadoop 클러스터 없이도 실행 가능
- 디버깅이 쉬움
- 로컬 개발 환경에 적합

**단점**:

- 대용량 데이터 처리에 비효율적
- 클러스터의 분산 처리 이점을 활용하지 못함

#### `scripts/run_mapreduce.sh` (새로 생성)

**특징**:

- Hadoop Streaming을 사용한 클러스터 MapReduce 실행
- HDFS에 직접 접근하여 분산 처리
- 멀티 노드 클러스터 환경에 적합
- 실제 Hadoop MapReduce 프레임워크 사용

**실행 방식**:

```bash
# Hadoop Streaming으로 직접 실행
hadoop jar hadoop-streaming-*.jar \
    -mapper "python3 cleaner_mapper.py" \
    -reducer "python3 cleaner_reducer.py" \
    -input /user/cointicker/raw \
    -output /user/cointicker/cleaned \
    -file cleaner_mapper.py \
    -file cleaner_reducer.py
```

**장점**:

- 클러스터의 분산 처리 활용
- 대용량 데이터 처리에 효율적
- 실제 프로덕션 환경과 동일한 방식

**단점**:

- Hadoop 클러스터가 필요함
- 디버깅이 상대적으로 어려움

---

## ✅ 통합 방안

### 옵션 1: 두 스크립트 모두 유지 (권장)

**이유**:

- 서로 다른 목적과 환경을 위해 사용
- `run_cleaner.sh`: 로컬 개발/테스트용
- `run_mapreduce.sh`: 클러스터 프로덕션용

**사용 시나리오**:

- **로컬 개발**: `worker-nodes/mapreduce/run_cleaner.sh` 사용
- **클러스터 배포**: `scripts/run_mapreduce.sh` 사용

### 옵션 2: 통합 스크립트 생성

**방법**:

- 환경 변수나 인자로 실행 모드 선택
- 로컬 모드: 기존 `run_cleaner.sh` 방식
- 클러스터 모드: 새로 생성한 `run_mapreduce.sh` 방식

**예시**:

```bash
#!/bin/bash
# 통합 MapReduce 실행 스크립트

MODE="${1:-local}"  # local 또는 cluster

if [ "$MODE" = "cluster" ]; then
    # Hadoop Streaming 사용
    exec "$(dirname "$0")/../scripts/run_mapreduce.sh" "$@"
else
    # 로컬 처리
    exec "$(dirname "$0")/run_cleaner.sh" "$@"
fi
```

---

## 📝 테스트 파일 비교

### `tests/test_mapreduce.py` (기존)

**목적**: Mapper/Reducer 함수 단위 테스트

- `clean_data()` 함수 테스트
- `remove_duplicates()` 함수 테스트
- 유닛 테스트 수준

### `tests/test_hdfs_connection.py` (새로 생성)

**목적**: HDFS 연결 및 기본 작업 테스트

- HDFS 클라이언트 초기화 테스트
- 파일 읽기/쓰기/삭제 테스트
- 통합 테스트 수준

**결론**: 중복 없음, 서로 다른 목적

---

## 🎯 권장 사항

### 1. 스크립트 구조

```
cointicker/
├── scripts/
│   └── run_mapreduce.sh          # 클러스터용 (Hadoop Streaming)
└── worker-nodes/
    └── mapreduce/
        └── run_cleaner.sh        # 로컬용 (Python 직접 실행)
```

### 2. 문서화

각 스크립트에 사용 목적과 환경을 명시:

**`run_mapreduce.sh`**:

```bash
#!/bin/bash
# MapReduce 작업 실행 스크립트 (클러스터용)
# Hadoop Streaming을 사용하여 클러스터에서 MapReduce 작업을 실행합니다.
# 사용법: ./run_mapreduce.sh [INPUT_PATH] [OUTPUT_PATH]
# 요구사항: Hadoop 클러스터가 실행 중이어야 합니다.
```

**`run_cleaner.sh`**:

```bash
#!/bin/bash
# MapReduce 데이터 정제 작업 실행 스크립트 (로컬용)
# 로컬에서 Python으로 MapReduce 작업을 수행합니다.
# 사용법: ./run_cleaner.sh
# 요구사항: HDFS 접근 가능 (단일 노드 모드 가능)
```

### 3. 테스트 파일

두 테스트 파일 모두 유지:

- `test_mapreduce.py`: 함수 단위 테스트
- `test_hdfs_connection.py`: HDFS 통합 테스트

---

## 📊 최종 결론

### ✅ 중복 없음

1. **MapReduce 실행 스크립트**:

   - `run_cleaner.sh`: 로컬 개발용
   - `run_mapreduce.sh`: 클러스터 프로덕션용
   - **둘 다 유지 권장**

2. **테스트 파일**:
   - `test_mapreduce.py`: 함수 단위 테스트
   - `test_hdfs_connection.py`: HDFS 통합 테스트
   - **둘 다 유지 권장**

### 🔧 개선 사항

1. 각 스크립트에 사용 목적 명시
2. README에 두 스크립트의 차이점 문서화
3. 필요시 통합 스크립트 생성 (선택 사항)

---

**작성자**: Claude Code
**마지막 업데이트**: 2025-12-03
