# PICU 문서 디렉토리

> **PICU 프로젝트 문서 모음**

이 디렉토리는 PICU 프로젝트의 모든 문서를 논리적으로 분류하여 관리합니다.

---

## 📁 디렉토리 구조

```
PICU_docs/
├── README.md                    # 이 파일
│
├── guides/                      # 📖 사용자 가이드 및 실습 가이드
│   ├── GUI_GUIDE.md            # GUI 애플리케이션 사용 가이드
│   ├── INTEGRATION_GUIDE.md    # 시스템 통합 가이드
│   └── 실습통합클러스터구성.md  # 클러스터 구성 실습 가이드
│
├── architecture/                # 🏗️ 아키텍처 및 설계 문서
│   ├── 파이프라인_ 아키텍처_설계.md
│   └── [코드]코인티커변경설계.md
│
├── analysis/                    # 📊 분석 및 리뷰 문서
│   ├── COMPREHENSIVE_ANALYSIS.md      # 프로젝트 종합 분석
│   ├── GUI_CONFIGURATION_ANALYSIS.md  # GUI 설정 분석
│   └── DEVELOPMENT_REVIEW.md         # 개발 리뷰
│
├── planning/                    # 📅 계획 및 로드맵
│   └── DEVELOPMENT_ROADMAP.md  # 개발 로드맵
│
├── reference/                   # 📚 참고 문서 및 종합 설명서
│   ├── PROJECT_DOCUMENTATION.md                    # 프로젝트 문서
│   └── 코인티커(CoinTicker)_프로젝트 종합 설명서.md # 종합 설명서
│
├── strategy/                    # 🎯 전략 문서
│   └── FRONTEND_STRATEGY.md     # 프론트엔드 전략
│
└── troubleshooting/             # 🔧 문제해결 및 디버깅 문서
    ├── HDFS_LOGIC_REVIEW.md     # HDFS 프로세스 흐름 논리적 검토
    └── HDFS_PROCESS_FLOW_ANALYSIS.md  # HDFS 프로세스 흐름 분석 및 문제점
```

---

## 📖 각 디렉토리 설명

### `guides/` - 사용자 가이드 및 실습 가이드

**목적**: 사용자가 시스템을 사용하고 설정하는 방법을 안내하는 문서

- **GUI_GUIDE.md**: GUI 애플리케이션 설치, 실행, 사용 방법
- **INTEGRATION_GUIDE.md**: 시스템 통합 및 연동 가이드
- **실습통합클러스터구성.md**: 클러스터 구성 실습 가이드

**대상 독자**: 개발자, 시스템 관리자, 사용자

---

### `architecture/` - 아키텍처 및 설계 문서

**목적**: 시스템 아키텍처, 설계 결정, 기술적 구조를 설명하는 문서

- **파이프라인* 아키텍처*설계.md**: 데이터 파이프라인 아키텍처 설계
- **[코드]코인티커변경설계.md**: 코드 변경 및 리팩토링 설계

**대상 독자**: 개발자, 아키텍트, 기술 리더

---

### `analysis/` - 분석 및 리뷰 문서

**목적**: 프로젝트 상태 분석, 코드 리뷰, 개선 사항 분석

- **COMPREHENSIVE_ANALYSIS.md**: 프로젝트 전역 종합 분석
- **GUI_CONFIGURATION_ANALYSIS.md**: GUI 설정 완전성 분석
- **DEVELOPMENT_REVIEW.md**: 개발 진행 상황 리뷰

**대상 독자**: 프로젝트 관리자, 개발 리더, 품질 관리자

---

### `planning/` - 계획 및 로드맵

**목적**: 프로젝트 계획, 일정, 우선순위, 로드맵

- **DEVELOPMENT_ROADMAP.md**: 개발 로드맵 및 단계별 계획

**대상 독자**: 프로젝트 관리자, 개발 팀, 이해관계자

---

### `reference/` - 참고 문서 및 종합 설명서

**목적**: 프로젝트 전체 개요, 참고 자료, 종합 설명서

- **PROJECT_DOCUMENTATION.md**: 프로젝트 전체 문서
- **코인티커(CoinTicker)\_프로젝트 종합 설명서.md**: 프로젝트 종합 설명서

**대상 독자**: 모든 이해관계자, 신규 팀원, 프로젝트 개요가 필요한 사람

---

### `strategy/` - 전략 문서

**목적**: 기술 전략, 개발 전략, 비즈니스 전략

- **FRONTEND_STRATEGY.md**: 프론트엔드 개발 전략

**대상 독자**: 기술 리더, 아키텍트, 전략 수립자

---

### `troubleshooting/` - 문제해결 및 디버깅 문서

**목적**: 발생한 문제점 분석, 디버깅 과정, 해결 방법 문서화

- **HDFS_LOGIC_REVIEW.md**: HDFS 프로세스 흐름 논리적 검토 및 개선사항
- **HDFS_PROCESS_FLOW_ANALYSIS.md**: HDFS 프로세스 흐름 분석 및 발견된 문제점과 수정 방안

**대상 독자**: 개발자, 디버깅 담당자, 문제 해결 담당자

---

## 🚀 빠른 시작

### 처음 시작하는 경우

1. **프로젝트 개요**: `reference/PROJECT_DOCUMENTATION.md` 또는 `reference/코인티커(CoinTicker)_프로젝트 종합 설명서.md`
2. **시작 가이드**: `guides/GUI_GUIDE.md` 또는 `guides/INTEGRATION_GUIDE.md`
3. **아키텍처 이해**: `architecture/파이프라인_ 아키텍처_설계.md`

### 개발자를 위한 문서

1. **아키텍처**: `architecture/` 디렉토리
2. **통합 가이드**: `guides/INTEGRATION_GUIDE.md`
3. **개발 로드맵**: `planning/DEVELOPMENT_ROADMAP.md`

### 관리자를 위한 문서

1. **프로젝트 분석**: `analysis/COMPREHENSIVE_ANALYSIS.md`
2. **개발 리뷰**: `analysis/DEVELOPMENT_REVIEW.md`
3. **로드맵**: `planning/DEVELOPMENT_ROADMAP.md`

---

## 📝 문서 작성 가이드

### 문서 분류 기준

- **guides/**: "어떻게 사용하는가?" - 사용 방법, 설정 방법, 실습
- **architecture/**: "어떻게 설계되었는가?" - 구조, 설계 결정
- **analysis/**: "현재 상태는?" - 분석, 리뷰, 평가
- **planning/**: "앞으로 어떻게 할 것인가?" - 계획, 로드맵
- **reference/**: "무엇인가?" - 개요, 설명서, 참고 자료
- **strategy/**: "왜 그렇게 하는가?" - 전략, 방향성
- **troubleshooting/**: "문제는 무엇이고 어떻게 해결했는가?" - 문제 분석, 디버깅, 해결 방법

### 새 문서 추가 시

1. 문서의 목적과 대상 독자를 명확히 하기
2. 적절한 디렉토리에 배치
3. 이 README.md에 추가 정보 업데이트

---

## 🔄 문서 업데이트 이력

- **2025-01-27**: 디렉토리 구조 재구성 및 분류 체계 정립
- **2025-01-27**: troubleshooting 디렉토리 추가 및 HDFS 문제해결 문서 이동

---

## 📞 문의

문서 관련 문의사항이나 개선 제안은 프로젝트 관리자에게 문의하세요.

---

**최종 업데이트**: 2025-01-27
