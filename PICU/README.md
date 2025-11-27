# PICU 프로젝트

> **PICU**: Personal Investment & Cryptocurrency Understanding

## 📋 프로젝트 개요

PICU는 두 가지 주요 프로젝트로 구성되어 있습니다:

1. **PICU Dashboard** - 동아리 관리 플랫폼 재무 분석 대시보드
2. **CoinTicker** - 암호화폐 시장 동향 분석 및 실시간 대시보드 시스템

---

## 📁 디렉토리 구조

```
PICU/
├── picu-dashboard/          # PICU 대시보드 프로젝트
│   ├── index.html
│   ├── financeexpect.html
│   └── investment_dashboard.html
│
├── cointicker/              # 코인티커 프로젝트 (개발 중)
│   ├── worker-nodes/        # Scrapy 크롤러
│   ├── backend/             # FastAPI 백엔드
│   ├── frontend/            # React 프론트엔드
│   └── shared/              # 공통 라이브러리
│
└── PICU_docs/               # 프로젝트 문서
    ├── DEVELOPMENT_ROADMAP.md
    ├── DEVELOPMENT_ANALYSIS.md
    └── ...
```

---

## 🚀 빠른 시작

### CoinTicker GUI (권장)

```bash
# PICU 루트에서 통합 가상환경 설정
bash setup_venv.sh

# 가상환경 활성화
source venv/bin/activate

# GUI 실행
bash run_gui.sh
```

### CoinTicker CLI

```bash
cd cointicker
source venv/bin/activate
cd worker-nodes
scrapy crawl upbit_trends
```

### 설치 마법사

```bash
# PICU 루트에서
bash run_installer.sh
```

---

## 📚 문서

### 프로젝트 문서
- [GUI 통합 가이드](GUI_GUIDE.md) - GUI 애플리케이션 사용 가이드
- [코인티커 개발 로드맵](PICU_docs/DEVELOPMENT_ROADMAP.md)
- [코인티커 개발 흐름 분석](PICU_docs/DEVELOPMENT_ANALYSIS.md)

### CoinTicker 문서
- [CoinTicker README](cointicker/README.md)
- [빠른 시작 가이드](cointicker/QUICKSTART.md)
- [테스트 가이드](cointicker/TESTING_GUIDE.md)
