# PYTHONPATH 문제 분석 및 해결 방안

**분석 일시**: 2025-12-03
**목적**: PYTHONPATH 설정 충돌 및 중복 문제 파악 및 해결

---

## 🔴 문제 상황

### 발견된 PYTHONPATH 설정 (총 50개 이상)

전체 프로젝트에서 **50개 이상의 파일**에서 PYTHONPATH 또는 sys.path를 조작하고 있습니다.

---

## 📊 문제 분류

### 1. **Shell 스크립트의 PYTHONPATH 설정 (6개)**

#### A. Backend 실행 스크립트
```bash
# cointicker/backend/scripts/run_server.sh:56
export PYTHONPATH="$PROJECT_ROOT/cointicker:$PYTHONPATH"

# cointicker/backend/scripts/run_server.sh:66
export PYTHONPATH="$(pwd):$PYTHONPATH"  # ← 중복 설정!
```

**문제**: 같은 스크립트에서 2번 설정 (충돌 가능)

#### B. Kafka Consumer 스크립트
```bash
# cointicker/worker-nodes/scripts/run_kafka_consumer.sh:36
export PYTHONPATH="$PROJECT_ROOT/cointicker:$PYTHONPATH"
```

#### C. Tier2 Scheduler 서비스
```bash
# deployment/create_tier2_scheduler_service.sh:40
Environment="PYTHONPATH=$PROJECT_DIR:$PROJECT_DIR/shared"

# deployment/create_tier2_scheduler_service.sh:80
Environment="PYTHONPATH=$PROJECT_DIR:$PROJECT_DIR/shared"  # ← 동일 설정 2번
```

#### D. 테스트 스크립트
```bash
# cointicker/tests/run_all_tests.sh:384
export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"

# cointicker/tests/run_all_tests.sh:814
export PYTHONPATH="$PROJECT_ROOT/worker-nodes:$PYTHONPATH"  # ← 충돌!

# cointicker/tests/run_all_tests.sh:852
export PYTHONPATH="$PROJECT_ROOT/worker-nodes:$PYTHONPATH"  # ← 중복!
```

---

### 2. **Python 파일의 sys.path.insert(0, ...) (40개 이상)**

#### A. 패턴 1: 프로젝트 루트 추가
```python
# cointicker/gui/main.py:11
sys.path.insert(0, str(project_root))

# cointicker/scripts/run_pipeline.py:12
sys.path.insert(0, str(project_root))

# cointicker/scripts/run_pipeline_scheduler.py:13
sys.path.insert(0, str(project_root))

# ... 20개 이상
```

#### B. 패턴 2: shared 디렉토리 추가
```python
# cointicker/worker-nodes/kafka/kafka_consumer.py:20
sys.path.insert(0, str(shared_path))

# cointicker/worker-nodes/cointicker/pipelines.py:23
sys.path.insert(0, str(shared_path))

# cointicker/worker-nodes/cointicker/pipelines/kafka_pipeline.py:23
sys.path.insert(0, str(shared_path))

# ... 10개 이상
```

#### C. 패턴 3: worker-nodes 추가
```python
# cointicker/tests/test_spiders.py:11
sys.path.insert(0, str(Path(__file__).parent.parent / "worker-nodes"))

# cointicker/tests/test_integration.py:24
sys.path.insert(0, str(Path(__file__).parent.parent / "worker-nodes"))

# ... 5개 이상
```

#### D. 패턴 4: 복합 설정
```python
# cointicker/gui/modules/spider_module.py:179-191
env = os.environ.copy()
pythonpath = env.get("PYTHONPATH", "")
paths = [
    str(worker_nodes_path),
    str(project_root),
    pythonpath
]
env["PYTHONPATH"] = ":".join(paths)
```

---

## 🔍 근본 원인

### 1. **프로젝트 구조 문제**

```
PICU/
├── cointicker/              # 실제 프로젝트 루트?
│   ├── shared/             # 공통 모듈
│   ├── worker-nodes/       # Scrapy
│   ├── backend/            # FastAPI
│   ├── gui/                # PyQt5
│   └── tests/              # 테스트
└── ...
```

**문제**: `cointicker`가 프로젝트 루트처럼 동작하지만, 실제 루트는 `PICU`
- `import shared.utils` → `cointicker/shared/utils.py`를 찾아야 함
- 하지만 Python은 `PICU/shared/utils.py`를 찾으려고 함
- 결과: 모든 파일에서 `sys.path.insert(0, ...)` 필요

### 2. **일관성 없는 import 방식**

```python
# 방법 1: 절대 import (from shared import ...)
from shared.utils import generate_hash  # ← sys.path 조작 필요

# 방법 2: 상대 import (from ..shared import ...)
from ..shared.utils import generate_hash  # ← 패키지 구조 필요

# 방법 3: 직접 경로
sys.path.insert(0, str(Path(__file__).parent.parent / "shared"))
from shared.utils import generate_hash
```

### 3. **실행 위치에 따른 경로 차이**

```bash
# 케이스 1: PICU 루트에서 실행
cd PICU
python cointicker/gui/main.py
# → sys.path에 PICU가 추가됨
# → import shared 실패!

# 케이스 2: cointicker에서 실행
cd PICU/cointicker
python gui/main.py
# → sys.path에 cointicker가 추가됨
# → import shared 성공!

# 케이스 3: 스크립트로 실행
cd PICU
bash scripts/start.sh
# → PYTHONPATH를 명시적으로 설정
```

---

## 💡 해결 방안

### 방안 1: **표준 Python 패키지 구조로 전환 (권장)**

#### 현재 구조:
```
PICU/
└── cointicker/
    ├── shared/
    ├── worker-nodes/
    ├── backend/
    └── gui/
```

#### 개선 구조:
```
PICU/
├── setup.py                # 패키지 설정
├── pyproject.toml          # 모던 패키지 설정
└── cointicker/
    ├── __init__.py         # 패키지 초기화
    ├── shared/
    │   └── __init__.py
    ├── workers/            # worker-nodes 이름 변경
    │   └── __init__.py
    ├── backend/
    │   └── __init__.py
    └── gui/
        └── __init__.py
```

#### setup.py 생성:
```python
# PICU/setup.py
from setuptools import setup, find_packages

setup(
    name="cointicker",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        # requirements.txt의 내용
    ],
    python_requires=">=3.8",
)
```

#### 설치:
```bash
cd PICU
pip install -e .  # editable install

# 이제 어디서든:
from cointicker.shared.utils import generate_hash
from cointicker.workers.spiders import UpbitTrendsSpider
from cointicker.backend.app import app
```

**장점**:
- ✅ sys.path 조작 불필요
- ✅ import가 일관적
- ✅ IDE 자동완성 작동
- ✅ 표준 Python 방식

**단점**:
- ⚠️ 대규모 리팩토링 필요
- ⚠️ 모든 import 문 수정 필요

---

### 방안 2: **통합 PYTHONPATH 설정 스크립트 (중간)**

#### env_setup.sh 생성:
```bash
# PICU/scripts/env_setup.sh
#!/bin/bash
# 모든 스크립트에서 source하여 사용

export PICU_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PYTHONPATH="$PICU_ROOT/cointicker:$PICU_ROOT/cointicker/shared:$PYTHONPATH"

echo "✅ PYTHONPATH 설정 완료"
echo "   PICU_ROOT: $PICU_ROOT"
echo "   PYTHONPATH: $PYTHONPATH"
```

#### 모든 스크립트에서 사용:
```bash
# scripts/start.sh
source "$(dirname "$0")/env_setup.sh"
# ... 나머지 코드

# cointicker/backend/scripts/run_server.sh
source "$PICU_ROOT/scripts/env_setup.sh"
# ... 나머지 코드
```

**장점**:
- ✅ 한 곳에서 관리
- ✅ 일관성 보장
- ✅ 수정 비용 낮음

**단점**:
- ⚠️ 여전히 환경 변수 의존
- ⚠️ Python 파일은 여전히 sys.path 조작 필요

---

### 방안 3: **sitecustomize.py 활용 (간단)**

#### sitecustomize.py 생성:
```python
# PICU/cointicker/sitecustomize.py
"""
Python 시작 시 자동으로 실행되는 모듈
PYTHONPATH를 자동으로 설정
"""
import sys
from pathlib import Path

# cointicker 루트 찾기
current_file = Path(__file__).resolve()
cointicker_root = current_file.parent
picu_root = cointicker_root.parent

# sys.path에 추가 (중복 방지)
paths_to_add = [
    str(cointicker_root),
    str(cointicker_root / "shared"),
]

for path in paths_to_add:
    if path not in sys.path:
        sys.path.insert(0, path)
```

#### 환경 변수 설정:
```bash
export PYTHONPATH="$PICU_ROOT/cointicker:$PYTHONPATH"
```

**장점**:
- ✅ Python 시작 시 자동 적용
- ✅ 간단한 구현

**단점**:
- ⚠️ 모든 Python 프로세스에 영향
- ⚠️ 디버깅 어려움

---

## 🎯 권장 솔루션 (단계적 접근)

### Phase 1: 즉시 실행 (긴급 수정)

#### 1.1 통합 환경 설정 스크립트 생성

```bash
# PICU/scripts/setup_env.sh
#!/bin/bash
# PICU 프로젝트 환경 설정

export PICU_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export COINTICKER_ROOT="$PICU_ROOT/cointicker"

# PYTHONPATH 설정 (중복 제거)
export PYTHONPATH="$COINTICKER_ROOT:$COINTICKER_ROOT/shared:$PYTHONPATH"

# 가상환경 활성화 (있으면)
if [ -f "$PICU_ROOT/venv/bin/activate" ]; then
    source "$PICU_ROOT/venv/bin/activate"
fi

echo "✅ PICU 환경 설정 완료"
```

#### 1.2 .env 파일 생성 (Python용)

```bash
# PICU/.env
PICU_ROOT=/Users/juns/code/personal/notion/pknu_workspace/bigdata/PICU
COINTICKER_ROOT=/Users/juns/code/personal/notion/pknu_workspace/bigdata/PICU/cointicker
PYTHONPATH=/Users/juns/code/personal/notion/pknu_workspace/bigdata/PICU/cointicker:/Users/juns/code/personal/notion/pknu_workspace/bigdata/PICU/cointicker/shared
```

#### 1.3 공통 path_utils.py 생성

```python
# PICU/cointicker/shared/path_utils.py
"""
경로 설정 유틸리티
모든 Python 파일에서 import하여 사용
"""
import sys
from pathlib import Path

def setup_pythonpath():
    """PYTHONPATH 설정 (중복 방지)"""
    # cointicker 루트 찾기
    current_file = Path(__file__).resolve()
    shared_dir = current_file.parent  # shared/
    cointicker_root = shared_dir.parent  # cointicker/

    paths_to_add = [
        str(cointicker_root),
        str(shared_dir),
    ]

    for path in paths_to_add:
        if path not in sys.path:
            sys.path.insert(0, path)

# 자동 실행
setup_pythonpath()
```

#### 1.4 모든 Python 파일 수정

**변경 전**:
```python
# 각 파일마다 다른 경로 설정
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "shared"))
# ...
from shared.utils import generate_hash
```

**변경 후**:
```python
# 한 줄로 통일
from shared.path_utils import setup_pythonpath
setup_pythonpath()

from shared.utils import generate_hash
```

---

### Phase 2: 중기 개선 (1-2주)

#### 2.1 __init__.py 추가

모든 디렉토리에 `__init__.py` 추가하여 패키지화:

```bash
touch cointicker/__init__.py
touch cointicker/shared/__init__.py
touch cointicker/worker-nodes/__init__.py
touch cointicker/backend/__init__.py
touch cointicker/gui/__init__.py
```

#### 2.2 import 문 일관성 개선

```python
# 절대 import로 통일
from shared.utils import generate_hash
from shared.kafka_client import KafkaProducerClient
from shared.hdfs_client import HDFSClient
```

---

### Phase 3: 장기 개선 (1개월)

#### 3.1 setup.py 기반 패키지화

```bash
cd PICU
pip install -e .

# 이후 어디서든:
from cointicker.shared.utils import generate_hash
```

---

## 📋 즉시 수정 체크리스트

### Shell 스크립트 수정

- [ ] `scripts/setup_env.sh` 생성
- [ ] `scripts/start.sh`에서 source
- [ ] `cointicker/backend/scripts/run_server.sh` 중복 제거
- [ ] `cointicker/worker-nodes/scripts/run_kafka_consumer.sh` 통합
- [ ] `cointicker/tests/run_all_tests.sh` 정리

### Python 파일 수정

- [ ] `cointicker/shared/path_utils.py` 생성
- [ ] 모든 Python 파일에서 `from shared.path_utils import setup_pythonpath` 사용
- [ ] 중복 `sys.path.insert()` 제거

---

## 🚨 위험 요소

1. **대규모 수정 필요**
   - 50개 이상의 파일 수정
   - 테스트 필요

2. **import 오류 가능성**
   - 경로 설정 실수 시 import 실패
   - 철저한 테스트 필요

3. **실행 위치 의존성**
   - 여전히 실행 위치에 따라 동작 다를 수 있음
   - setup.py 패키지화가 근본 해결

---

## 🎯 최종 권장사항

### 지금 당장:
1. ✅ **통합 환경 스크립트 생성** (`scripts/setup_env.sh`)
2. ✅ **공통 path_utils.py 생성** (`cointicker/shared/path_utils.py`)
3. 🟡 **중복 PYTHONPATH 설정 제거** (점진적)

### 다음 주:
1. 🟡 **모든 __init__.py 추가**
2. 🟡 **import 문 일관성 개선**

### 다음 달:
1. 🔵 **setup.py 기반 패키지화**
2. 🔵 **모든 sys.path 조작 제거**

---

**작성일**: 2025-12-03
**작성자**: Claude Code
**다음 액션**: setup_env.sh 및 path_utils.py 생성
