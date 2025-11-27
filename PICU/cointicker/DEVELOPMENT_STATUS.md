# 코인티커 프로젝트 개발 현황

> **최종 업데이트**: 2025-11-27

## ✅ 완료된 작업

### 1. 프로젝트 구조 ✅
- 전체 디렉토리 구조 생성
- 설정 파일 템플릿 생성
- 공통 라이브러리 구현

### 2. Scrapy Spiders ✅ (5개)
- ✅ `upbit_trends.py` - Upbit API
- ✅ `coinness.py` - 코인니스 뉴스
- ✅ `saveticker.py` - SaveTicker/Yahoo Finance
- ✅ `perplexity.py` - Perplexity AI
- ✅ `cnn_fear_greed.py` - 공포·탐욕 지수

### 3. HDFS 저장 모듈 ✅
- ✅ `HDFSPipeline` - Scrapy Pipeline 구현
- ✅ `HDFSClient` - HDFS 클라이언트 유틸리티

### 4. MapReduce 작업 ✅
- ✅ `cleaner_mapper.py` - 데이터 정제 및 중복 제거
- ✅ `cleaner_reducer.py` - 시간대별 집계
- ✅ `run_cleaner.sh` - 실행 스크립트

### 5. 백엔드 서비스 ✅
- ✅ `app.py` - FastAPI 메인 애플리케이션
- ✅ `models.py` - 데이터베이스 모델
- ✅ `config.py` - 설정 파일
- ✅ `data_loader.py` - 데이터 로더 서비스
- ✅ `sentiment_analyzer.py` - 감성 분석 서비스 (FinBERT)
- ✅ `technical_indicators.py` - 기술적 지표 계산
- ✅ `insight_generator.py` - 인사이트 생성

### 6. API 엔드포인트 ✅
- ✅ `/api/dashboard/summary` - 대시보드 요약
- ✅ `/api/dashboard/sentiment-timeline` - 감성 추이
- ✅ `/api/insights/recent` - 최신 인사이트
- ✅ `/api/news/latest` - 최신 뉴스

### 7. 파이프라인 오케스트레이터 ✅
- ✅ `orchestrator.py` - 전체 파이프라인 관리
- ✅ `scheduler.py` - Scrapyd 스케줄러

## 📊 프로젝트 통계

- **Python 파일**: 20+ 개
- **Spider 개수**: 5개
- **API 엔드포인트**: 6개
- **서비스 모듈**: 4개

## 🚀 다음 단계

### 즉시 테스트 가능
1. Spider 로컬 테스트
2. FastAPI 서버 실행
3. 데이터베이스 스키마 생성

### 추가 개발 필요
1. 프론트엔드 React 컴포넌트 구현
2. 데이터베이스 마이그레이션
3. 배포 스크립트 완성
4. 모니터링 및 로깅 강화

## 📝 실행 방법

### Spider 테스트
```bash
cd worker-nodes
scrapy crawl upbit_trends -o output.json
```

### 백엔드 서버 실행
```bash
cd backend
python app.py
# 또는
uvicorn app:app --host 0.0.0.0 --port 5000
```

### 파이프라인 오케스트레이터 실행
```bash
cd master-node
python orchestrator.py
```

---

**개발 진행률: 약 70% 완료** 🎉

