# PICU 프로젝트 통합 가이드

**최종 업데이트**: 2025-12-08

PICU (Personal Investment & Cryptocurrency Understanding) 프로젝트의 통합 아키텍처 및 구성 요소를 설명합니다.

## 📋 프로젝트 개요

PICU 프로젝트는 암호화폐 데이터 수집, 분석, 시각화를 위한 통합 플랫폼입니다.

### 주요 구성 요소

1. **CoinTicker**: 암호화폐 티커 데이터 수집 및 대시보드
2. **GUI 통합 관리 시스템**: 모든 모듈을 통합 관리하는 엔터프라이즈급 GUI
3. **2-Tier 아키텍처**: 라즈베리파이 클러스터 (Tier 1) + 외부 서버 (Tier 2)

## 🔗 통합 아키텍처

### 전체 시스템 아키텍처

```
┌─────────────────────────────────────────────────────────┐
│                    PICU 통합 파이프라인                    │
└─────────────────────────────────────────────────────────┘

[Tier 1: 라즈베리파이 클러스터]
    │
    ├─ 데이터 수집 계층
    │   ├─ Scrapy → 암호화폐 뉴스, 시장 데이터 크롤링
    │   ├─ Selenium → 동적 콘텐츠 (TradingView, Upbit 등)
    │   └─ Scrapyd → 크롤링 작업 스케줄링 및 관리
    │
    ├─ 분산 저장 계층
    │   └─ HDFS → 대용량 데이터 저장
    │       ├─ /raw/crypto/news/
    │       ├─ /raw/crypto/ticker/
    │       └─ /raw/crypto/market/
    │
    ├─ 분산 처리 계층
    │   └─ MapReduce → 데이터 정제 및 집계
    │       ├─ 중복 제거
    │       ├─ 시간대별 집계
    │       └─ 형식 통일
    │
    └─ 오케스트레이션 계층
        ├─ Orchestrator → 전체 파이프라인 관리
        └─ Scrapyd Scheduler → 크롤링 작업 스케줄링
    │
    ▼ [Tier 1 → Tier 2 전송]
    │ SSH 또는 HDFS 클라이언트
    │
[Tier 2: 외부 서버]
    │
    ├─ 데이터 적재 계층
    │   └─ DataLoader → HDFS → PostgreSQL 적재
    │
    ├─ 데이터베이스 계층
    │   └─ PostgreSQL → 정제된 데이터 저장
    │       ├─ raw_news
    │       ├─ market_trends
    │       ├─ fear_greed_index
    │       ├─ sentiment_analysis
    │       ├─ technical_indicators
    │       └─ crypto_insights
    │
    ├─ API 계층
    │   └─ FastAPI → RESTful API 제공
    │
    ├─ 프론트엔드 계층
    │   └─ React → 실시간 대시보드
    │
    └─ 통합 관리 계층
        └─ GUI 애플리케이션 → 모든 모듈 통합 관리
```

## 🏗️ 컴포넌트 상세

### 1. 데이터 수집 계층 (Tier 1)

#### Scrapy Spiders

**위치**: `cointicker/worker-nodes/cointicker/spiders/`

**구현된 Spider**:

- `upbit_trends`: 업비트 시장 트렌드
- `saveticker`: 세이브티커 뉴스
- `coinness`: 코인니스 뉴스
- `perplexity`: Perplexity Finance 뉴스
- `cnn_fear_greed`: CNN 공포·탐욕 지수

**실행 방법**:

```bash
cd cointicker/worker-nodes/cointicker
scrapy crawl upbit_trends
```

#### Scrapyd 통합

**위치**: `cointicker/master-node/scheduler.py`

**주요 기능**:

- Scrapyd 서버 자동 시작 및 관리
- 프로젝트 자동 배포
- Spider 스케줄링 (spider_config.yaml 기반)

**설정 파일**: `cointicker/config/spider_config.yaml`

```yaml
spiders:
  upbit_trends:
    enabled: true
    schedule: "*/5 * * * *" # 5분마다
  saveticker:
    enabled: true
    schedule: "*/5 * * * *" # 5분마다
  coinness:
    enabled: true
    schedule: "*/10 * * * *" # 10분마다
  perplexity:
    enabled: true
    schedule: "0 * * * *" # 1시간마다
  cnn_fear_greed:
    enabled: true
    schedule: "0 0 * * *" # 매일 자정
```

### 2. 분산 저장 계층 (Tier 1)

#### HDFS 통합

**위치**: `cointicker/shared/hdfs_client.py`

**주요 기능**:

- HDFS 클라이언트 구현
- 파일 업로드/다운로드
- 디렉토리 관리

**사용 예시**:

```python
from shared.hdfs_client import HDFSClient

client = HDFSClient()
client.upload_file(local_path, hdfs_path)
data = client.download_file(hdfs_path)
```

**HDFS 경로 구조**:

```
/raw/
  ├── upbit/
  │   └── 20251208/
  │       └── *.json
  ├── saveticker/
  │   └── 20251208/
  │       └── *.json
  └── ...

/cleaned/
  └── 20251208/
      └── aggregated_*.json
```

### 3. 분산 처리 계층 (Tier 1)

#### MapReduce 통합

**위치**: `cointicker/worker-nodes/mapreduce/`

**주요 기능**:

- 데이터 정제 및 중복 제거
- 시간대별 집계
- 형식 통일

**실행 방법**:

```bash
cd cointicker/worker-nodes/mapreduce
bash run_mapreduce.sh
```

### 4. 오케스트레이션 계층 (Tier 1)

#### Orchestrator

**위치**: `cointicker/master-node/orchestrator.py`

**주요 기능**:

- 전체 파이프라인 오케스트레이션
- 크롤링 작업 스케줄링 (2분마다)
- 전체 파이프라인 실행 (5분마다)
- 공포·탐욕 지수 수집 (매일 자정)

**실행 방법**:

```bash
cd cointicker
python master-node/orchestrator.py
```

**systemd 서비스**:

```bash
sudo systemctl start orchestrator
sudo systemctl status orchestrator
```

### 5. 데이터 적재 계층 (Tier 2)

#### DataLoader

**위치**: `cointicker/backend/services/data_loader.py`

**주요 기능**:

- HDFS에서 정제된 데이터 다운로드
- JSON 파싱 및 타입별 분류
- PostgreSQL 적재 (중복 체크)

**실행 방법**:

```bash
cd cointicker
python scripts/run_pipeline.py
```

#### Tier 2 Scheduler

**위치**: `cointicker/scripts/run_pipeline_scheduler.py`

**주요 기능**:

- HDFS → PostgreSQL 적재 스케줄링 (30분마다)
- systemd 서비스로 실행 가능

**실행 방법**:

```bash
cd cointicker
python scripts/run_pipeline_scheduler.py
```

**systemd 서비스**:

```bash
sudo systemctl start tier2-scheduler
sudo systemctl status tier2-scheduler
```

### 6. 데이터베이스 계층 (Tier 2)

#### PostgreSQL 통합

**기본 데이터베이스**: PostgreSQL (MariaDB도 지원)

**설정 파일**: `cointicker/config/database_config.yaml`

```yaml
database:
  type: "postgresql" # 또는 "mariadb"

  postgresql:
    host: "localhost"
    port: 5432
    user: "cointicker"
    password: "password"
    database: "cointicker"
```

**주요 테이블**:

- `raw_news`: 뉴스 원본 데이터
- `market_trends`: 시장 트렌드 데이터
- `fear_greed_index`: 공포·탐욕 지수
- `sentiment_analysis`: 감성 분석 결과
- `technical_indicators`: 기술적 지표
- `crypto_insights`: 암호화폐 인사이트

### 7. API 계층 (Tier 2)

#### FastAPI Backend

**위치**: `cointicker/backend/app.py`

**주요 엔드포인트**:

- `GET /` - API 정보
- `GET /health` - 헬스 체크
- `GET /api/dashboard/summary` - 대시보드 요약
- `GET /api/dashboard/sentiment-timeline` - 감성 추이
- `GET /api/news/latest` - 최신 뉴스
- `GET /api/insights/recent` - 최신 인사이트
- `POST /api/insights/generate` - 인사이트 생성

**실행 방법**:

```bash
cd cointicker/backend
uvicorn app:app --host 0.0.0.0 --port 5000
```

### 8. 프론트엔드 계층 (Tier 2)

#### React Frontend

**위치**: `cointicker/frontend/`

**주요 기능**:

- 실시간 대시보드
- 데이터 시각화
- 인사이트 표시

**실행 방법**:

```bash
cd cointicker/frontend
npm install
npm run dev
```

### 9. 통합 관리 계층 (Tier 2)

#### GUI 애플리케이션

**위치**: `cointicker/gui/`

**주요 기능**:

- 모든 모듈 통합 관리
- 클러스터 실시간 모니터링
- Tier2 서버 관리
- 파이프라인 제어
- 설정 중앙 관리
- 설치 마법사

**실행 방법**:

```bash
# PICU 루트에서 실행 (권장)
bash scripts/run_gui.sh

# 또는 cointicker에서 실행
cd cointicker
python gui/main.py
```

## 🚀 통합 실행 순서

### 1. 전체 환경 설정

```bash
# 통합 설치 마법사 실행
bash scripts/start.sh
```

### 2. Tier 1 서비스 시작

```bash
# Orchestrator 시작
cd cointicker
python master-node/orchestrator.py

# 또는 systemd 서비스로
sudo systemctl start orchestrator
```

### 3. Tier 2 서비스 시작

```bash
# Tier 2 Scheduler 시작
cd cointicker
python scripts/run_pipeline_scheduler.py

# 또는 systemd 서비스로
sudo systemctl start tier2-scheduler

# FastAPI Backend 시작
cd cointicker/backend
uvicorn app:app --host 0.0.0.0 --port 5000

# React Frontend 시작
cd cointicker/frontend
npm run dev
```

### 4. GUI 통합 관리 시스템 시작

```bash
# PICU 루트에서 실행 (권장)
bash scripts/run_gui.sh
```

## 📊 모니터링

### GUI 통합 모니터링

GUI 애플리케이션에서 실시간으로 모든 모듈 상태를 확인할 수 있습니다:

- 클러스터 모니터링 탭: 라즈베리파이 노드 상태
- Tier2 탭: FastAPI 백엔드 및 데이터베이스 상태
- 모듈 탭: 모든 모듈 상태 및 제어

### 로그 모니터링

```bash
# 모든 로그 동시 모니터링
bash scripts/monitor_logs.sh

# 또는 GUI에서 로그 모니터링 메뉴 선택
```

**로그 위치**:

- Orchestrator: `cointicker/logs/orchestrator.log`
- Scheduler: `cointicker/logs/scheduler.log`
- Scrapyd: `cointicker/logs/scrapyd.log`

### 데이터베이스 상태 확인

```bash
# DB 상태 확인
python scripts/check_db_status.py
```

## 🔧 설정 관리

### 중앙 설정 파일

모든 설정은 `cointicker/config/` 디렉토리에 있습니다:

- `spider_config.yaml`: Spider 스케줄 설정
- `database_config.yaml`: 데이터베이스 설정
- `cluster_config.yaml`: 클러스터 설정
- `gui_config.yaml`: GUI 설정
- `kafka_config.yaml`: Kafka 설정 (선택)

### GUI를 통한 설정 관리

GUI 애플리케이션의 "설정" 탭에서 모든 설정을 중앙에서 관리할 수 있습니다.

## 🎯 다음 단계

1. **실시간 데이터 파이프라인 완성**

   - Scrapy → HDFS → MapReduce → PostgreSQL → Dashboard

2. **감성 분석 추가**

   - 뉴스 데이터 감성 분석
   - 투자 인사이트 생성

3. **알림 시스템 구축**

   - 중요한 시장 변동 알림
   - 뉴스 알림

4. **확장성 개선**
   - 워커 노드 추가
   - Spider 분산 배치

---

**통합 완료 후**: PICU 프로젝트는 2-Tier 아키텍처를 통해 안정적이고 확장 가능한 데이터 파이프라인을 제공합니다.
