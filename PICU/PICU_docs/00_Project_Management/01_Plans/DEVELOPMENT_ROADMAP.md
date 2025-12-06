# 코인티커(CoinTicker) 프로젝트 개발 로드맵

> **프로젝트명**: 암호화폐 시장 동향 분석 및 실시간 대시보드 시스템
> **아키텍처**: 2-Tier 구조 (라즈베리파이 클러스터 + 외부 서버)
> **개발 기간**: 12주 (3개월)
> **최종 업데이트**: 2025-11-27

---

## 📋 목차

1. [프로젝트 개요](#1-프로젝트-개요)
2. [시스템 아키텍처](#2-시스템-아키텍처)
3. [개발 전략](#3-개발-전략)
4. [단계별 개발 계획](#4-단계별-개발-계획)
5. [기술 스택](#5-기술-스택)
6. [데이터 파이프라인](#6-데이터-파이프라인)
7. [프로젝트 구조](#7-프로젝트-구조)
8. [개발 우선순위](#8-개발-우선순위)

---

## 1. 프로젝트 개요

### 1.1 핵심 목표

**비즈니스 목표**

- 암호화폐 시장의 실시간 심리·기술적 동향을 정량화
- 투자자에게 유의미한 인사이트를 제공하는 대시보드 플랫폼
- 정보 수집 시간 절약 (30분 → 0분)
- 실시간성 확보 (5~30분 주기 자동 업데이트)

**기술 목표**

- 라즈베리파이 4대 기반 Hadoop 클러스터 구축
- Scrapy 기반 24/7 무중단 크롤링
- HDFS 분산 저장 및 MapReduce 정제
- NLP 감성 분석 및 기술적 지표 계산
- 실시간 대시보드 제공

### 1.2 데이터 소스

| 사이트                 | 수집 데이터                   | 업데이트 주기 | 담당 Worker |
| ---------------------- | ----------------------------- | ------------- | ----------- |
| **Upbit Trends**       | 거래량 급증 코인, 인기 검색어 | 5분           | Worker 1    |
| **Coinness**           | 암호화폐 특화 뉴스            | 10분          | Worker 2    |
| **SaveTicker**         | 주요 코인 가격, 기술적 지표   | 5분           | Worker 3    |
| **Perplexity Finance** | AI 기반 금융 요약             | 1시간         | Worker 1    |
| **CNN Fear & Greed**   | 공포·탐욕 지수                | 1일 1회       | Worker 2    |

---

## 2. 시스템 아키텍처

### 2.1 2-Tier 아키텍처

```
┌─────────────────────────────────────────────────────────┐
│         Tier 1: 라즈베리파이 클러스터 (4대)              │
│         ━━━ 데이터 수집 & 저장 전담 ━━━                 │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  [Master Node - 라즈베리파이 #1]                        │
│   • Hadoop NameNode (HDFS 메타데이터 관리)              │
│   • YARN ResourceManager (작업 스케줄링)                │
│   • Scrapyd Scheduler (크롤링 작업 관리)                 │
│                                                          │
│  [Worker Nodes - 라즈베리파이 #2,3,4]                  │
│   • Hadoop DataNode (데이터 분산 저장)                 │
│   • Scrapy Spiders (병렬 크롤링)                        │
│   • MapReduce (기초 정제: 중복제거, 형식 통일)         │
│                                                          │
└─────────────────┬───────────────────────────────────────┘
                  │ SSH/REST API
                  │ 정제된 데이터 전송
                  ↓
┌─────────────────────────────────────────────────────────┐
│         Tier 2: 외부 서버 (일반 PC/클라우드)            │
│         ━━━ 데이터 분석 & 대시보드 운영 ━━━            │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  [데이터 처리 계층]                                      │
│   • HDFS 데이터 fetch                                   │
│   • MariaDB/PostgreSQL 적재                             │
│   • NLP 감성분석 (FinBERT/KoBERT)                      │
│   • 기술적 지표 계산 (RSI, MACD, 볼린저밴드)            │
│   • 암호화폐 특화 트렌드 분석                            │
│                                                          │
│  [대시보드 계층]                                         │
│   • Backend: Flask/FastAPI (REST API)                  │
│   • Frontend: React/Vue + Chart.js                      │
│   • 실시간 시각화: WebSocket 연동                       │
│   • 알림 시스템: Email/Slack/Telegram                  │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### 2.2 아키텍처 선택 이유

**2-Tier 구조의 장점**

1. **라즈베리파이 리소스 최적화**: 데이터 수집과 저장에만 집중
2. **외부 서버 활용**: 고부하 작업(DB 쿼리, 시각화) 분리
3. **장애 격리**: 크롤러 장애가 대시보드에 영향 없음
4. **확장성**: 필요시 서버 스펙 업그레이드 가능

---

## 3. 개발 전략

### 3.1 설계 원칙

1. **관심사 분리 (Separation of Concerns)**

   - 라즈베리파이: 데이터 수집 및 저장
   - 외부 서버: 데이터 분석 및 시각화

2. **단계적 개발 (Incremental Development)**

   - Phase 1: 인프라 구축
   - Phase 2: 데이터 수집
   - Phase 3: 데이터 정제
   - Phase 4: 백엔드 개발
   - Phase 5: 프론트엔드 개발
   - Phase 6: 통합 및 최적화

3. **테스트 주도 (Test-Driven)**

   - 각 단계마다 검증 및 테스트
   - 단위 테스트, 통합 테스트 작성

4. **확장성 고려 (Scalability)**
   - 새로운 데이터 소스 추가 용이
   - Worker 노드 추가 가능
   - 모듈화된 코드 구조

### 3.2 개발 방식

**통합 개발 후 배포 방식**

```
개발 PC (로컬)
├── cointicker/
│   ├── master-node/        # 마스터 노드용 코드
│   ├── worker-nodes/       # 워커 노드용 코드
│   ├── shared/             # 공통 라이브러리
│   └── deployment/          # 배포 스크립트
│
배포 시
├── rsync로 각 노드에 배포
└── systemd 서비스로 자동 실행
```

---

## 4. 단계별 개발 계획

### Phase 1: 인프라 구축 (Week 1-2)

**목표**: 라즈베리파이 클러스터 및 Hadoop 환경 구축

**주요 작업**

- [ ] 라즈베리파이 4대 Ubuntu Server 설치
- [ ] 네트워크 구성 (SSH, 고정 IP)
- [ ] Hadoop 클러스터 구축 (NameNode, DataNode)
- [ ] HDFS 테스트 (파일 업로드/다운로드)
- [ ] YARN 및 MapReduce 환경 구성

**검증 기준**

- HDFS 파일 업로드/다운로드 성공
- MapReduce WordCount 예제 실행 성공
- 모든 노드 간 SSH 통신 정상

### Phase 2: 데이터 수집 (Week 3-4)

**목표**: Scrapy 기반 크롤링 파이프라인 구현

**주요 작업**

- [ ] Scrapy 프로젝트 초기화
- [ ] 5개 Spider 구현
  - [ ] Upbit Trends Spider
  - [ ] Coinness News Spider
  - [ ] SaveTicker Spider
  - [ ] Perplexity Finance Spider
  - [ ] CNN Fear & Greed Spider
- [ ] HDFS Pipeline 연동
- [ ] Cron/Scrapyd 스케줄 설정
- [ ] 에러 핸들링 및 재시도 로직

**검증 기준**

- 5개 Spider가 정상적으로 데이터 수집
- HDFS에 원시 데이터 저장 확인
- 30분 주기 자동 실행 확인

### Phase 3: 데이터 정제 (Week 5-6)

**목표**: MapReduce를 통한 데이터 정제 및 집계

**주요 작업**

- [ ] MapReduce Mapper 구현
  - [ ] 중복 제거 로직
  - [ ] NULL 필터링
  - [ ] 형식 통일
- [ ] MapReduce Reducer 구현
  - [ ] 시간대별 집계
  - [ ] 데이터 병합
- [ ] 정제 파이프라인 테스트
- [ ] 성능 최적화

**검증 기준**

- MapReduce 작업이 정상 실행
- 중복 데이터 제거 확인
- 정제된 데이터가 `/cleaned/` 디렉토리에 저장

### Phase 4: 데이터 전송 (Week 6)

**목표**: 라즈베리파이 → 외부 서버 데이터 전송

**주요 작업**

- [ ] SSH/SFTP 스크립트 작성
- [ ] 또는 REST API 전송 구현
- [ ] 전송 실패 시 재시도 로직
- [ ] 배치 전송 최적화

**검증 기준**

- 정제된 데이터가 외부 서버로 전송
- 네트워크 장애 시 로컬 큐잉 및 복구

### Phase 5: 백엔드 개발 (Week 7-8)

**목표**: Flask/FastAPI 백엔드 및 데이터 처리 엔진

**주요 작업**

- [ ] Flask/FastAPI 프로젝트 초기화
- [ ] 데이터베이스 스키마 설계
  - [ ] raw_news 테이블
  - [ ] sentiment_analysis 테이블
  - [ ] market_trends 테이블
  - [ ] technical_indicators 테이블
  - [ ] crypto_insights 테이블
- [ ] 데이터 적재 로직 구현
- [ ] NLP 감성 분석 모듈 (FinBERT)
- [ ] 기술적 지표 계산 모듈
- [ ] 인사이트 생성 모듈
- [ ] REST API 엔드포인트 구현 (10개 이상)

**검증 기준**

- 데이터가 MariaDB에 정상 저장
- 감성 분석 결과 생성
- 기술적 지표 계산 정확도 확인
- REST API 10개 이상 엔드포인트 동작

### Phase 6: 프론트엔드 개발 (Week 9-10)

**목표**: React 기반 실시간 대시보드

**주요 작업**

- [ ] React 프로젝트 초기화
- [ ] 대시보드 레이아웃 설계
- [ ] API 연동 및 데이터 시각화
  - [ ] Chart.js 차트 구현
  - [ ] 실시간 업데이트 (60초 주기)
  - [ ] 반응형 디자인
- [ ] 주요 화면 구현
  - [ ] 대시보드 홈
  - [ ] 감성 분석 차트
  - [ ] 기술적 지표 차트
  - [ ] 인사이트 목록
  - [ ] 공포·탐욕 지수

**검증 기준**

- 대시보드가 정상적으로 데이터 표시
- 실시간 업데이트 동작
- 반응형 디자인 적용

### Phase 7: 통합 및 최적화 (Week 11-12)

**목표**: 전체 파이프라인 통합 및 안정화

**주요 작업**

- [ ] 전체 파이프라인 통합 테스트
- [ ] 성능 최적화
- [ ] 모니터링 및 로깅 체계 구축
- [ ] 알림 시스템 구현
- [ ] 문서화
- [ ] 발표 준비

**검증 기준**

- 24/7 안정적 운영
- 전체 파이프라인 정상 동작
- 성능 목표 달성

---

## 5. 기술 스택

### 5.1 Tier 1 (라즈베리파이 클러스터)

| 역할             | 기술               | 버전      | 용도               |
| ---------------- | ------------------ | --------- | ------------------ |
| OS               | Ubuntu Server      | 20.04 LTS | 경량 CLI 환경      |
| 분산 파일 시스템 | Hadoop HDFS        | 3.4.1     | 데이터 분산 저장   |
| 리소스 관리      | YARN               | 3.4.1     | 작업 스케줄링      |
| 데이터 처리      | MapReduce          | 3.4.1     | 분산 데이터 정제   |
| 웹 크롤링        | Scrapy             | 2.11+     | 데이터 수집        |
| 스케줄링         | Cron + APScheduler | -         | 정기 작업 실행     |
| 언어             | Python             | 3.8+      | 크롤러 및 스크립트 |

### 5.2 Tier 2 (외부 서버)

| 역할              | 기술       | 버전   | 용도             |
| ----------------- | ---------- | ------ | ---------------- |
| 백엔드 프레임워크 | FastAPI    | 0.110+ | REST API 서버    |
| 데이터베이스      | MariaDB    | 10.11+ | 정제 데이터 저장 |
| ORM               | SQLAlchemy | 2.0+   | DB 추상화        |
| NLP 모델          | FinBERT    | -      | 감성 분석        |
| 프론트엔드        | React      | 18+    | 대시보드 UI      |
| 차트 라이브러리   | Chart.js   | 4.4+   | 데이터 시각화    |

---

## 6. 데이터 파이프라인

### 6.1 전체 파이프라인 흐름

```
T+0분    크롤링 시작 (라즈베리파이 Worker)
         ↓
T+1분    HDFS 원시 데이터 저장 (/raw/)
         ↓
T+2분    MapReduce 정제 시작
         ↓
T+4분    정제 완료 (/cleaned/ 디렉토리)
         ↓
T+5분    외부 서버 데이터 fetch (SSH/REST API)
         ↓
T+6분    DB 적재 (MariaDB)
         ↓
T+7분    NLP 감성 분석 + 기술적 지표 계산
         ↓
T+8분    인사이트 생성
         ↓
T+9분    API 서버 캐시 업데이트
         ↓
T+10분   대시보드 자동 새로고침
```

### 6.2 각 단계 상세

**Phase 1: 데이터 수집**

- Scrapy Spider 실행
- HTML/JSON 크롤링
- HDFS에 원시 데이터 저장

**Phase 2: 데이터 정제**

- MapReduce Mapper: 중복 제거, NULL 필터링
- MapReduce Reducer: 시간대별 집계
- 정제된 데이터 저장

**Phase 3: 데이터 전송**

- SSH/SFTP 또는 REST API로 전송
- 네트워크 장애 시 로컬 큐잉

**Phase 4: 데이터 적재**

- JSON 파싱
- MariaDB 적재
- 중복 체크

**Phase 5: 데이터 분석**

- NLP 감성 분석 (FinBERT)
- 기술적 지표 계산 (RSI, MACD 등)
- 인사이트 생성

**Phase 6: 데이터 제공**

- REST API 엔드포인트
- 실시간 대시보드 업데이트

---

## 7. 프로젝트 구조

### 7.1 디렉토리 구조

```
cointicker/
├── README.md                    # 프로젝트 개요
├── requirements.txt             # Python 의존성
├── config/                      # 설정 파일
│   ├── cluster_config.yaml      # 클러스터 설정
│   ├── spider_config.yaml      # Spider 설정
│   └── database_config.yaml    # DB 설정
│
├── master-node/                 # 마스터 노드 코드
│   ├── orchestrator.py          # 작업 분배 및 모니터링
│   ├── scheduler.py             # Scrapyd 스케줄러
│   └── config.yaml              # 마스터 설정
│
├── worker-nodes/                # 워커 노드 코드
│   ├── spiders/                 # Scrapy Spiders
│   │   ├── upbit_spider.py
│   │   ├── coinness_spider.py
│   │   ├── saveticker_spider.py
│   │   ├── perplexity_spider.py
│   │   └── cnn_fear_greed_spider.py
│   ├── pipelines.py             # HDFS Pipeline
│   ├── mapreduce/               # MapReduce 작업
│   │   ├── cleaner_mapper.py
│   │   └── cleaner_reducer.py
│   └── config.yaml              # 워커 설정
│
├── shared/                      # 공통 라이브러리
│   ├── utils.py                 # 유틸리티 함수
│   ├── hdfs_client.py           # HDFS 클라이언트
│   └── logger.py                # 로깅 설정
│
├── backend/                     # 외부 서버 백엔드
│   ├── app.py                   # FastAPI 메인
│   ├── models.py                # DB 모델
│   ├── services/                 # 비즈니스 로직
│   │   ├── data_loader.py       # 데이터 적재
│   │   ├── sentiment_analyzer.py # 감성 분석
│   │   ├── technical_indicators.py # 기술적 지표
│   │   └── insight_generator.py # 인사이트 생성
│   ├── api/                      # API 라우트
│   │   ├── dashboard.py
│   │   ├── sentiment.py
│   │   └── insights.py
│   └── config.py                # 설정
│
├── frontend/                     # React 프론트엔드
│   ├── src/
│   │   ├── components/          # React 컴포넌트
│   │   ├── services/            # API 통신
│   │   └── App.js
│   └── public/
│
├── deployment/                   # 배포 스크립트
│   ├── setup_master.sh          # 마스터 노드 배포
│   ├── setup_worker.sh          # 워커 노드 배포
│   └── deploy_all.sh             # 전체 배포
│
└── docs/                         # 문서
    ├── API_DOCUMENTATION.md      # API 문서
    ├── DEPLOYMENT_GUIDE.md       # 배포 가이드
    └── TROUBLESHOOTING.md        # 문제 해결
```

---

## 8. 개발 우선순위

### 8.1 필수 구현 사항 (MVP)

**Phase 1-2: 인프라 및 수집**

1. ✅ Hadoop 클러스터 구축
2. ✅ Scrapy 프로젝트 초기화
3. ✅ 최소 3개 Spider 구현 (Upbit, Coinness, SaveTicker)
4. ✅ HDFS Pipeline 연동

**Phase 3-4: 정제 및 전송** 5. ✅ MapReduce 정제 작업 6. ✅ 데이터 전송 메커니즘

**Phase 5-6: 백엔드 및 프론트엔드** 7. ✅ FastAPI 백엔드 기본 구조 8. ✅ MariaDB 스키마 및 적재 9. ✅ 기본 대시보드 (통계만)

### 8.2 선택 구현 사항

**고급 기능**

- [ ] NLP 감성 분석 (FinBERT)
- [ ] 기술적 지표 계산 (RSI, MACD)
- [ ] 인사이트 자동 생성
- [ ] WebSocket 실시간 통신
- [ ] 알림 시스템 (Email/Slack)

**최적화**

- [ ] Redis 캐싱
- [ ] Kafka 실시간 스트리밍
- [ ] Docker 컨테이너화
- [ ] CI/CD 파이프라인

---

## 9. 다음 단계

### 9.1 즉시 시작 가능한 작업

1. **프로젝트 구조 생성**

   ```bash
   mkdir -p cointicker/{master-node,worker-nodes,shared,backend,frontend,deployment,docs}
   ```

2. **기존 프로젝트 통합 확인**

   - Scrapy 프로젝트 구조 확인
   - Hadoop 프로젝트 구조 확인
   - Kafka 프로젝트 구조 확인

3. **개발 환경 설정**
   - Python 가상환경 생성
   - 의존성 설치
   - 설정 파일 템플릿 생성

### 9.2 개발 시작 순서

1. **Week 1**: 프로젝트 구조 생성 및 기본 설정
2. **Week 2**: 첫 번째 Spider 구현 및 테스트
3. **Week 3**: HDFS Pipeline 연동
4. **Week 4**: MapReduce 정제 작업 구현
5. **Week 5**: 백엔드 기본 구조 구현
6. **Week 6**: 데이터 적재 로직 구현
7. **Week 7**: 프론트엔드 기본 대시보드
8. **Week 8**: 통합 테스트 및 최적화

---

## 10. 참고 문서

- [PROJECT_DOCUMENTATION.md](./PROJECT_DOCUMENTATION.md) - 전체 프로젝트 문서
- [파이프라인 아키텍처 설계](./파이프라인%20아키텍처%20설계%202b8edd4b98c581bb9d6ec0a3aba7e37a.md) - 파이프라인 설계
- [코인티커 프로젝트 종합 설명서](<./코인티커(CoinTicker)_프로젝트%20종합%20설명서.md>) - 상세 설계
- [코드 코인티커 변경설계](./[코드]코인티커변경설계.md) - 구현 가이드

---

**프로젝트 성공을 기원합니다! 🚀**
