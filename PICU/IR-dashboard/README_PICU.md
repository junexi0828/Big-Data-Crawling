# CoinTicker IR 대시보드

## 📊 프로젝트 개요

코인티커(CoinTicker) 프로젝트의 IR(Investor Relations) 발표용 대시보드입니다.
프로젝트 아키텍처, 성능, 데이터 파이프라인 등을 시각화하여 제공합니다.

## 📁 파일 구조

```
IR-dashboard/
├── IR/                         # 코인티커(CoinTicker) 대시보드
│   ├── index.html              # 메인 대시보드 (https://eieconcierge.com/cointicker/)
│   ├── demo.html               # 데모 페이지
│   ├── live-dashboard.html     # 실시간 대시보드
│   ├── architecture.html       # 아키텍처 다이어그램
│   ├── performance.html        # 성능 모니터링
│   ├── data-pipeline.html      # 데이터 파이프라인
│   └── dashboard.html          # 대시보드
├── static/                     # 정적 리소스 (CSS, JS)
└── README_PICU.md              # 프로젝트 설명서
```

## 🎯 주요 기능

### 코인티커(CoinTicker) 대시보드 (`/cointicker/`)

1. **메인 대시보드** (`index.html`)

   - 프로젝트 개요 및 주요 지표

2. **데모 페이지** (`demo.html`)

   - 인터랙티브 데모 및 기능 소개

3. **실시간 대시보드** (`live-dashboard.html`)

   - 실시간 데이터 모니터링

4. **아키텍처 다이어그램** (`architecture.html`)

   - 시스템 아키텍처 시각화

5. **성능 모니터링** (`performance.html`)

   - 성능 지표 및 분석

6. **데이터 파이프라인** (`data-pipeline.html`)

   - 데이터 흐름 및 파이프라인 시각화

7. **대시보드** (`dashboard.html`)
   - 통합 대시보드 뷰

## 🚀 사용 방법

### 배포된 사이트 접속

**코인티커 대시보드:**

- https://eieconcierge.com/cointicker/ (메인)
- https://eieconcierge.com/cointicker/demo.html
- https://eieconcierge.com/cointicker/live-dashboard.html
- https://eieconcierge.com/cointicker/architecture.html
- https://eieconcierge.com/cointicker/performance.html
- https://eieconcierge.com/cointicker/data-pipeline.html
- https://eieconcierge.com/cointicker/dashboard.html

### 로컬 개발

```bash
# Python 간단한 서버
python -m http.server 8000

# 브라우저에서 접속
# http://localhost:8000/IR/index.html
```

## 🎨 기술 스택

- HTML5
- CSS3
- JavaScript (ES6+)
- Chart.js

---

**Last Updated**: 2025년 10월 14일
