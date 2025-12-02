# 배포 관점에서의 폴더 구조 및 의존성 관리 분석

**작성 일시**: 2025-12-02
**목적**: 라즈베리파이 배포를 고려한 올바른 프로젝트 구조 및 의존성 관리 방법

---

## 📦 현재 배포 구조 분석

### 1. 배포 대상 구분

```
개발 머신 (Mac)                    라즈베리파이 클러스터
===================                 ========================
PICU/
├── cointicker/         ──────────> /home/ubuntu/cointicker/
│   ├── master-node/    ──────────> Master: master-node/ + shared/
│   ├── worker-nodes/   ──────────> Worker: worker-nodes/ + shared/
│   ├── shared/
│   └── config/
├── scripts/            (배포 안 됨)
├── PICU_docs/          (배포 안 됨)
├── deployment/         (배포 안 됨)
└── venv/               (배포 안 됨)
```

### 2. 배포 스크립트 분석

#### setup_master.sh (Master Node)

```bash
# 배포되는 파일들
rsync -avz --exclude 'venv' \
    "$PROJECT_ROOT/cointicker/master-node/" \
    "$MASTER_USER@$MASTER_IP:$PROJECT_DIR/master-node/"

rsync -avz --exclude 'venv' \
    "$PROJECT_ROOT/cointicker/shared/" \
    "$MASTER_USER@$MASTER_IP:$PROJECT_DIR/shared/"

rsync -avz --exclude 'venv' \
    "$PROJECT_ROOT/cointicker/config/" \
    "$MASTER_USER@$MASTER_IP:$PROJECT_DIR/config/"

# 의존성 파일
rsync -avz \
    "$PROJECT_ROOT/requirements/requirements-master.txt" \
    "$MASTER_USER@$MASTER_IP:$PROJECT_DIR/"
```

#### setup_worker.sh (Worker Node)

```bash
# 배포되는 파일들
rsync -avz --exclude 'venv' \
    "$PROJECT_ROOT/cointicker/worker-nodes/" \
    "$WORKER_USER@$WORKER_IP:$PROJECT_DIR/worker-nodes/"

rsync -avz --exclude 'venv' \
    "$PROJECT_ROOT/cointicker/shared/" \
    "$WORKER_USER@$WORKER_IP:$PROJECT_DIR/shared/"

rsync -avz --exclude 'venv' \
    "$PROJECT_ROOT/cointicker/config/" \
    "$WORKER_USER@$WORKER_IP:$PROJECT_DIR/config/"

# 의존성 파일
rsync -avz \
    "$PROJECT_ROOT/requirements/requirements-worker.txt" \
    "$WORKER_USER@$WORKER_IP:$PROJECT_DIR/"
```

---

## ✅ 올바른 구조 판단

### 질문 1: cointicker 안에 venv가 필요한가?

**답변**: ❌ **필요 없음**

**이유**:

1. 배포 스크립트가 `--exclude 'venv'`로 venv를 제외하고 있음
2. 라즈베리파이에서 SSH로 직접 venv를 생성함:
   ```bash
   ssh "$MASTER_USER@$MASTER_IP" << EOF
       cd $PROJECT_DIR
       python3 -m venv venv  # 라즈베리파이에서 직접 생성
       source venv/bin/activate
       pip install -r requirements-master.txt
   EOF
   ```
3. 개발 머신의 venv를 배포하는 것이 아니라, 라즈베리파이에서 새로 만듦

**올바른 구조**:

```
PICU/
├── venv/               # ✅ 개발용 (Mac) - 유지
├── cointicker/
│   └── venv/           # ❌ 불필요 - 삭제 권장
└── scripts/
    └── venv/           # ❌ 불필요 - 삭제 권장
```

**권장 조치**:

```bash
# cointicker/venv와 scripts/venv는 삭제해도 됨
rm -rf ./cointicker/venv
rm -rf ./scripts/venv

# 루트 venv만 사용
# 개발 시: source venv/bin/activate
# 배포 시: 라즈베리파이에서 자동 생성됨
```

---

### 질문 2: cointicker 안에 requirements.txt가 필요한가?

**답변**: ❌ **필요 없음 (현재 구조에서는)**

**이유**:

1. 현재 배포 스크립트는 `requirements/requirements-master.txt`와 `requirements/requirements-worker.txt`를 사용
2. `cointicker/requirements.txt`는 배포 스크립트에서 사용되지 않음
3. 노드별로 다른 의존성이 필요함:
   - Master: `requirements-master.txt` (Scrapyd, NameNode 관련)
   - Worker: `requirements-worker.txt` (Scrapy, DataNode 관련)
   - Tier2: `requirements-tier2.txt` (Flask, DB 관련)

**현재 의존성 파일 구조**:

```
PICU/
├── requirements.txt              # ⚠️ 개발용? 목적 불명확
├── requirements/
│   ├── requirements-master.txt   # ✅ Master Node 배포용
│   ├── requirements-worker.txt   # ✅ Worker Node 배포용
│   └── requirements-tier2.txt    # ✅ Tier2 서버 배포용
└── cointicker/
    └── requirements.txt          # ⚠️ 사용되지 않음
```

**문제점**:

- `PICU/requirements.txt`와 `cointicker/requirements.txt`의 역할이 불명확
- 배포 스크립트는 `requirements/` 디렉토리만 사용
- 중복으로 인한 혼란

---

### 질문 3: 패키지 관리 툴 사용 시 올바른 방법론

**답변**: 배포 환경(라즈베리파이)과 개발 환경(Mac)을 명확히 분리하여 관리

**핵심 원칙**:
1. **개발 환경**: `PICU/requirements.txt` (전체 패키지 포함)
2. **배포 환경**: `requirements/master.txt`, `worker.txt`, `tier2.txt` (노드별 최소 패키지)
3. **레거시 호환**: `cointicker/requirements.txt` (심볼릭 링크로 유지)

---

## 🎯 올바른 의존성 관리 방법론

### 방법 1: 현재 구조 개선 (간단, 권장)

#### 구조:

```
PICU/
├── pyproject.toml              # 통합 패키지 정의
├── requirements/
│   ├── base.txt                # 공통 의존성
│   ├── dev.txt                 # 개발 전용 (pytest, black 등)
│   ├── master.txt              # Master Node 전용
│   ├── worker.txt              # Worker Node 전용
│   └── tier2.txt               # Tier2 Server 전용
└── cointicker/                 # 배포 대상 코드
```

#### pyproject.toml:

```toml
[project]
name = "picu-cointicker"
version = "1.0.0"
requires-python = ">=3.9"

# 공통 의존성 (모든 노드)
dependencies = [
    "pyyaml>=6.0.1",
    "python-dotenv>=1.0.0",
    "loguru>=0.7.2",
    "hdfs>=2.7.0",
    "kafka-python>=2.0.2",
]

[project.optional-dependencies]
# 개발 환경용
dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "black>=23.0.0",
    "flake8>=6.0.0",
    "pyqt5>=5.15.0",  # GUI
]

# Master Node용
master = [
    "scrapy>=2.11.0",
    "scrapyd>=1.3.0",
    "paramiko>=3.0.0",
    "schedule>=1.2.0",
]

# Worker Node용
worker = [
    "scrapy>=2.11.0",
    "beautifulsoup4>=4.12.0",
    "requests>=2.31.0",
    "python-dateutil>=2.8.2",
]

# Tier2 Server용
tier2 = [
    "flask>=3.0.0",
    "flask-cors>=4.0.0",
    "pymongo>=4.6.0",
    "pandas>=2.1.0",
    "numpy>=1.24.0",
]
```

#### requirements/ 디렉토리 (pip 호환):

```bash
# requirements/base.txt
pyyaml>=6.0.1
python-dotenv>=1.0.0
loguru>=0.7.2
hdfs>=2.7.0
kafka-python>=2.0.2

# requirements/master.txt
-r base.txt
scrapy>=2.11.0
scrapyd>=1.3.0
paramiko>=3.0.0
schedule>=1.2.0

# requirements/worker.txt
-r base.txt
scrapy>=2.11.0
beautifulsoup4>=4.12.0
requests>=2.31.0
python-dateutil>=2.8.2

# requirements/tier2.txt
-r base.txt
flask>=3.0.0
flask-cors>=4.0.0
pymongo>=4.6.0
pandas>=2.1.0
numpy>=1.24.0

# requirements/dev.txt
-r base.txt
pytest>=7.4.0
pytest-cov>=4.1.0
black>=23.0.0
flake8>=6.0.0
pyqt5>=5.15.0
```

#### 설치 방법:

```bash
# 개발 환경 (Mac)
pip install -e ".[dev]"
# 또는
pip install -r requirements/dev.txt

# Master Node 배포 (라즈베리파이)
pip install -r requirements/master.txt

# Worker Node 배포 (라즈베리파이)
pip install -r requirements/worker.txt

# Tier2 Server 배포
pip install -r requirements/tier2.txt
```

---

### 방법 2: Poetry 사용 (고급, 더 나은 의존성 관리)

#### pyproject.toml:

```toml
[tool.poetry]
name = "picu-cointicker"
version = "1.0.0"
description = "암호화폐 시장 동향 분석 및 실시간 대시보드 시스템"
authors = ["Your Name <you@example.com>"]

[tool.poetry.dependencies]
python = "^3.9"
# 공통 의존성
pyyaml = "^6.0.1"
python-dotenv = "^1.0.0"
loguru = "^0.7.2"
hdfs = "^2.7.0"
kafka-python = "^2.0.2"

# Optional dependencies (extras)
scrapy = {version = "^2.11.0", optional = true}
scrapyd = {version = "^1.3.0", optional = true}
paramiko = {version = "^3.0.0", optional = true}
schedule = {version = "^1.2.0", optional = true}
beautifulsoup4 = {version = "^4.12.0", optional = true}
requests = {version = "^2.31.0", optional = true}
flask = {version = "^3.0.0", optional = true}
flask-cors = {version = "^4.0.0", optional = true}
pymongo = {version = "^4.6.0", optional = true}

[tool.poetry.group.dev.dependencies]
pytest = "^7.4.0"
pytest-cov = "^4.1.0"
black = "^23.0.0"
flake8 = "^6.0.0"
pyqt5 = "^5.15.0"

[tool.poetry.extras]
master = ["scrapy", "scrapyd", "paramiko", "schedule"]
worker = ["scrapy", "beautifulsoup4", "requests"]
tier2 = ["flask", "flask-cors", "pymongo", "pandas", "numpy"]

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
```

#### 설치 방법:

```bash
# 개발 환경 (Mac)
poetry install --with dev

# Master Node 배포 (라즈베리파이)
poetry install --extras master

# Worker Node 배포 (라즈베리파이)
poetry install --extras worker

# Tier2 Server 배포
poetry install --extras tier2
```

#### 배포 시 requirements.txt 생성:

```bash
# Poetry에서 requirements.txt 생성
poetry export -f requirements.txt --without-hashes --output requirements/master.txt --extras master
poetry export -f requirements.txt --without-hashes --output requirements/worker.txt --extras worker
poetry export -f requirements.txt --without-hashes --output requirements/tier2.txt --extras tier2

# 배포 스크립트는 기존 그대로 사용 가능
```

---

### 방법 3: pip-tools + pyproject.toml (중간 수준, 권장)

#### pyproject.toml:

```toml
[project]
name = "picu-cointicker"
version = "1.0.0"

# 공통 의존성 (pin 안 함, 범위만 지정)
dependencies = [
    "pyyaml>=6.0.1",
    "python-dotenv>=1.0.0",
    "loguru>=0.7.2",
]

[project.optional-dependencies]
master = [
    "scrapy>=2.11.0",
    "scrapyd>=1.3.0",
]
worker = [
    "scrapy>=2.11.0",
    "beautifulsoup4>=4.12.0",
]
tier2 = [
    "flask>=3.0.0",
    "pymongo>=4.6.0",
]
dev = [
    "pytest>=7.4.0",
    "black>=23.0.0",
]
```

#### requirements.in 파일들:

```bash
# requirements/master.in
-e .[master]

# requirements/worker.in
-e .[worker]

# requirements/tier2.in
-e .[tier2]
```

#### 의존성 잠금 (개발 머신에서):

```bash
pip-compile requirements/master.in -o requirements/master.txt
pip-compile requirements/worker.in -o requirements/worker.txt
pip-compile requirements/tier2.in -o requirements/tier2.txt
```

#### 장점:

- 버전 잠금으로 재현 가능한 빌드
- 의존성 충돌 자동 해결
- 간단한 업데이트: `pip-compile --upgrade`

---

## 📋 최종 권장사항

### 1. 즉시 조치 (현재 구조 개선)

```bash
# 1. 불필요한 venv 삭제
rm -rf ./cointicker/venv
rm -rf ./scripts/venv

# 2. requirements/ 디렉토리 구조 개선
cd requirements/
mv requirements-master.txt master.txt
mv requirements-worker.txt worker.txt
mv requirements-tier2.txt tier2.txt

# 3. base.txt 생성 (공통 의존성)
cat > base.txt << 'EOF'
# 공통 의존성 (모든 노드)
pyyaml>=6.0.1
python-dotenv>=1.0.0
loguru>=0.7.2
hdfs>=2.7.0
kafka-python>=2.0.2
EOF

# 4. dev.txt 생성 (개발 환경 전용)
cat > dev.txt << 'EOF'
-r base.txt

# GUI 개발
pyqt5>=5.15.0

# 테스트
pytest>=7.4.0
pytest-cov>=4.1.0

# Scrapy (로컬 테스트용)
scrapy>=2.11.0
beautifulsoup4>=4.12.0
requests>=2.31.0
selenium>=4.0.0
webdriver-manager>=4.0.1

# 코드 품질
black>=23.0.0
flake8>=6.0.0

# Tier2 (로컬 테스트용)
flask>=3.0.0
flask-cors>=4.0.0
pymongo>=4.6.0
pandas>=2.1.0
numpy>=1.24.0

# 기타 개발 도구
ipython>=8.0.0
EOF

# 5. master.txt, worker.txt, tier2.txt에 base.txt 참조 추가
echo "-r base.txt" | cat - master.txt > temp && mv temp master.txt
echo "-r base.txt" | cat - worker.txt > temp && mv temp worker.txt
echo "-r base.txt" | cat - tier2.txt > temp && mv temp tier2.txt

# 6. PICU/requirements.txt 생성 (심볼릭 링크, 권장)
cd ..
ln -s requirements/dev.txt requirements.txt

# 7. cointicker/requirements.txt를 심볼릭 링크로 전환 (레거시 호환)
mv cointicker/requirements.txt cointicker/requirements.txt.bak
ln -s ../requirements.txt cointicker/requirements.txt
```

### 2. 배포 스크립트 수정

#### deployment/setup_master.sh:

```bash
# 변경 전
rsync -avz \
    "$PROJECT_ROOT/requirements/requirements-master.txt" \
    "$MASTER_USER@$MASTER_IP:$PROJECT_DIR/"

# 변경 후
rsync -avz \
    "$PROJECT_ROOT/requirements/master.txt" \
    "$MASTER_USER@$MASTER_IP:$PROJECT_DIR/"

# 설치 부분도 수정
pip install -r $PROJECT_DIR/master.txt
```

#### deployment/setup_worker.sh:

```bash
# 변경 전
rsync -avz \
    "$PROJECT_ROOT/requirements/requirements-worker.txt" \
    "$WORKER_USER@$WORKER_IP:$PROJECT_DIR/"

# 변경 후
rsync -avz \
    "$PROJECT_ROOT/requirements/worker.txt" \
    "$WORKER_USER@$WORKER_IP:$PROJECT_DIR/"

# 설치 부분도 수정
pip install -r $PROJECT_DIR/worker.txt
```

### 3. 장기적 개선 (pyproject.toml 도입)

```bash
# pyproject.toml 생성 (위의 방법 1 또는 방법 3 사용)
# 개발 환경에서:
pip install -e ".[dev]"

# 라즈베리파이 배포는 기존 requirements/*.txt 그대로 사용 가능
```

---

## 🎯 올바른 구조 (최종)

### 개발 환경 (Mac):
```
PICU/
├── requirements.txt -> requirements/dev.txt  # 심볼릭 링크 (개발 환경용)
├── pyproject.toml              # 프로젝트 메타데이터 + 의존성 정의 (선택)
├── venv/                       # 개발용 가상환경
├── requirements/
│   ├── base.txt                # 공통 의존성
│   ├── dev.txt                 # 개발 환경 전용 (GUI + 테스트)
│   ├── master.txt              # Master Node 배포용
│   ├── worker.txt              # Worker Node 배포용
│   └── tier2.txt               # Tier2 배포용
├── cointicker/                 # 배포 대상 코드
│   ├── requirements.txt -> ../requirements.txt  # 심볼릭 링크 (레거시 호환)
│   ├── master-node/
│   ├── worker-nodes/
│   ├── shared/
│   └── config/
├── deployment/                 # 배포 스크립트
├── scripts/                    # 개발 환경 실행 스크립트
└── PICU_docs/                  # 문서
```

### 라즈베리파이 (배포 후):
```
/home/ubuntu/cointicker/
├── venv/                       # SSH로 생성됨 (라즈베리파이에서 직접)
├── master.txt 또는 worker.txt  # rsync로 전송됨 (requirements/에서)
├── master-node/ 또는 worker-nodes/
├── shared/
└── config/
```

### 핵심 차이점:
- **개발 환경**: `requirements.txt` (= `dev.txt`, 전체 패키지)
- **배포 환경**: `master.txt`, `worker.txt` (노드별 최소 패키지)
- **venv**: 각 환경에서 독립적으로 생성 (아키텍처 차이)

---

## 💡 핵심 원칙

1. **개발 머신의 venv는 배포하지 않음**

   - Mac과 라즈베리파이의 아키텍처가 다름 (x86_64 vs ARM64)
   - 라즈베리파이에서 직접 생성해야 함

2. **requirements.txt는 배포 대상별로 분리**

   - `requirements/master.txt` - Master Node
   - `requirements/worker.txt` - Worker Node
   - `requirements/tier2.txt` - Tier2 Server
   - `requirements/dev.txt` - 개발 환경

3. **cointicker/ 디렉토리는 "순수 코드"만**

   - venv, requirements.txt 제외
   - 배포 대상 코드만 포함
   - 배포 스크립트가 rsync로 전송

4. **pyproject.toml은 "소스 오브 트루스"**
   - 모든 의존성을 여기서 정의
   - requirements/\*.txt는 pyproject.toml에서 생성 가능

---

**작성자**: Juns Claude Code
**마지막 업데이트**: 2025-12-02
