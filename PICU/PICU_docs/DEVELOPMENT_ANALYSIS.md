# 코인티커(CoinTicker) 프로젝트 개발 흐름 분석

> **분석 일자**: 2025-11-27
> **프로젝트 상태**: 개발 착수 준비 완료
> **아키텍처**: 2-Tier 분산 시스템

---

## 📊 전체 개발 흐름 요약

### 핵심 아키텍처

```
[개발 PC] → 통합 개발
    ↓
[배포] → rsync/SSH로 각 노드에 배포
    ↓
┌─────────────────────────────────────┐
│ Tier 1: 라즈베리파이 클러스터 (4대)  │
│ - 데이터 수집 & 저장 전담            │
│ - Scrapy + Hadoop + MapReduce      │
└──────────────┬──────────────────────┘
               │ SSH/REST API
               ↓
┌─────────────────────────────────────┐
│ Tier 2: 외부 서버 (일반 PC)          │
│ - 데이터 분석 & 대시보드            │
│ - FastAPI + MariaDB + React         │
└─────────────────────────────────────┘
```

---

## 🎯 개발 전략 핵심 포인트

### 1. 통합 개발 후 배포 방식

**개발 방식**

- ✅ 로컬에서 하나의 통합 프로젝트로 개발
- ✅ 각 노드별로 필요한 부분만 배포
- ✅ 공통 라이브러리는 shared/ 디렉토리로 관리

**프로젝트 구조**

```
cointicker/
├── master-node/        # 마스터 노드용 (라즈베리파이 #1)
├── worker-nodes/       # 워커 노드용 (라즈베리파이 #2,3,4)
├── shared/             # 공통 라이브러리
├── backend/            # 외부 서버 백엔드
├── frontend/           # 외부 서버 프론트엔드
└── deployment/         # 배포 스크립트
```

### 2. 2-Tier 아키텍처 선택 이유

**Tier 1 (라즈베리파이)**

- 저전력 24/7 운영
- 데이터 수집 및 저장에 집중
- 분산 처리로 속도 향상

**Tier 2 (외부 서버)**

- 고부하 작업 분리 (NLP, 시각화)
- 확장성 확보
- 개발 환경 유연성

---

## 🔄 데이터 파이프라인 흐름

### 전체 파이프라인 (30분 주기)

```
T+0분    [라즈베리파이] 크롤링 시작
         ├─ Worker 1: Upbit + Perplexity
         ├─ Worker 2: Coinness + CNN Fear & Greed
         └─ Worker 3: SaveTicker
         ↓
T+1분    HDFS 원시 데이터 저장 (/raw/)
         ↓
T+2분    MapReduce 정제 시작
         ├─ Mapper: 중복 제거, NULL 필터링
         └─ Reducer: 시간대별 집계
         ↓
T+4분    정제 완료 (/cleaned/ 디렉토리)
         ↓
T+5분    [외부 서버] HDFS 데이터 fetch (SSH/REST API)
         ↓
T+6분    MariaDB 적재
         ├─ raw_news 테이블
         ├─ market_trends 테이블
         └─ fear_greed_index 테이블
         ↓
T+7분    데이터 분석
         ├─ NLP 감성 분석 (FinBERT)
         ├─ 기술적 지표 계산 (RSI, MACD)
         └─ 인사이트 생성
         ↓
T+8분    API 서버 캐시 업데이트
         ↓
T+9분    대시보드 자동 새로고침 (60초 주기)
```

---

## 📋 단계별 개발 계획

### Phase 1: 인프라 구축 (Week 1-2)

**목표**: 라즈베리파이 클러스터 및 Hadoop 환경

**주요 작업**

1. 라즈베리파이 4대 Ubuntu Server 설치
2. 네트워크 구성 (SSH, 고정 IP)
3. Hadoop 클러스터 구축
   - NameNode (Master)
   - DataNode (Worker 1,2,3)
4. HDFS 테스트
5. YARN 및 MapReduce 환경 구성

**검증 기준**

- ✅ HDFS 파일 업로드/다운로드 성공
- ✅ MapReduce WordCount 예제 실행 성공
- ✅ 모든 노드 간 SSH 통신 정상

### Phase 2: 데이터 수집 (Week 3-4)

**목표**: Scrapy 기반 크롤링 파이프라인

**주요 작업**

1. Scrapy 프로젝트 초기화
2. 5개 Spider 구현
   - `upbit_spider.py` - Upbit Trends
   - `coinness_spider.py` - Coinness News
   - `saveticker_spider.py` - SaveTicker/Yahoo Finance
   - `perplexity_spider.py` - Perplexity Finance
   - `cnn_fear_greed_spider.py` - CNN Fear & Greed Index
3. HDFS Pipeline 연동
4. Cron/Scrapyd 스케줄 설정
5. 에러 핸들링 및 재시도 로직

**검증 기준**

- ✅ 5개 Spider가 정상적으로 데이터 수집
- ✅ HDFS에 원시 데이터 저장 확인
- ✅ 30분 주기 자동 실행 확인

### Phase 3: 데이터 정제 (Week 5-6)

**목표**: MapReduce를 통한 데이터 정제

**주요 작업**

1. MapReduce Mapper 구현
   - 중복 제거 (URL/타임스탬프 기준)
   - NULL 필터링
   - 형식 통일
2. MapReduce Reducer 구현
   - 시간대별 집계
   - 데이터 병합
3. 정제 파이프라인 테스트
4. 성능 최적화

**검증 기준**

- ✅ MapReduce 작업이 정상 실행
- ✅ 중복 데이터 제거 확인
- ✅ 정제된 데이터가 `/cleaned/` 디렉토리에 저장

### Phase 4: 데이터 전송 (Week 6)

**목표**: 라즈베리파이 → 외부 서버 데이터 전송

**주요 작업**

1. SSH/SFTP 스크립트 작성
2. 또는 REST API 전송 구현
3. 전송 실패 시 재시도 로직
4. 배치 전송 최적화

**검증 기준**

- ✅ 정제된 데이터가 외부 서버로 전송
- ✅ 네트워크 장애 시 로컬 큐잉 및 복구

### Phase 5: 백엔드 개발 (Week 7-8)

**목표**: FastAPI 백엔드 및 데이터 처리 엔진

**주요 작업**

1. FastAPI 프로젝트 초기화
2. MariaDB 스키마 설계 및 구현
   - `raw_news` - 원시 뉴스
   - `sentiment_analysis` - 감성 분석 결과
   - `market_trends` - 시장 트렌드
   - `technical_indicators` - 기술적 지표
   - `fear_greed_index` - 공포·탐욕 지수
   - `crypto_insights` - 인사이트
3. 데이터 적재 로직 구현
4. NLP 감성 분석 모듈 (FinBERT)
5. 기술적 지표 계산 모듈
6. 인사이트 생성 모듈
7. REST API 엔드포인트 구현 (10개 이상)

**검증 기준**

- ✅ 데이터가 MariaDB에 정상 저장
- ✅ 감성 분석 결과 생성
- ✅ 기술적 지표 계산 정확도 확인
- ✅ REST API 10개 이상 엔드포인트 동작

### Phase 6: 프론트엔드 개발 (Week 9-10)

**목표**: React 기반 실시간 대시보드

**주요 작업**

1. React 프로젝트 초기화
2. 대시보드 레이아웃 설계
3. API 연동 및 데이터 시각화
   - Chart.js 차트 구현
   - 실시간 업데이트 (60초 주기)
   - 반응형 디자인
4. 주요 화면 구현
   - 대시보드 홈
   - 감성 분석 차트
   - 기술적 지표 차트
   - 인사이트 목록
   - 공포·탐욕 지수

**검증 기준**

- ✅ 대시보드가 정상적으로 데이터 표시
- ✅ 실시간 업데이트 동작
- ✅ 반응형 디자인 적용

### Phase 7: 통합 및 최적화 (Week 11-12)

**목표**: 전체 파이프라인 통합 및 안정화

**주요 작업**

1. 전체 파이프라인 통합 테스트
2. 성능 최적화
3. 모니터링 및 로깅 체계 구축
4. 알림 시스템 구현
5. 문서화
6. 발표 준비

**검증 기준**

- ✅ 24/7 안정적 운영
- ✅ 전체 파이프라인 정상 동작
- ✅ 성능 목표 달성

---

## 🛠️ 기술 스택 상세

### Tier 1: 라즈베리파이 클러스터

| 컴포넌트         | 기술                    | 용도               |
| ---------------- | ----------------------- | ------------------ |
| OS               | Ubuntu Server 20.04 LTS | 경량 CLI 환경      |
| 분산 파일 시스템 | Hadoop HDFS 3.4.1       | 데이터 분산 저장   |
| 리소스 관리      | YARN 3.4.1              | 작업 스케줄링      |
| 데이터 처리      | MapReduce 3.4.1         | 분산 데이터 정제   |
| 웹 크롤링        | Scrapy 2.11+            | 데이터 수집        |
| 스케줄링         | Cron + APScheduler      | 정기 작업 실행     |
| 언어             | Python 3.8+             | 크롤러 및 스크립트 |

### Tier 2: 외부 서버

| 컴포넌트     | 기술            | 용도             |
| ------------ | --------------- | ---------------- |
| 백엔드       | FastAPI 0.110+  | REST API 서버    |
| 데이터베이스 | MariaDB 10.11+  | 정제 데이터 저장 |
| ORM          | SQLAlchemy 2.0+ | DB 추상화        |
| NLP 모델     | FinBERT         | 감성 분석        |
| 프론트엔드   | React 18+       | 대시보드 UI      |
| 차트         | Chart.js 4.4+   | 데이터 시각화    |

---

## 📁 프로젝트 구조

### 권장 디렉토리 구조

```
cointicker/
├── README.md
├── requirements.txt
│
├── config/                      # 설정 파일
│   ├── cluster_config.yaml      # 클러스터 설정
│   ├── spider_config.yaml      # Spider 설정
│   └── database_config.yaml    # DB 설정
│
├── master-node/                 # 마스터 노드 코드
│   ├── orchestrator.py          # 작업 분배 및 모니터링
│   ├── scheduler.py             # Scrapyd 스케줄러
│   └── config.yaml
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
│   └── config.yaml
│
├── shared/                      # 공통 라이브러리
│   ├── utils.py
│   ├── hdfs_client.py
│   └── logger.py
│
├── backend/                     # 외부 서버 백엔드
│   ├── app.py                   # FastAPI 메인
│   ├── models.py                # DB 모델
│   ├── services/                # 비즈니스 로직
│   │   ├── data_loader.py
│   │   ├── sentiment_analyzer.py
│   │   ├── technical_indicators.py
│   │   └── insight_generator.py
│   ├── api/                     # API 라우트
│   │   ├── dashboard.py
│   │   ├── sentiment.py
│   │   └── insights.py
│   └── config.py
│
├── frontend/                    # React 프론트엔드
│   ├── src/
│   │   ├── components/
│   │   ├── services/
│   │   └── App.js
│   └── public/
│
└── deployment/                  # 배포 스크립트
    ├── setup_master.sh
    ├── setup_worker.sh
    └── deploy_all.sh
```

---

## 🚀 개발 시작 순서

### 1단계: 프로젝트 구조 생성 (즉시 시작)

```bash
# 프로젝트 루트 디렉토리 생성
mkdir -p cointicker/{master-node,worker-nodes/spiders,worker-nodes/mapreduce,shared,backend/{services,api},frontend/src/{components,services},deployment,config,docs}

# 기본 파일 생성
touch cointicker/README.md
touch cointicker/requirements.txt
touch cointicker/.gitignore
```

### 2단계: 기존 프로젝트 통합 확인

**확인 사항**

- ✅ Scrapy 프로젝트 구조 (`scrapy_project/tutorial/`)
- ✅ Hadoop 프로젝트 구조 (`hadoop_project/`)
- ✅ Kafka 프로젝트 구조 (`kafka_project/`) - 선택사항
- ✅ Selenium 프로젝트 구조 (`selenium_project/`) - 선택사항

**통합 포인트**

- Scrapy 프로젝트의 Spider 구조 참고
- Hadoop 프로젝트의 MapReduce 예제 참고
- Kafka 프로젝트의 Producer/Consumer 참고 (실시간 스트리밍 확장 시)

### 3단계: 개발 환경 설정

**로컬 개발 환경**

```bash
# Python 가상환경 생성
python3 -m venv cointicker_env
source cointicker_env/bin/activate

# 기본 의존성 설치
pip install scrapy fastapi uvicorn sqlalchemy pymysql transformers torch
```

**설정 파일 템플릿 생성**

- `config/cluster_config.yaml` - 클러스터 설정
- `config/spider_config.yaml` - Spider 설정
- `config/database_config.yaml` - DB 설정

### 4단계: 첫 번째 Spider 구현

**우선순위**

1. **Upbit Trends Spider** (가장 단순)
2. **Coinness News Spider** (뉴스 데이터)
3. **SaveTicker Spider** (가격 데이터)

**구현 순서**

1. 기본 Spider 구조 작성
2. 데이터 파싱 로직 구현
3. HDFS Pipeline 연동
4. 테스트 및 검증

### 5단계: MapReduce 정제 작업

**구현 순서**

1. Mapper 작성 (중복 제거, 필터링)
2. Reducer 작성 (집계)
3. 테스트 및 검증
4. 성능 최적화

### 6단계: 백엔드 개발

**구현 순서**

1. FastAPI 프로젝트 초기화
2. MariaDB 스키마 설계 및 구현
3. 데이터 적재 로직
4. NLP 감성 분석 모듈
5. 기술적 지표 계산 모듈
6. REST API 엔드포인트

### 7단계: 프론트엔드 개발

**구현 순서**

1. React 프로젝트 초기화
2. 기본 레이아웃
3. API 연동
4. 차트 구현
5. 실시간 업데이트

---

## 📊 데이터베이스 스키마

### 핵심 테이블 구조

```sql
-- 1. 원시 뉴스
raw_news (id, source, title, url, published_at, keywords, collected_at)

-- 2. 감성 분석 결과
sentiment_analysis (id, news_id, sentiment_score, sentiment_label, confidence)

-- 3. 시장 트렌드
market_trends (id, source, symbol, volume_24h, price, change_24h, timestamp)

-- 4. 기술적 지표
technical_indicators (id, symbol, timestamp, rsi, macd, bb_upper, bb_middle, bb_lower)

-- 5. 공포·탐욕 지수
fear_greed_index (id, value, classification, timestamp)

-- 6. 암호화폐 인사이트
crypto_insights (id, insight_type, symbol, description, severity, related_news, created_at)
```

---

## 🔑 핵심 개발 포인트

### 1. 데이터 수집 계층

**Scrapy Spider 구조**

- 각 사이트별 독립적인 Spider
- 공통 Item 구조 사용
- HDFS Pipeline으로 자동 저장

**스케줄링**

- Cron 또는 Scrapyd 사용
- 사이트별 다른 주기 설정
- 실패 시 자동 재시도

### 2. 데이터 정제 계층

**MapReduce 작업**

- Mapper: 중복 제거, NULL 필터링
- Reducer: 시간대별 집계
- 정제된 데이터는 `/cleaned/` 디렉토리에 저장

### 3. 데이터 분석 계층

**NLP 감성 분석**

- FinBERT 모델 사용
- 뉴스 제목/본문 분석
- 점수: -1.0 (부정) ~ +1.0 (긍정)

**기술적 지표 계산**

- RSI(14), MACD(12,26,9)
- Bollinger Bands(20, 2)
- ATR(14), ADX(14)

**인사이트 생성**

- 감성 급변 감지
- 거래량 급증 감지
- 추세 반전 감지

### 4. 대시보드 계층

**REST API**

- `/api/dashboard/summary` - 대시보드 요약
- `/api/charts/sentiment-timeline` - 감성 추이
- `/api/insights/recent` - 최신 인사이트
- `/api/news/latest` - 최신 뉴스

**React 대시보드**

- 실시간 업데이트 (60초 주기)
- Chart.js 시각화
- 반응형 디자인

---

## ⚠️ 주요 고려사항

### 1. 라즈베리파이 리소스 최적화

**SD카드 보호**

- tmpfs 활용 (로그, 임시 파일)
- 로그 순환 설정
- 정기 백업

**메모리 관리**

- 배치 크기 조정
- 스왑 설정
- 메모리 모니터링

### 2. 네트워크 장애 대응

**로컬 큐잉**

- 네트워크 장애 시 로컬 저장
- 복구 시 자동 재전송
- 배치 처리로 효율성 향상

### 3. 크롤링 차단 방지

**Rate Limiting**

- 사이트별 요청 간격 조절
- User-Agent 회전
- Proxy 사용 (필요시)

### 4. 데이터 일관성

**중복 제거**

- URL 기준 중복 체크
- 타임스탬프 기준 중복 체크
- MapReduce에서 처리

---

## 📈 성능 목표

### 데이터 수집

- 일일 500~2,500개 데이터 수집
- 5~30분 주기 자동 업데이트
- 크롤링 성공률 95% 이상

### 데이터 처리

- MapReduce 정제 시간: 2~4분
- 감성 분석: 100개 뉴스 < 10초
- 기술적 지표 계산: 실시간

### 대시보드

- API 응답 시간: < 500ms
- 실시간 업데이트: 60초 주기
- 동시 사용자: 10명 이상 지원

---

## 🎯 다음 단계

### 즉시 시작 가능한 작업

1. **프로젝트 구조 생성**

   ```bash
   mkdir -p cointicker/{master-node,worker-nodes/spiders,shared,backend,frontend,deployment}
   ```

2. **기본 설정 파일 생성**

   - `requirements.txt`
   - `config/cluster_config.yaml`
   - `config/spider_config.yaml`

3. **첫 번째 Spider 구현**

   - Upbit Trends Spider부터 시작
   - 로컬 테스트 후 HDFS 연동

4. **개발 환경 문서화**
   - 개발 가이드 작성
   - API 문서 템플릿 생성

---

## 📚 참고 문서

- [PROJECT_DOCUMENTATION.md](./PROJECT_DOCUMENTATION.md) - 전체 프로젝트 문서
- [파이프라인 아키텍처 설계](./파이프라인%20아키텍처%20설계%202b8edd4b98c581bb9d6ec0a3aba7e37a.md) - 파이프라인 설계
- [코인티커 프로젝트 종합 설명서](<./코인티커(CoinTicker)_프로젝트%20종합%20설명서.md>) - 상세 설계
- [코드 코인티커 변경설계](./[코드]코인티커변경설계.md) - 구현 가이드
- [실습 통합 클러스터 구성](./실습통합클러스터구성.md) - 클러스터 구성 가이드

---

**개발 착수 준비 완료! 🚀**
