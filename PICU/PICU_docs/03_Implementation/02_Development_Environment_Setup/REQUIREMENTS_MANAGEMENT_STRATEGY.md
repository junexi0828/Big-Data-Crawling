# Requirements.txt 관리 전략 - 완전 분석

**작성 일시**: 2025-12-02
**분석 범위**: 모든 스크립트 및 GUI 코드 포함
**목적**: 배포와 개발 환경 모두를 고려한 올바른 requirements.txt 관리 전략

---

## 🔍 현재 상황 완전 분석

### 1. 존재하는 Requirements 파일들

```
PICU/
├── requirements.txt              # ❌ 존재하지 않음!
├── requirements/
│   ├── requirements-master.txt   # ✅ Master Node 배포용
│   ├── requirements-worker.txt   # ✅ Worker Node 배포용
│   └── requirements-tier2.txt    # ✅ Tier2 Server 배포용
└── cointicker/
    └── requirements.txt          # ✅ 존재함 (52줄)
```

### 2. Requirements.txt를 참조하는 모든 코드

#### 2.1 GUI Installer (installer.py)
**파일**: `cointicker/gui/installer/installer.py`
**라인**: 50-59

```python
# requirements.txt 찾기 (PICU 루트 우선, 없으면 cointicker)
picu_requirements = self.project_root / "requirements.txt"
cointicker_requirements = self.project_root / "cointicker" / "requirements.txt"

if picu_requirements.exists():
    self.requirements_file = picu_requirements
elif cointicker_requirements.exists():
    self.requirements_file = cointicker_requirements
else:
    self.requirements_file = Path("requirements.txt")  # 현재 디렉토리
```

**현재 동작**:
- `PICU/requirements.txt` 없음 → 건너뜀
- `cointicker/requirements.txt` 있음 → ✅ **이것 사용**
- 둘 다 없으면 현재 디렉토리에서 찾음

---

#### 2.2 GUI Install Script (install.sh)
**파일**: `cointicker/gui/scripts/install.sh`
**라인**: 55-57

```bash
REQUIREMENTS_FILE="$PROJECT_ROOT/requirements.txt"
if [ -f "$REQUIREMENTS_FILE" ]; then
    pip install -r "$REQUIREMENTS_FILE"
```

**PROJECT_ROOT**: `gui/scripts/install.sh` → `../../..` → **PICU/**

**현재 동작**:
- `PICU/requirements.txt` 찾으려 함
- **❌ 파일 없음 → 오류 발생**

---

#### 2.3 Start Script (start.sh)
**파일**: `scripts/start.sh`
**라인**: 55

```bash
pip install -r "$PROJECT_ROOT/requirements.txt"
```

**PROJECT_ROOT**: `scripts/` → `..` → **PICU/**

**현재 동작**:
- `PICU/requirements.txt` 찾으려 함
- **❌ 파일 없음 → 오류 발생**

---

#### 2.4 Test Script (run_all_tests.sh)
**파일**: `cointicker/tests/run_all_tests.sh`
**라인**: 324-332

```bash
# PICU 루트의 requirements.txt 우선 사용, 없으면 cointicker의 requirements.txt 사용
REQUIREMENTS_FILE="$PICU_ROOT/requirements.txt"
if [ ! -f "$REQUIREMENTS_FILE" ]; then
    REQUIREMENTS_FILE="$PROJECT_ROOT/requirements.txt"
    if [ ! -f "$REQUIREMENTS_FILE" ]; then
        log_error "requirements.txt 파일을 찾을 수 없습니다"
        exit 1
    fi
fi
log_info "requirements.txt 사용: $REQUIREMENTS_FILE"
pip install -r "$REQUIREMENTS_FILE"
```

**현재 동작**:
- `PICU/requirements.txt` 없음 → 건너뜀
- `cointicker/requirements.txt` 있음 → ✅ **이것 사용**

---

#### 2.5 Integration Test Script (run_integration_tests.sh)
**파일**: `cointicker/tests/run_integration_tests.sh`
**라인**: 79-81

```bash
# PICU 루트의 requirements.txt 사용
REQUIREMENTS_FILE="$PROJECT_ROOT/../requirements.txt"
if [ ! -f "$REQUIREMENTS_FILE" ]; then
    echo -e "${RED}❌ requirements.txt 파일을 찾을 수 없습니다: $REQUIREMENTS_FILE${NC}"
    exit 1
fi
```

**현재 동작**:
- `PICU/requirements.txt` 찾으려 함
- **❌ 파일 없음 → 오류 발생**

---

#### 2.6 Test User Flow Script (test_user_flow.sh)
**파일**: `scripts/test_user_flow.sh`
**라인**: 42

```bash
pip install -q -r "$PROJECT_ROOT/requirements.txt"
```

**현재 동작**:
- `PICU/requirements.txt` 찾으려 함
- **❌ 파일 없음 → 오류 발생**

---

### 3. 배포 스크립트 (라즈베리파이용)

#### 3.1 setup_master.sh
```bash
rsync -avz \
    "$PROJECT_ROOT/requirements/requirements-master.txt" \
    "$MASTER_USER@$MASTER_IP:$PROJECT_DIR/"

pip install -r $PROJECT_DIR/requirements-master.txt
```

**✅ 정상 작동**: `requirements/` 디렉토리 사용

#### 3.2 setup_worker.sh
```bash
rsync -avz \
    "$PROJECT_ROOT/requirements/requirements-worker.txt" \
    "$WORKER_USER@$WORKER_IP:$PROJECT_DIR/"

pip install -r $PROJECT_DIR/requirements-worker.txt
```

**✅ 정상 작동**: `requirements/` 디렉토리 사용

---

## 🎯 문제점 요약

### 현재 문제:

1. **`PICU/requirements.txt` 없음**
   - 4개 스크립트가 이 파일을 찾음
   - 오류 발생 또는 fallback으로 `cointicker/requirements.txt` 사용

2. **역할 불명확**
   - 개발용 requirements.txt가 어디에 있어야 하는지 불명확
   - GUI는 `cointicker/requirements.txt` 사용
   - 다른 스크립트는 `PICU/requirements.txt` 기대

3. **배포와 개발 분리 부족**
   - 배포용: `requirements/requirements-*.txt` (노드별 분리)
   - 개발용: `PICU/requirements.txt` 또는 `cointicker/requirements.txt`?

---

## ✅ 올바른 해결 방안

### 방안 1: PICU/requirements.txt 생성 (권장)

**구조**:
```
PICU/
├── requirements.txt              # ✅ 개발 환경용 (전체 통합)
├── requirements/
│   ├── base.txt                  # 공통 의존성
│   ├── dev.txt                   # 개발 전용 (GUI, 테스트 등)
│   ├── master.txt                # Master 배포용
│   ├── worker.txt                # Worker 배포용
│   └── tier2.txt                 # Tier2 배포용
└── cointicker/
    └── requirements.txt          # ❌ 삭제 (중복)
```

**장점**:
- 모든 스크립트가 정상 작동
- GUI Installer가 `PICU/requirements.txt` 우선 사용
- 개발 환경과 배포 환경 명확히 분리

**단점**:
- `cointicker/requirements.txt` 삭제 필요 (GUI Installer fallback 제거)

---

### 방안 2: 스크립트 수정 (비권장)

모든 스크립트를 `cointicker/requirements.txt` 또는 `requirements/dev.txt`를 사용하도록 수정

**장점**:
- requirements.txt 파일 수 최소화

**단점**:
- 6개 스크립트 수정 필요
- 기존 레거시 코드 변경
- 유지보수 어려움

---

## 🎯 최종 권장 전략

### 전략: PICU/requirements.txt 생성 + cointicker/requirements.txt 유지

**이유**:
1. **레거시 유지**: GUI Installer가 fallback으로 `cointicker/requirements.txt` 사용 가능
2. **호환성**: 모든 기존 스크립트 정상 작동
3. **명확성**: 개발용(`PICU/requirements.txt`)과 배포용(`requirements/`) 분리

**구조**:
```
PICU/
├── requirements.txt              # 개발 환경용 (전체 통합) - 생성
├── requirements/
│   ├── base.txt                  # 공통 의존성
│   ├── dev.txt                   # 개발 전용 (pyqt5, pytest 등)
│   ├── master.txt                # Master 배포용 (기존)
│   ├── worker.txt                # Worker 배포용 (기존)
│   └── tier2.txt                 # Tier2 배포용 (기존)
└── cointicker/
    └── requirements.txt          # 레거시 호환용 (유지, 심볼릭 링크 가능)
```

---

## 📋 구현 단계

### 1단계: requirements/ 디렉토리 개선

#### 1.1 base.txt 생성 (공통 의존성)
```bash
cat > requirements/base.txt << 'EOF'
# 공통 의존성 (모든 노드)
pyyaml>=6.0.1
python-dotenv>=1.0.0
loguru>=0.7.2
hdfs>=2.7.0
kafka-python>=2.0.2
EOF
```

#### 1.2 dev.txt 생성 (개발 환경)
```bash
cat > requirements/dev.txt << 'EOF'
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

# 코드 품질
black>=23.0.0
flake8>=6.0.0

# Tier2 (로컬 테스트용)
flask>=3.0.0
flask-cors>=4.0.0
pymongo>=4.6.0

# 기타 개발 도구
ipython>=8.0.0
jupyter>=1.0.0
EOF
```

#### 1.3 master.txt 개선
```bash
cat > requirements/master.txt << 'EOF'
-r base.txt

# Master Node 전용
scrapy>=2.11.0
scrapyd>=1.3.0
paramiko>=3.0.0
schedule>=1.2.0
EOF
```

#### 1.4 worker.txt 개선
```bash
cat > requirements/worker.txt << 'EOF'
-r base.txt

# Worker Node 전용
scrapy>=2.11.0
beautifulsoup4>=4.12.0
requests>=2.31.0
python-dateutil>=2.8.2
selenium>=4.0.0
webdriver-manager>=4.0.1
EOF
```

#### 1.5 tier2.txt 개선
```bash
cat > requirements/tier2.txt << 'EOF'
-r base.txt

# Tier2 Server 전용
flask>=3.0.0
flask-cors>=4.0.0
pymongo>=4.6.0
pandas>=2.1.0
numpy>=1.24.0
pyarrow>=14.0.0
EOF
```

---

### 2단계: PICU/requirements.txt 생성

```bash
# 옵션 1: dev.txt로 심볼릭 링크 (권장)
ln -s requirements/dev.txt requirements.txt

# 옵션 2: dev.txt 복사
cp requirements/dev.txt requirements.txt

# 옵션 3: 직접 생성
cat > requirements.txt << 'EOF'
-r requirements/dev.txt
EOF
```

**권장**: 옵션 1 (심볼릭 링크)
- 중복 방지
- requirements/dev.txt 수정 시 자동 반영

---

### 3단계: cointicker/requirements.txt 처리

#### 옵션 A: 심볼릭 링크로 전환 (권장)
```bash
# 백업
mv cointicker/requirements.txt cointicker/requirements.txt.bak

# 심볼릭 링크 생성
ln -s ../requirements.txt cointicker/requirements.txt

# 또는
ln -s ../requirements/dev.txt cointicker/requirements.txt
```

#### 옵션 B: 유지 (레거시 호환)
```bash
# 현재 그대로 유지
# GUI Installer가 fallback으로 사용 가능
```

**권장**: 옵션 A (심볼릭 링크)
- 중복 제거
- 일관성 유지

---

### 4단계: 배포 스크립트 파일명 변경

```bash
cd requirements/
mv requirements-master.txt master.txt
mv requirements-worker.txt worker.txt
mv requirements-tier2.txt tier2.txt
```

**deployment/setup_master.sh 수정**:
```bash
# 변경 전
rsync -avz \
    "$PROJECT_ROOT/requirements/requirements-master.txt" \
    "$MASTER_USER@$MASTER_IP:$PROJECT_DIR/"
pip install -r $PROJECT_DIR/requirements-master.txt

# 변경 후
rsync -avz \
    "$PROJECT_ROOT/requirements/master.txt" \
    "$MASTER_USER@$MASTER_IP:$PROJECT_DIR/"
pip install -r $PROJECT_DIR/master.txt
```

**deployment/setup_worker.sh 수정**:
```bash
# 변경 전
rsync -avz \
    "$PROJECT_ROOT/requirements/requirements-worker.txt" \
    "$WORKER_USER@$WORKER_IP:$PROJECT_DIR/"
pip install -r $PROJECT_DIR/requirements-worker.txt

# 변경 후
rsync -avz \
    "$PROJECT_ROOT/requirements/worker.txt" \
    "$WORKER_USER@$WORKER_IP:$PROJECT_DIR/"
pip install -r $PROJECT_DIR/worker.txt
```

---

## 🧪 테스트 및 검증

### 1. GUI Installer 테스트
```bash
# PICU/requirements.txt 우선 사용 확인
python cointicker/gui/installer/installer_cli.py
```

### 2. Start Script 테스트
```bash
# PICU/requirements.txt 사용 확인
bash scripts/start.sh
```

### 3. Test Script 테스트
```bash
# PICU/requirements.txt 우선 사용 확인
bash cointicker/tests/run_all_tests.sh
```

### 4. 배포 스크립트 테스트
```bash
# 파일명 변경 확인
bash deployment/setup_master.sh
bash deployment/setup_worker.sh
```

---

## 📊 최종 구조 (권장)

```
PICU/
├── requirements.txt -> requirements/dev.txt  # 심볼릭 링크
├── requirements/
│   ├── base.txt              # 공통 의존성
│   ├── dev.txt               # 개발 환경 (GUI + 테스트)
│   ├── master.txt            # Master Node 배포용
│   ├── worker.txt            # Worker Node 배포용
│   └── tier2.txt             # Tier2 Server 배포용
└── cointicker/
    └── requirements.txt -> ../requirements.txt  # 심볼릭 링크 (레거시 호환)
```

---

## 🎯 사용 시나리오별 가이드

### 시나리오 1: 개발 환경 설정 (Mac)
```bash
cd PICU
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt  # = requirements/dev.txt
```

### 시나리오 2: Master Node 배포 (라즈베리파이)
```bash
# 개발 머신에서
bash deployment/setup_master.sh

# 라즈베리파이에서 자동 실행
cd /home/ubuntu/cointicker
python3 -m venv venv
source venv/bin/activate
pip install -r master.txt  # requirements/master.txt에서 전송됨
```

### 시나리오 3: Worker Node 배포 (라즈베리파이)
```bash
# 개발 머신에서
bash deployment/setup_worker.sh worker1 192.168.0.101

# 라즈베리파이에서 자동 실행
cd /home/ubuntu/cointicker
python3 -m venv venv
source venv/bin/activate
pip install -r worker.txt  # requirements/worker.txt에서 전송됨
```

### 시나리오 4: Tier2 Server 배포
```bash
cd /path/to/tier2-server
python3 -m venv venv
source venv/bin/activate
pip install -r requirements/tier2.txt
```

### 시나리오 5: GUI만 실행 (빠른 테스트)
```bash
cd PICU
python cointicker/gui/main.py
# requirements.txt 자동 감지 및 설치
```

---

## 🔑 핵심 원칙

1. **개발 환경**: `PICU/requirements.txt` (= `requirements/dev.txt`)
2. **배포 환경**: `requirements/master.txt`, `worker.txt`, `tier2.txt`
3. **레거시 호환**: `cointicker/requirements.txt` (심볼릭 링크 유지)
4. **중복 제거**: 심볼릭 링크 활용
5. **명확한 분리**: 개발과 배포 의존성 명확히 구분

---

## ⚠️ 주의사항

1. **venv는 배포하지 않음**
   - Mac과 라즈베리파이의 아키텍처가 다름
   - 각 환경에서 직접 생성

2. **requirements.txt는 환경별로 다름**
   - 개발: `dev.txt` (전체 패키지)
   - Master: `master.txt` (Scrapyd 관련)
   - Worker: `worker.txt` (Scrapy 관련)
   - Tier2: `tier2.txt` (Flask, DB 관련)

3. **base.txt는 모든 환경에서 필요**
   - HDFS, Kafka, Logger 등 공통 패키지
   - 각 requirements 파일에서 `-r base.txt`로 참조

---

**작성자**: Claude Code
**마지막 업데이트**: 2025-12-02
**검토 필요**: 배포 스크립트 수정 후 라즈베리파이 테스트
