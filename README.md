# PICU 프로젝트

> **PICU**: Personal Investment & Cryptocurrency Understanding
> 암호화폐 데이터 수집, 분석, 시각화를 위한 통합 플랫폼

---

## 📋 프로젝트 개요

PICU는 **2-Tier 아키텍처**를 기반으로 한 분산 데이터 파이프라인 시스템입니다.

| 구성 요소  | 설명                                                   |
| ---------- | ------------------------------------------------------ |
| **Tier 1** | 라즈베리파이 클러스터 (4대) - 데이터 수집 및 분산 처리 |
| **Tier 2** | 외부 서버 - 데이터 적재, 분석, 시각화                  |

---

## 🏗️ 시스템 아키텍처

### 전체 구조

```
┌─────────────────────────────────────────────────────────────┐
│                    PICU 통합 파이프라인                       │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  Tier 1: 라즈베리파이 클러스터 (4대)                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Master Node (라즈베리파이 1번)                              │
│  ├─ Hadoop NameNode (HDFS 메타데이터)                      │
│  ├─ YARN ResourceManager (작업 스케줄링)                    │
│  ├─ Orchestrator (파이프라인 오케스트레이션)                 │
│  └─ Scrapyd Scheduler (크롤링 스케줄링)                      │
│                                                             │
│  Worker Nodes (라즈베리파이 2,3,4번)                        │
│  ├─ Worker 1: Upbit + Perplexity 크롤링                    │
│  ├─ Worker 2: Coinness + CNN 크롤링                         │
│  ├─ Worker 3: SaveTicker 크롤링                            │
│  └─ Hadoop DataNode (HDFS 블록 저장)                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                    │
                    │ [SSH / HDFS 클라이언트]
                    ↓
┌─────────────────────────────────────────────────────────────┐
│  Tier 2: 외부 서버                                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  DataLoader → PostgreSQL 적재                              │
│  FastAPI Backend → RESTful API                              │
│  React Frontend → 실시간 대시보드                            │
│  GUI 통합 관리 시스템 → 모듈 통합 관리                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔄 데이터 파이프라인

### 데이터 흐름

| 단계 | 계층     | 컴포넌트           | 역할                             |
| ---- | -------- | ------------------ | -------------------------------- |
| 1    | 수집     | Scrapy Spiders     | 암호화폐 뉴스/시장 데이터 크롤링 |
| 2    | 검증     | ValidationPipeline | 데이터 검증                      |
| 3    | 중복제거 | DuplicatesPipeline | 중복 데이터 제거                 |
| 4    | 저장     | HDFSPipeline       | HDFS `/raw/` 저장                |
| 5    | 정제     | MapReduce          | 데이터 정제 및 집계              |
| 6    | 저장     | HDFS               | HDFS `/cleaned/` 저장            |
| 7    | 전송     | SSH/HDFS Client    | Tier 1 → Tier 2 전송             |
| 8    | 적재     | DataLoader         | PostgreSQL 적재                  |
| 9    | 분석     | FastAPI Backend    | 데이터 분석 및 API 제공          |
| 10   | 시각화   | React Frontend     | 실시간 대시보드                  |

### 스케줄링

| 컴포넌트          | 주기      | 역할                   |
| ----------------- | --------- | ---------------------- |
| Orchestrator      | 2분       | 크롤링 작업 실행       |
| Orchestrator      | 5분       | 전체 파이프라인 실행   |
| Orchestrator      | 매일 자정 | 공포·탐욕 지수 수집    |
| Scrapyd Scheduler | 설정 기반 | Spider 스케줄링        |
| Tier 2 Scheduler  | 30분      | HDFS → PostgreSQL 적재 |

---

## 🛠️ 주요 서비스

### Tier 1 서비스

| 서비스             | 위치                                          | 역할                      |
| ------------------ | --------------------------------------------- | ------------------------- |
| **Orchestrator**   | `cointicker/master-node/orchestrator.py`      | 파이프라인 오케스트레이션 |
| **Scheduler**      | `cointicker/master-node/scheduler.py`         | Scrapyd 스케줄링          |
| **Scrapy Spiders** | `cointicker/worker-nodes/cointicker/spiders/` | 데이터 크롤링             |
| **HDFS**           | Hadoop 클러스터                               | 분산 저장                 |
| **MapReduce**      | `cointicker/worker-nodes/mapreduce/`          | 데이터 정제               |

### Tier 2 서비스

| 서비스              | 위치                                         | 역할                   |
| ------------------- | -------------------------------------------- | ---------------------- |
| **DataLoader**      | `cointicker/backend/services/data_loader.py` | HDFS → PostgreSQL 적재 |
| **FastAPI Backend** | `cointicker/backend/app.py`                  | RESTful API            |
| **React Frontend**  | `cointicker/frontend/`                       | 실시간 대시보드        |
| **GUI 통합 관리**   | `cointicker/gui/`                            | 모듈 통합 관리         |

---

## 📊 클러스터 구성

### 노드 역할 분담

| 노드                 | 역할          | 서비스                                             |
| -------------------- | ------------- | -------------------------------------------------- |
| **Master (RPi 1)**   | 클러스터 관리 | NameNode, ResourceManager, Orchestrator, Scheduler |
| **Worker 1 (RPi 2)** | 데이터 수집   | Upbit, Perplexity 크롤링, DataNode                 |
| **Worker 2 (RPi 3)** | 데이터 수집   | Coinness, CNN 크롤링, DataNode                     |
| **Worker 3 (RPi 4)** | 데이터 수집   | SaveTicker 크롤링, DataNode                        |

### Spider 배포

| Spider         | 소스               | Worker   | 주기  |
| -------------- | ------------------ | -------- | ----- |
| upbit_trends   | 업비트 시장 트렌드 | Worker 1 | 5분   |
| perplexity     | Perplexity Finance | Worker 1 | 1시간 |
| coinness       | 코인니스 뉴스      | Worker 2 | 10분  |
| cnn_fear_greed | CNN 공포·탐욕 지수 | Worker 2 | 매일  |
| saveticker     | 세이브티커 뉴스    | Worker 3 | 5분   |

---

## 🔌 통신 구조

### Tier 1 내부 통신

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│   Master    │◄────►│   Worker 1   │      │   Worker 2  │
│             │      │             │      │             │
│ - NameNode  │      │ - DataNode  │      │ - DataNode  │
│ - Resource  │      │ - Scrapy    │      │ - Scrapy    │
│   Manager   │      │   Spider    │      │   Spider    │
└─────────────┘      └─────────────┘      └─────────────┘
       │                    │                    │
       └────────────────────┴────────────────────┘
                            │
                    ┌───────▼────────┐
                    │  HDFS Cluster │
                    └────────────────┘
```

### Tier 1 ↔ Tier 2 통신

| 통신 방식   | 프로토콜 | 용도                      |
| ----------- | -------- | ------------------------- |
| SSH         | SSH      | 원격 명령 실행, 파일 전송 |
| HDFS Client | HDFS API | 데이터 다운로드           |
| HTTP        | REST API | 상태 모니터링             |

---

## 🗄️ 데이터베이스 구조

### PostgreSQL 스키마

| 테이블               | 용도               |
| -------------------- | ------------------ |
| raw_news             | 원시 뉴스 데이터   |
| market_trends        | 시장 트렌드 데이터 |
| fear_greed_index     | 공포·탐욕 지수     |
| sentiment_analysis   | 감성 분석 결과     |
| technical_indicators | 기술적 지표        |
| crypto_insights      | 암호화폐 인사이트  |

### HDFS 디렉토리 구조

```
/raw/
  ├── upbit/
  │   └── 20251208/
  ├── coinness/
  │   └── 20251208/
  ├── saveticker/
  │   └── 20251208/
  └── perplexity/
      └── 20251208/

/cleaned/
  └── 20251208/
      └── aggregated_*.json
```

---

## 🚀 빠른 시작

### 설치

```bash
# 통합 설치 마법사
bash scripts/start.sh
```

### 실행

```bash
# GUI 통합 관리 시스템 실행
bash scripts/run_gui.sh
```

### 서비스 관리

| 서비스           | 시작                              | 중지                             |
| ---------------- | --------------------------------- | -------------------------------- |
| Orchestrator     | `systemctl start orchestrator`    | `systemctl stop orchestrator`    |
| Scrapyd          | `systemctl start scrapyd`         | `systemctl stop scrapyd`         |
| Tier 2 Scheduler | `systemctl start tier2-scheduler` | `systemctl stop tier2-scheduler` |

---

## 📚 문서

### 핵심 문서

- [PICU 문서](PICU/PICU_docs/README.md) - 전체 프로젝트 문서
- [통합 가이드](PICU/PICU_docs/02_Design_and_Architecture/01_Software_Architecture_Design/INTEGRATION_GUIDE.md) - 아키텍처 상세
- [파이프라인 설계](PICU/PICU*docs/02_Design_and_Architecture/01_Software_Architecture_Design/파이프라인* 아키텍처\_설계.md) - 파이프라인 상세

### 운영 문서

- [배포 가이드](PICU/PICU_docs/05_Deployment_and_Release/01_Deployment_Guide/DEPLOYMENT_GUIDE.md)
- [사용자 매뉴얼](PICU/PICU_docs/06_Operations_and_Maintenance/01_User_Manual/)
- [트러블슈팅](PICU/PICU_docs/06_Operations_and_Maintenance/02_Troubleshooting_Guide/)

---

## 📝 레거시 프로젝트

> ⚠️ **참고**: 아래 프로젝트는 레거시 백업으로 유지됩니다.

- **Scrapy 고급 기능 실습 프로젝트**: Scrapy 학습용 프로젝트 (백업)
- **Kafka 프로젝트**: Kafka 학습용 프로젝트 (백업)
- **Selenium 프로젝트**: Selenium 학습용 프로젝트 (백업)

---

**PICU 프로젝트** - Personal Investment & Cryptocurrency Understanding
