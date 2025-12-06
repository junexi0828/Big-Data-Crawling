# 프론트엔드 통합 전략

## 📊 현재 상황 분석

### 1. 기존 프론트엔드 프로젝트

#### A. `picu-dashboard/` (PICU 프로젝트)

- **목적**: 동아리 관리 플랫폼 재무 분석
- **기술**: 순수 HTML/CSS/JavaScript, Chart.js
- **기능**:
  - 재무 시뮬레이션 (36개월 전망)
  - 투자 인사이트 대시보드 (ROI, IRR, CAC 등)
  - 시나리오 분석 (보수/기본/낙관)
- **특징**: ✅ 완성도 높음, 정적 데이터, 비즈니스 분석 중심
- **상태**: 독립 프로젝트 (CoinTicker와 무관)

#### B. `cointicker/frontend/public/` (CoinTicker 소개 페이지)

- **목적**: CoinTicker 프로젝트 소개 및 데모
- **기술**: 순수 HTML/CSS/JavaScript, Chart.js
- **기능**:
  - 프로젝트 소개 (`index.html`)
  - 아키텍처 설명 (`architecture.html`)
  - 성과 분석 (`performance.html`)
  - 데이터 파이프라인 (`data-pipeline.html`)
  - 실시간 대시보드 데모 (`live-dashboard.html`, `demo.html`)
- **특징**: ✅ 완성도 높음, 정적 소개 페이지, 데모용
- **상태**: CoinTicker 프로젝트의 마케팅/소개용

#### C. 새로 만든 React 프론트엔드 (`cointicker/frontend/src/`)

- **목적**: CoinTicker 백엔드 API와 연동하는 동적 대시보드
- **기술**: React 18, Vite, Chart.js, Axios
- **기능**:
  - 실시간 데이터 연동 (FastAPI 백엔드)
  - 대시보드 (요약, 감성 분석 차트)
  - 뉴스 목록
  - 인사이트 목록
  - 설정 페이지
- **특징**: ✅ 백엔드 연동, 실시간 업데이트, 모던 스택
- **상태**: 새로 개발됨, 백엔드와 연동 필요

---

## 🎯 통합 전략 제안

### **방안 1: 하이브리드 접근 (권장) ⭐**

#### 구조

```
cointicker/frontend/
├── public/                    # 정적 소개 페이지 (기존 유지)
│   ├── index.html            # 프로젝트 소개 (기존)
│   ├── architecture.html     # 아키텍처 설명 (기존)
│   ├── performance.html      # 성과 분석 (기존)
│   ├── data-pipeline.html    # 파이프라인 설명 (기존)
│   ├── live-dashboard.html   # 실시간 대시보드 데모 (기존)
│   └── demo.html             # 데모 (기존)
│
└── src/                      # React 앱 (새로 개발)
    ├── pages/
    │   ├── Dashboard.jsx     # 실시간 대시보드 (API 연동)
    │   ├── News.jsx          # 뉴스 (API 연동)
    │   ├── Insights.jsx      # 인사이트 (API 연동)
    │   └── Settings.jsx      # 설정
    └── ...
```

#### 장점

1. ✅ **기존 소개 페이지 유지**: 마케팅/프레젠테이션용
2. ✅ **React 앱 추가**: 실제 운영용 동적 대시보드
3. ✅ **명확한 역할 분리**: 소개 vs 운영
4. ✅ **점진적 마이그레이션 가능**: 필요시 소개 페이지도 React로 전환

#### 라우팅 구조

```
/                    → public/index.html (프로젝트 소개)
/about               → public/architecture.html
/performance         → public/performance.html
/demo                → public/demo.html
/app                 → React 앱 (실제 대시보드)
/app/dashboard       → React Dashboard
/app/news            → React News
/app/insights        → React Insights
```

---

### **방안 2: React로 완전 통합**

#### 구조

```
cointicker/frontend/
└── src/
    ├── pages/
    │   ├── Home.jsx              # 프로젝트 소개 (기존 index.html 변환)
    │   ├── Architecture.jsx      # 아키텍처 (기존 architecture.html 변환)
    │   ├── Performance.jsx      # 성과 분석 (기존 performance.html 변환)
    │   ├── Dashboard.jsx        # 실시간 대시보드 (API 연동)
    │   ├── News.jsx             # 뉴스 (API 연동)
    │   └── Insights.jsx         # 인사이트 (API 연동)
    └── ...
```

#### 장점

1. ✅ **단일 기술 스택**: React로 통일
2. ✅ **코드 재사용**: 컴포넌트 공유
3. ✅ **일관된 UX**: 통일된 디자인 시스템

#### 단점

1. ❌ **작업량 증가**: 기존 HTML을 React로 변환 필요
2. ❌ **기존 완성도 높은 페이지 재작업**: 시간 소요

---

### **방안 3: 기존 HTML 유지 + React 앱 분리**

#### 구조

```
cointicker/
├── frontend-static/              # 정적 소개 페이지
│   └── public/                  # 기존 HTML 파일들
│
└── frontend/                     # React 앱
    └── src/                     # 새로 개발한 React 코드
```

#### 장점

1. ✅ **완전 분리**: 역할이 명확
2. ✅ **독립 배포**: 각각 다른 도메인/경로에 배포 가능

#### 단점

1. ❌ **관리 복잡도 증가**: 두 개의 프론트엔드 프로젝트
2. ❌ **코드 중복 가능성**: 공통 컴포넌트/스타일

---

## 💡 최종 권장안: **방안 1 (하이브리드 접근)**

### 이유

1. **기존 투자 보존**: 완성도 높은 소개 페이지 유지
2. **실용성**: 실제 운영은 React 앱으로
3. **유연성**: 필요시 점진적 통합 가능
4. **명확한 역할**: 소개 vs 운영 분리

### 구현 계획

#### 1단계: 현재 상태 유지

- `public/` 폴더의 기존 HTML 파일 유지
- `src/` 폴더의 React 앱 개발 완료

#### 2단계: 라우팅 통합

```javascript
// vite.config.js에 rewrites 추가
export default defineConfig({
  // ... 기존 설정
  server: {
    proxy: {
      "/api": "http://localhost:5000",
    },
  },
  // 정적 파일 서빙
  publicDir: "public",
});
```

#### 3단계: 네비게이션 통합

- React 앱에 "소개" 메뉴 추가 → `/` (public/index.html)
- 소개 페이지에 "실시간 대시보드" 링크 추가 → `/app`

#### 4단계: (선택) 점진적 마이그레이션

- 필요시 소개 페이지도 React 컴포넌트로 변환
- 하지만 급하게 할 필요 없음

---

## 📋 구체적 작업 계획

### 즉시 작업

1. ✅ React 앱 완성 (이미 완료)
2. ✅ 기존 `public/` 파일 유지
3. ⏳ Vite 설정으로 정적 파일 서빙 확인

### 향후 개선

1. React 앱에 "프로젝트 소개" 페이지 추가 (기존 index.html 참고)
2. 소개 페이지에서 React 앱으로 이동하는 링크 추가
3. 공통 디자인 시스템 구축 (선택)

---

## 🎨 디자인 통합 제안

### 공통 디자인 요소

- **색상 팔레트**: 기존 CoinTicker 브랜드 색상 유지
  - Primary: `#1e3c72`, `#2a5298`, `#7e22ce`
  - Accent: `#f0b90b`
- **타이포그래피**: Pretendard 폰트 계열
- **차트 스타일**: Chart.js 통일

### React 앱 스타일 조정

현재 React 앱은 다크 테마 (`#0b0e11`)를 사용 중이지만, 기존 소개 페이지는 라이트 테마입니다.

**옵션 1**: React 앱도 라이트 테마로 변경 (일관성)
**옵션 2**: React 앱은 다크 테마 유지 (실시간 대시보드 느낌)
**옵션 3**: 테마 전환 기능 추가 (사용자 선택)

---

## ✅ 결론

**권장 방향**: **방안 1 (하이브리드 접근)**

1. 기존 `public/` 폴더의 HTML 파일은 **그대로 유지** (소개/프레젠테이션용)
2. 새로 만든 React 앱은 **실제 운영용 대시보드**로 사용
3. 두 가지를 **공존**시키되, 명확한 역할 분리
4. 필요시 점진적으로 통합 가능

이 방식이 **가장 실용적이고 효율적**입니다! 🚀
