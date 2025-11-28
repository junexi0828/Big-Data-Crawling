# 프로젝트 구조 문서

CoinTicker 프로젝트의 전체 디렉토리 구조 및 각 디렉토리의 역할을 설명합니다.

## 📁 전체 구조

```
cointicker/
├── backend/                 # FastAPI 백엔드 서버
│   ├── api/                 # API 라우트
│   │   ├── dashboard.py    # 대시보드 API
│   │   ├── insights.py      # 인사이트 API
│   │   ├── market.py        # 시장 데이터 API
│   │   └── news.py          # 뉴스 API
│   ├── services/            # 비즈니스 로직
│   │   ├── data_loader.py  # 데이터 로더
│   │   ├── insight_generator.py # 인사이트 생성
│   │   ├── sentiment_analyzer.py # 감성 분석
│   │   ├── technical_indicators.py # 기술적 지표
│   │   └── yahoo_finance_service.py # Yahoo Finance 서비스
│   ├── models/              # 데이터베이스 모델
│   ├── app.py               # FastAPI 애플리케이션
│   ├── config.py            # 설정
│   ├── init_db.py           # 데이터베이스 초기화
│   ├── models.py            # 모델 정의
│   └── run_server.sh        # 서버 실행 스크립트
│
├── frontend/                # React 프론트엔드
│   ├── public/              # 정적 파일
│   │   ├── index.html       # 프로젝트 소개
│   │   ├── architecture.html # 아키텍처 설명
│   │   ├── dashboard.html   # 대시보드
│   │   ├── data-pipeline.html # 데이터 파이프라인
│   │   ├── demo.html        # 데모
│   │   ├── live-dashboard.html # 실시간 대시보드
│   │   └── performance.html # 성과 분석
│   ├── src/                 # 소스 코드
│   │   ├── components/      # React 컴포넌트
│   │   │   ├── Layout.jsx  # 레이아웃
│   │   │   ├── dashboard/  # 대시보드 컴포넌트
│   │   │   ├── news/       # 뉴스 컴포넌트
│   │   │   └── insights/   # 인사이트 컴포넌트
│   │   ├── pages/           # 페이지 컴포넌트
│   │   │   ├── Home.jsx     # 홈
│   │   │   ├── Dashboard.jsx # 대시보드
│   │   │   ├── News.jsx     # 뉴스
│   │   │   ├── Insights.jsx # 인사이트
│   │   │   ├── Settings.jsx # 설정
│   │   │   └── NotFound.jsx # 404
│   │   ├── services/        # API 서비스
│   │   │   └── api.js       # API 클라이언트
│   │   ├── App.jsx          # 메인 앱
│   │   ├── main.jsx         # 진입점
│   │   └── index.css        # 전역 스타일
│   ├── package.json         # npm 패키지 설정
│   ├── vite.config.js       # Vite 설정
│   ├── run_dev.sh           # 개발 서버 실행 스크립트
│   └── README.md            # 프론트엔드 문서
│
├── gui/                     # GUI 애플리케이션 (PyQt5/tkinter)
│   ├── core/                # 핵심 모듈
│   │   ├── module_manager.py # 모듈 매니저
│   │   ├── config_manager.py # 설정 관리자
│   │   ├── cache_manager.py  # 캐시 관리자
│   │   ├── retry_utils.py    # 재시도 유틸리티
│   │   └── timing_config.py  # 타이밍 설정
│   ├── modules/             # 기능 모듈
│   │   ├── spider_module.py # Spider 관리
│   │   ├── mapreduce_module.py # MapReduce 관리
│   │   ├── hdfs_module.py   # HDFS 관리
│   │   ├── backend_module.py # Backend 관리
│   │   ├── kafka_module.py  # Kafka 관리
│   │   ├── pipeline_module.py # 파이프라인 관리
│   │   ├── pipeline_orchestrator.py # 파이프라인 오케스트레이터
│   │   ├── process_monitor.py # 프로세스 모니터
│   │   └── managers/        # 서비스 매니저
│   │       ├── hdfs_manager.py # HDFS 매니저
│   │       ├── kafka_manager.py # Kafka 매니저
│   │       └── ssh_manager.py  # SSH 매니저
│   ├── ui/                  # UI 탭 컴포넌트
│   │   ├── dashboard_tab.py # 대시보드 탭
│   │   ├── cluster_tab.py   # 클러스터 탭
│   │   ├── tier2_tab.py    # Tier2 서버 탭
│   │   ├── modules_tab.py  # 모듈 관리 탭
│   │   ├── control_tab.py  # 제어 탭
│   │   └── config_tab.py   # 설정 탭
│   ├── installer/           # 설치 마법사
│   │   ├── installer.py     # 설치 로직
│   │   ├── installer_cli.py # CLI 설치
│   │   ├── installer_gui.py # GUI 설치
│   │   └── unified_installer.py # 통합 설치
│   ├── tests/               # GUI 테스트
│   │   ├── test_refactoring.py # 리팩토링 테스트
│   │   └── test_integration.py # 통합 테스트
│   ├── app.py               # 메인 애플리케이션 (PyQt5)
│   ├── dashboard.py         # 대시보드 (tkinter fallback)
│   ├── cluster_monitor.py   # 클러스터 모니터링
│   ├── tier2_monitor.py     # Tier2 서버 모니터링
│   ├── main.py              # 진입점
│   ├── module_mapping.json  # 모듈 매핑 설정
│   ├── run.sh               # 실행 스크립트
│   ├── install.sh           # 설치 스크립트
│   ├── README.md            # GUI 문서
│   └── QUICK_START.md       # 빠른 시작 가이드
│
├── worker-nodes/            # 워커 노드 코드
│   ├── cointicker/          # Scrapy 프로젝트
│   │   ├── spiders/         # Spider 구현
│   │   │   ├── upbit_trends.py # Upbit Trends
│   │   │   ├── coinness.py  # Coinness
│   │   │   ├── saveticker.py # SaveTicker
│   │   │   ├── perplexity.py # Perplexity
│   │   │   └── cnn_fear_greed.py # CNN Fear & Greed
│   │   ├── items.py         # Item 정의
│   │   ├── pipelines.py     # 파이프라인
│   │   ├── settings.py      # Scrapy 설정
│   │   └── middlewares.py   # 미들웨어
│   ├── mapreduce/           # MapReduce 작업
│   │   ├── cleaner_mapper.py # 데이터 정제 Mapper
│   │   ├── cleaner_reducer.py # 데이터 정제 Reducer
│   │   └── run_cleaner.sh  # 실행 스크립트
│   ├── kafka_consumer.py    # Kafka Consumer
│   ├── kafka_consumer_service.py # Kafka Consumer 서비스
│   ├── run_kafka_consumer.sh # Kafka Consumer 실행 스크립트
│   ├── data/                # 임시 데이터
│   ├── logs/                # 로그 파일
│   └── scrapy.cfg           # Scrapy 설정
│
├── master-node/             # 마스터 노드 코드
│   ├── orchestrator.py      # 파이프라인 오케스트레이터
│   └── scheduler.py         # 스케줄러
│
├── shared/                  # 공통 라이브러리
│   ├── logger.py            # 로깅 유틸리티
│   ├── utils.py             # 공통 함수
│   ├── hdfs_client.py       # HDFS 클라이언트
│   ├── kafka_client.py      # Kafka 클라이언트
│   └── selenium_utils.py   # Selenium 유틸리티
│
├── config/                  # 설정 파일
│   ├── cluster_config.yaml  # 클러스터 설정
│   ├── cluster_config.yaml.example # 클러스터 설정 예제
│   ├── database_config.yaml # 데이터베이스 설정
│   ├── database_config.yaml.example # 데이터베이스 설정 예제
│   ├── spider_config.yaml   # Spider 설정
│   ├── spider_config.yaml.example # Spider 설정 예제
│   ├── gui_config.yaml      # GUI 설정
│   └── kafka_config.yaml.example # Kafka 설정 예제
│
├── scripts/                 # 유틸리티 스크립트
│   ├── run_pipeline.py      # 파이프라인 실행
│   └── test_process_flow.sh # 프로세스 흐름 테스트
│
├── deployment/              # 배포 스크립트 (예정)
│
├── docs/                    # 문서
│   ├── QUICKSTART.md        # 빠른 시작 가이드
│   ├── INTEGRATED_PIPELINE_GUIDE.md # 통합 파이프라인 가이드
│   ├── KAFKA_INTEGRATION.md # Kafka 통합 가이드
│   └── KAFKA_README.md      # Kafka README
│
├── tests/                   # 프로젝트 테스트
│   ├── test_backend.py      # Backend 테스트
│   ├── test_config_manager.py # ConfigManager 테스트
│   ├── test_integration.py  # 통합 테스트
│   ├── test_mapreduce.py   # MapReduce 테스트
│   ├── test_module_manager.py # ModuleManager 테스트
│   ├── test_spiders.py      # Spider 테스트
│   ├── test_tier2_monitor.py # Tier2Monitor 테스트
│   ├── test_utils.py        # 유틸리티 테스트
│   ├── run_all_tests.sh     # 전체 테스트 실행
│   ├── run_tests.sh         # 기본 테스트 실행
│   ├── run_integration_tests.sh # 통합 테스트 실행
│   └── README.md            # 테스트 문서
│
├── README.md                # 프로젝트 메인 README
├── PROJECT_STRUCTURE.md     # 이 파일
├── requirements.txt          # Python 의존성
└── venv/                    # 가상환경 (로컬)
```

## 📂 디렉토리별 상세 설명

### backend/

FastAPI 기반 백엔드 서버

- **api/**: REST API 엔드포인트
- **services/**: 비즈니스 로직 및 서비스 레이어
- **models/**: 데이터베이스 모델
- **app.py**: FastAPI 애플리케이션 메인 파일

### frontend/

React + Vite 기반 프론트엔드

- **public/**: 정적 HTML 파일 (레거시)
- **src/components/**: 재사용 가능한 React 컴포넌트
- **src/pages/**: 페이지 컴포넌트
- **src/services/**: API 클라이언트

### gui/

PyQt5/tkinter 기반 GUI 애플리케이션

- **core/**: 핵심 모듈 (매니저, 설정, 캐시 등)
- **modules/**: 기능 모듈 (Spider, HDFS, Kafka 등)
- **ui/**: UI 탭 컴포넌트
- **installer/**: 설치 마법사
- **tests/**: GUI 테스트

### worker-nodes/

워커 노드에서 실행되는 코드

- **cointicker/**: Scrapy 프로젝트
- **mapreduce/**: MapReduce 작업
- **kafka_consumer.py**: Kafka Consumer

### master-node/

마스터 노드에서 실행되는 코드

- **orchestrator.py**: 파이프라인 오케스트레이터
- **scheduler.py**: 스케줄러

### shared/

공통 라이브러리 (모든 컴포넌트에서 사용)

- **logger.py**: 로깅 유틸리티
- **utils.py**: 공통 함수
- **hdfs_client.py**: HDFS 클라이언트
- **kafka_client.py**: Kafka 클라이언트
- **selenium_utils.py**: Selenium 유틸리티

### config/

설정 파일

- **cluster_config.yaml**: 클러스터 설정
- **database_config.yaml**: 데이터베이스 설정
- **spider_config.yaml**: Spider 설정
- **gui_config.yaml**: GUI 설정

### scripts/

유틸리티 스크립트

- **run_pipeline.py**: 파이프라인 실행
- **test_process_flow.sh**: 프로세스 흐름 테스트

### tests/

프로젝트 테스트

- 단위 테스트 및 통합 테스트
- 테스트 실행 스크립트

### docs/

프로젝트 문서

- 가이드 및 README 파일

## 🔗 모듈 간 의존성

```
gui/
  ├── core/ (독립적)
  ├── modules/ → core/
  ├── ui/ → core/, modules/
  └── app.py → core/, modules/, ui/

backend/ (독립적)
frontend/ → backend/ (API 호출)
worker-nodes/ → shared/
master-node/ → shared/
```

## 📝 파일 명명 규칙

- **Python 파일**: `snake_case.py`
- **클래스**: `PascalCase`
- **함수/변수**: `snake_case`
- **상수**: `UPPER_SNAKE_CASE`
- **설정 파일**: `*_config.yaml`
- **테스트 파일**: `test_*.py`

## 🎯 디렉토리 정리 원칙

1. **관심사 분리**: 각 디렉토리는 명확한 역할을 가짐
2. **재사용성**: 공통 코드는 `shared/`에 배치
3. **테스트**: 각 모듈의 테스트는 `tests/`에 배치
4. **설정**: 모든 설정 파일은 `config/`에 배치
5. **문서**: 문서는 `docs/`에 배치

---

**최종 업데이트**: 2025-01-XX
