# venv 및 temp 디렉토리 아키텍처 분석

**분석 일시**: 2025-12-03
**목적**: venv와 data/temp 디렉토리의 실제 용도 및 배포 전략 명확화

---

## 🎯 핵심 결론

### ✅ **venv 통합은 불필요 - 각 환경별로 독립적으로 필요**

### ✅ **data/temp는 상대 경로 사용 - 통합 불필요, 개발 임시 데이터만 정리**

---

## 📦 1. venv 아키텍처 분석

### 현재 구조의 의미

```
PICU/
├── venv/                           # 로컬 개발 환경 (Mac)
├── cointicker/venv/                # 로컬 개발 환경 (Mac) - 중복?
└── requirements/
    ├── dev.txt                     # Mac 개발 환경
    ├── master.txt                  # 라즈베리파이 Master Node
    ├── worker.txt                  # 라즈베리파이 Worker Nodes
    └── tier2.txt                   # 외부 Tier2 서버
```

### 실제 배포 시나리오

#### **개발 환경 (현재 - Mac)**

```bash
# 로컬 Mac에서 개발
cd PICU
python3 -m venv venv
source venv/bin/activate
pip install -r requirements/dev.txt

# 모든 컴포넌트 로컬 테스트
# - GUI 실행
# - Backend API 테스트
# - Scrapy Spider 테스트
# - Frontend 개발
```

#### **배포 환경 1: 라즈베리파이 Master Node**

```bash
# Raspberry Pi OS (Debian ARM)
ssh ubuntu@raspberry-master

cd /opt/PICU
python3 -m venv venv                    # ← 라즈베리파이에서 생성!
source venv/bin/activate
pip install -r requirements/master.txt  # ← Master 전용 의존성

# Master 역할:
# - HDFS NameNode
# - YARN ResourceManager
# - Kafka Broker (optional)
```

#### **배포 환경 2: 라즈베리파이 Worker Nodes**

```bash
# 각 Worker 노드에서
ssh ubuntu@raspberry-worker1

cd /opt/PICU
python3 -m venv venv                    # ← Worker에서 생성!
source venv/bin/activate
pip install -r requirements/worker.txt  # ← Worker 전용 의존성

# Worker 역할:
# - HDFS DataNode
# - YARN NodeManager
# - Scrapy Spiders 실행
```

#### **배포 환경 3: Tier2 서버 (외부)**

```bash
# AWS/GCP/Azure 서버
ssh user@tier2-server

cd /var/www/PICU
python3 -m venv venv                    # ← Tier2 서버에서 생성!
source venv/bin/activate
pip install -r requirements/tier2.txt   # ← Backend API 전용 의존성

# Tier2 역할:
# - FastAPI Backend
# - MariaDB 연결
# - REST API 제공
```

### 왜 각각 독립적인 venv가 필요한가?

| 환경                    | OS/아키텍처           | Python 패키지                | 이유                      |
| ----------------------- | --------------------- | ---------------------------- | ------------------------- |
| **로컬 Mac**            | macOS (x86_64/ARM64)  | PyQt5, Scrapy, FastAPI, 전체 | GUI + 전체 테스트 필요    |
| **라즈베리파이 Master** | Raspberry Pi OS (ARM) | HDFS, YARN, 최소 패키지      | 경량화 필요 (메모리 제한) |
| **라즈베리파이 Worker** | Raspberry Pi OS (ARM) | Scrapy, HDFS, 최소 패키지    | 크롤링 + 저장만           |
| **Tier2 서버**          | Ubuntu (x86_64)       | FastAPI, SQLAlchemy, 최소    | API 서버만                |

### 🚫 **venv 통합하면 안 되는 이유**

1. **플랫폼 차이**

   ```bash
   # Mac에서 설치한 패키지를 라즈베리파이에서 사용 불가!
   # 바이너리 호환성 문제

   # Mac venv:
   numpy-1.24.0-cp311-cp311-macosx_11_0_arm64.whl

   # 라즈베리파이에서 필요:
   numpy-1.24.0-cp311-cp311-linux_armv7l.whl
   ```

2. **의존성 차이**

   ```python
   # dev.txt (로컬 개발)
   PyQt5>=5.15.0          # GUI 개발
   jupyter>=1.0.0         # 데이터 분석
   transformers>=4.35.0   # NLP (용량 큼)
   torch>=2.1.0           # AI (용량 매우 큼)

   # master.txt (라즈베리파이 Master)
   pyyaml>=6.0.1          # 설정만
   hdfs>=2.7.0            # HDFS만
   # PyQt5 없음! (GUI 불필요)
   # torch 없음! (메모리 부족)
   ```

3. **리소스 제약**

   ```
   로컬 Mac: RAM 16GB+, 디스크 500GB+
   라즈베리파이: RAM 4GB, 디스크 32GB SD 카드

   → 라즈베리파이에 dev.txt 전체 설치 불가능!
   ```

### ✅ **올바른 접근**

```bash
# 개발 완료 후 배포 시
cd PICU

# 1. 로컬 venv 삭제 (선택)
rm -rf venv
rm -rf cointicker/venv

# 2. 각 환경에 배포하면서 각각 생성
# Master:
scp -r requirements/ ubuntu@raspberry-master:/opt/PICU/
ssh ubuntu@raspberry-master "cd /opt/PICU && python3 -m venv venv && source venv/bin/activate && pip install -r requirements/master.txt"

# Worker:
scp -r requirements/ ubuntu@raspberry-worker1:/opt/PICU/
ssh ubuntu@raspberry-worker1 "cd /opt/PICU && python3 -m venv venv && source venv/bin/activate && pip install -r requirements/worker.txt"

# Tier2:
scp -r requirements/ user@tier2-server:/var/www/PICU/
ssh user@tier2-server "cd /var/www/PICU && python3 -m venv venv && source venv/bin/activate && pip install -r requirements/tier2.txt"
```

---

## 📁 2. data/temp 디렉토리 분석

### 현재 구조

```
PICU/cointicker/
├── data/temp/                              # 최근 데이터 (20251201)
│   └── 20251201/
├── worker-nodes/
│   ├── data/temp/                          # 가장 오래된 데이터 (20251128)
│   │   └── 20251128/
│   └── cointicker/
│       └── data/temp/                      # 많은 데이터 (20251129, 20251202, 20251203)
│           ├── 20251129/
│           ├── 20251202/
│           └── 20251203/
```

### 코드 분석 결과

#### **상대 경로 사용 (✅ 정상)**

```python
# cointicker/worker-nodes/cointicker/pipelines.py:348
date_path = get_date_path("data/temp", datetime.now())

# cointicker/worker-nodes/kafka/kafka_consumer.py:186
date_path = get_date_path("data/temp", datetime.now())

# cointicker/worker-nodes/cointicker/pipelines/__init__.py:136
date_path = get_date_path('data/temp', datetime.now())

# shared/utils.py:104-119
def get_date_path(base_path: str, date: Optional[datetime] = None) -> Path:
    if date is None:
        date = datetime.now()
    date_str = date.strftime("%Y%m%d")
    return Path(base_path) / date_str  # ← 상대 경로!
```

#### **실행 위치에 따른 경로**

```bash
# Scrapy 실행 위치: cointicker/worker-nodes/
cd worker-nodes
scrapy crawl upbit_trends
# → 저장 경로: worker-nodes/data/temp/YYYYMMDD/

# Pipeline 실행 위치: cointicker/worker-nodes/cointicker/
cd worker-nodes/cointicker
python -m scrapy crawl upbit_trends
# → 저장 경로: worker-nodes/cointicker/data/temp/YYYYMMDD/

# Backend 실행 위치: cointicker/backend/
cd backend
python services/data_loader.py
# → 읽기 경로: backend/data/temp/YYYYMMDD/
```

### 🔍 **실제 상황 분석**

1. **여러 위치의 temp는 개발 과정에서 생성된 임시 데이터**

   - 다양한 위치에서 테스트하면서 각각 생성됨
   - 하드코딩 아님 ✅
   - 상대 경로 사용 중 ✅

2. **프로덕션 환경에서는 각 노드마다 독립적**

   ```
   Master Node:
   /opt/PICU/data/temp/         # Master에서 수집한 데이터

   Worker Node 1:
   /opt/PICU/data/temp/         # Worker1에서 수집한 데이터

   Worker Node 2:
   /opt/PICU/data/temp/         # Worker2에서 수집한 데이터

   → 각 노드에서 수집 후 HDFS로 전송
   → temp는 임시 버퍼 역할
   ```

### ✅ **해야 할 일**

#### **개발 환경 정리 (선택)**

```bash
# 오래된 테스트 데이터 삭제
cd PICU/cointicker

# 최근 1주일 이전 데이터 삭제
find . -type d -path "*/data/temp/202*" ! -path "*/venv/*" -mtime +7 -exec rm -rf {} \;

# 또는 전체 삭제 (다시 생성됨)
rm -rf ./data/temp/*
rm -rf ./worker-nodes/data/temp/*
rm -rf ./worker-nodes/cointicker/data/temp/*
```

#### **프로덕션 배포 시**

```bash
# 각 노드에서 독립적으로 data/temp 사용
# 통합 불필요!

# Worker Node에서:
cd /opt/PICU/worker-nodes
scrapy crawl upbit_trends
# → data/temp/YYYYMMDD/ 생성
# → Kafka로 전송
# → HDFS로 백업
# → data/temp 정리 (cron job)
```

---

## 📝 최종 결론 및 권장사항

### ✅ **venv 관련**

| 항목           | 결론                    | 이유                        |
| -------------- | ----------------------- | --------------------------- |
| 로컬 venv 통합 | **불필요**              | 개발 완료 후 삭제할 것      |
| 배포 시 venv   | **각 노드별 독립 생성** | OS/아키텍처/요구사항이 다름 |
| 현재 여러 venv | **정상**                | 테스트 중이므로 유지        |

**권장 액션**:

```bash
# 지금: 아무것도 하지 말기 (정상 상태)

# 개발 완료 후:
rm -rf PICU/venv
rm -rf PICU/cointicker/venv
rm -rf PICU/scripts/venv

# 배포 시: 각 노드에서 독립 생성
```

---

### ✅ **data/temp 관련**

| 항목               | 결론                 | 이유                              |
| ------------------ | -------------------- | --------------------------------- |
| 경로 하드코딩 여부 | **없음 (상대 경로)** | `Path(base_path) / date_str` 사용 |
| 여러 위치의 temp   | **개발 임시 데이터** | 다양한 위치에서 테스트한 흔적     |
| 통합 필요성        | **불필요**           | 프로덕션에서는 각 노드별 독립     |

**권장 액션**:

```bash
# 선택 1: 오래된 데이터만 삭제
find ./cointicker -type d -path "*/data/temp/202*" ! -path "*/venv/*" -mtime +7 -exec rm -rf {} \;

# 선택 2: 전체 삭제 (다시 생성됨)
rm -rf ./cointicker/data/temp/*
rm -rf ./cointicker/worker-nodes/data/temp/*
rm -rf ./cointicker/worker-nodes/cointicker/data/temp/*

# .gitignore에 추가
echo "data/temp/" >> .gitignore
```

---

## 🎯 EXECUTION_PLAN.md 수정 필요

### Phase 2.3, 2.4는 **삭제 또는 수정** 필요

**현재 (잘못된 권장사항)**:

```
Phase 2.3: venv 통합 (선택, 신중히)
Phase 2.4: data/temp/ 통합 (선택, 신중히)
```

**수정 후 (올바른 권장사항)**:

```
Phase 2.3: 개발 환경 venv 정리 (배포 전)
  - 로컬 venv 삭제 (배포 시 각 노드에서 재생성)
  - 배포 스크립트에서 자동으로 각 노드별 venv 생성

Phase 2.4: data/temp 개발 데이터 정리 (선택)
  - 오래된 테스트 데이터 삭제
  - .gitignore에 data/temp/ 추가
  - 통합 불필요 (각 노드별 독립 사용)
```

---

## 📊 배포 아키텍처 요약

```
┌─────────────────────────────────────────────────────────────┐
│                    개발 환경 (Mac)                           │
│  venv/ + requirements/dev.txt                               │
│  - 전체 컴포넌트 테스트                                      │
│  - GUI, Backend, Frontend, Scrapy 전부                      │
│  ↓ 개발 완료 후 배포                                         │
└─────────────────────────────────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        ▼                    ▼                    ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ Master Node  │    │ Worker Nodes │    │ Tier2 Server │
│              │    │              │    │              │
│ Raspberry Pi │    │ Raspberry Pi │    │ AWS/GCP/Azure│
│ venv/        │    │ venv/        │    │ venv/        │
│ master.txt   │    │ worker.txt   │    │ tier2.txt    │
│              │    │              │    │              │
│ - HDFS NN    │    │ - HDFS DN    │    │ - FastAPI    │
│ - YARN RM    │    │ - Scrapy     │    │ - MariaDB    │
│ - Kafka      │    │ - Kafka      │    │ - REST API   │
│              │    │              │    │              │
│ data/temp/   │    │ data/temp/   │    │ data/temp/   │
│ (독립)       │    │ (독립)       │    │ (독립)       │
└──────────────┘    └──────────────┘    └──────────────┘
```

---

**작성일**: 2025-12-03
**작성자**: Juns Claude Code
**다음 액션**: EXECUTION_PLAN.md의 Phase 2.3, 2.4 수정 필요
