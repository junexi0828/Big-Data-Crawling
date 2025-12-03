# PICU - 올인원 동아리 관리 플랫폼 설명회 HTML 웹사이트

## 📊 프로젝트 개요

PICU는 대학 동아리를 위한 올인원 관리 플랫폼의 재무 분석 및 투자 인사이트를 제공하는 프로젝트입니다.
해당 폴더는 플랫폼 설명회 전용 HTML 웹사이트 구성으로 이루어져있습니다.

## 📁 파일 구조

```
IR-dashboard/
├── index.html                  # 메인 페이지
├── investment_dashboard.html    # 투자 인사이트 대시보드
├── financeexpect.html          # 재무 시뮬레이션 대시보드
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

### 코인티커(CoinTicker) 대시보드 (`/IR/` 또는 `/cointicker/`)

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

### 재무 시뮬레이션 (`financeexpect.html`)

- 36개월 재무 전망 시뮬레이션
- 3가지 시나리오 분석 (보수적/기본/낙관적)
- 월별 수익 및 지출 추적
- 누적 현금 흐름 분석
- CSV 데이터 내보내기

### 투자 인사이트 대시보드 (`investment_dashboard.html`)

- Executive Summary
- 핵심 투자 지표 (ROI, IRR, CAC 등)
- 투자 하이라이트
- 리스크 평가 (HIGH/MEDIUM/LOW)
- 시나리오 비교 분석
- 투자 권장사항

## 💡 핵심 재무 지표

- **초기 투자금**: ₩1,064,000
- **월간 운영비**: ₩2,218,000
- **손익분기점**: 15개월
- **3년 후 연간 수익**: ₩75,000,000
- **ROI (3년)**: 71%
- **IRR**: 22%

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

**재무 및 투자 대시보드:**

- https://eieconcierge.com/investment-dashboard
- https://eieconcierge.com/finance-simulation

### 로컬 개발

```bash
# Python 간단한 서버
python -m http.server 8000

# 브라우저에서 접속
# http://localhost:8000/IR/index.html
# http://localhost:8000/investment_dashboard.html
# http://localhost:8000/financeexpect.html
```

## 📈 비즈니스 모델

### 1단계: B2C 광고 수익 (1-12개월)

- 사용자당 월 ₩3,000 광고 수익
- 목표: 12개월 내 5,000명 확보

### 2단계: B2B/B2G 구독 모델 (13개월~)

- B2B: 기업 채용 연계 (연 ₩50M 목표)
- B2G: 대학 공식 솔루션 (연 ₩25M 목표)

## ⚠️ 주요 리스크

1. **HIGH**: 시장 진입 리스크, B2B 전환 실패
2. **MEDIUM**: 운영 비용 증가, 기술적 확장성
3. **LOW**: 규제 및 법률, 팀 구성 리스크

## 🎨 기술 스택

- HTML5
- CSS3
- JavaScript (ES6+)
- Chart.js 3.9.1

## 📊 시나리오 비교

| 구분          | 보수적 | 기본    | 낙관적 |
| ------------- | ------ | ------- | ------ |
| 사용자 성장률 | 월 10% | 월 15%  | 월 20% |
| 손익분기점    | 미달성 | 15개월  | 12개월 |
| 3년 후 누적   | -₩15M  | +₩25M   | +₩65M  |
| 발생 확률     | 25%    | **50%** | 25%    |

## 💼 투자 권장사항

✅ **투자 추천: POSITIVE (긍정적)**

- 명확한 시장 니즈
- 낮은 초기 투자
- 빠른 손익분기점 (15개월)
- 확장 가능한 비즈니스 모델

## 📞 Contact

- 📧 Email: investment@clubmanagement.kr
- 📱 Phone: 02-XXXX-XXXX

## 📄 License

본 프로젝트는 재무 분석 및 투자 검토 목적으로 작성되었습니다.

---

**Last Updated**: 2025년 10월 14일
