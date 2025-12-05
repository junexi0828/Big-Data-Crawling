# HTML → React 컴포넌트 통합 계획

## 📋 현재 상황

### ✅ React 앱에 있는 페이지

- Dashboard (대시보드)
- News (뉴스)
- Insights (인사이트)

### 📄 `public/` 폴더의 정적 HTML 파일들

#### 🔄 React로 변환할 페이지 (데이터/기능 중심)

1. **demo.html** - 데모 플랫폼

   - 실시간 뉴스 속보 (필터링 기능)
   - 투자 인사이트 (암호화폐 검색)
   - 주요 정부 일정
   - **→ React 컴포넌트로 변환**

2. **dashboard.html** - 통합 대시보드

   - 실시간 시장 심리 & 기술적 지표
   - 뉴스 감성 분석
   - 지지선/저항선 클러스터
   - 실시간 알림
   - **→ React 컴포넌트로 변환**

3. **live-dashboard.html** - 실시간 트레이딩 대시보드
   - Chart.js 기반 차트
   - 실시간 가격 데이터
   - 기술적 지표
   - **→ React 컴포넌트로 변환**

#### 🔗 외부 링크로 연결할 페이지 (기업소개/설명)

4. **architecture.html** - 시스템 아키텍처 설명

   - 기업소개 내용
   - **→ 외부 링크 연결**: `https://eieconcierge.com/cointicker/architecture.html`

5. **performance.html** - 성과 분석

   - 기업소개 내용
   - **→ 외부 링크 연결**: `https://eieconcierge.com/cointicker/performance.html`

6. **data-pipeline.html** - 데이터 파이프라인 설명
   - 기업소개 내용
   - **→ 외부 링크 연결**: `https://eieconcierge.com/cointicker/data-pipeline.html`

---

## 🎯 통합 전략

### 방법 1: 데이터/기능 페이지 → React 컴포넌트 변환

1. **HTML 파일의 데이터 구조와 기능만 추출**

   - 데이터 구조 파악 (뉴스, 인사이트, 차트 데이터 등)
   - 기능 로직 추출 (필터링, 검색, 차트 렌더링 등)
   - HTML 구조 → JSX
   - 인라인 CSS → Tailwind CSS 클래스
   - 정적 데이터 → React state/props + API 연동

2. **App.tsx에 라우팅 추가**

   - Navigation에 새 메뉴 항목 추가
   - 페이지 컴포넌트 추가

### 방법 2: 기업소개 페이지 → 외부 링크 연결

1. **Navigation에 "About" 또는 "회사소개" 섹션 추가**
2. **외부 링크로 연결**

   - Architecture → `https://eieconcierge.com/cointicker/architecture.html`
   - Performance → `https://eieconcierge.com/cointicker/performance.html`
   - Data Pipeline → `https://eieconcierge.com/cointicker/data-pipeline.html`

3. **통합 후 `public/` 폴더 삭제** (기업소개 페이지는 Vercel에 그대로 유지)

---

## 📝 작업 순서

### Phase 1: 데이터/기능 페이지 컴포넌트 생성

- [ ] `DemoPage.tsx` - 데모 플랫폼

  - [ ] 실시간 뉴스 속보 컴포넌트 (필터링 기능)
  - [ ] 투자 인사이트 컴포넌트 (암호화폐 검색)
  - [ ] 주요 정부 일정 컴포넌트
  - [ ] API 연동 (newsAPI, insightsAPI)

- [ ] `LiveDashboardPage.tsx` - 실시간 대시보드

  - [ ] 실시간 시장 심리 & 기술적 지표
  - [ ] 뉴스 감성 분석 차트
  - [ ] 지지선/저항선 클러스터
  - [ ] 실시간 알림
  - [ ] Chart.js 통합

- [ ] `TradingDashboardPage.tsx` - 실시간 트레이딩 대시보드
  - [ ] Chart.js 캔들스틱 차트
  - [ ] 볼린저 밴드
  - [ ] 거래량 차트
  - [ ] 기술적 지표 (RSI, MACD, ADX 등)
  - [ ] 실시간 가격 업데이트

### Phase 2: Navigation 업데이트

- [ ] Navigation 컴포넌트에 새 메뉴 항목 추가
  - [ ] Demo (데모 플랫폼)
  - [ ] Live Dashboard (실시간 대시보드)
  - [ ] Trading Dashboard (트레이딩 대시보드)
- [ ] "About" 섹션 추가 (드롭다운 또는 별도 메뉴)
  - [ ] Architecture (외부 링크)
  - [ ] Performance (외부 링크)
  - [ ] Data Pipeline (외부 링크)
- [ ] 아이콘 추가

### Phase 3: App.tsx 업데이트

- [ ] 새 페이지 컴포넌트 import
- [ ] 라우팅 로직 추가
- [ ] 페이지 상태 타입 확장

### Phase 4: 스타일링

- [ ] HTML의 인라인 CSS를 Tailwind CSS로 변환
- [ ] 다크 테마에 맞게 색상 조정
- [ ] 반응형 디자인 적용

---

## 🎨 디자인 통합 방향

### 기존 HTML 스타일

- 밝은 그라데이션 배경 (#1e3c72 → #2a5298 → #7e22ce)
- 흰색 카드 배경
- 큰 제목과 섹션 구분

### React 앱 스타일

- 다크 테마 (#0b0e11 배경)
- 카드 배경 (#1e2329)
- 보라색 액센트 (#667eea)

### 통합 방향

- **데이터/기능 페이지**: 다크 테마로 변환하여 React 앱과 일관성 유지
- **기업소개 페이지**: 외부 링크로 연결하므로 기존 스타일 유지

---

## 📂 파일 구조

```
Cryptocurrency Analytics Dashboard/src/
├── components/
│   ├── demo-page.tsx                    # 새로 생성 (데이터/기능)
│   ├── live-dashboard-page.tsx          # 새로 생성 (데이터/기능)
│   ├── trading-dashboard-page.tsx      # 새로 생성 (데이터/기능)
│   ├── dashboard-page.tsx              # 기존
│   ├── news-page.tsx                    # 기존
│   ├── insights-page.tsx                # 기존
│   └── navigation.tsx                   # 업데이트 필요 (외부 링크 추가)
└── App.tsx                              # 업데이트 필요
```

### 외부 링크 (Vercel에 유지)

- `https://eieconcierge.com/cointicker/architecture.html`
- `https://eieconcierge.com/cointicker/performance.html`
- `https://eieconcierge.com/cointicker/data-pipeline.html`

---

## 🔧 구현 예시

### DemoPage.tsx 구조

```typescript
import { useState, useEffect } from "react";
import { newsAPI, insightsAPI } from "../services/api";

export function DemoPage() {
  const [news, setNews] = useState([]);
  const [filter, setFilter] = useState("all");
  const [selectedCoin, setSelectedCoin] = useState(null);

  useEffect(() => {
    // 뉴스 데이터 로드
    newsAPI.getLatest(20).then(setNews);
  }, []);

  return (
    <div className="space-y-6">
      <div className="text-center text-white py-8">
        <h1 className="text-4xl font-bold mb-2">🎯 CoinTicker Demo Platform</h1>
        <p className="text-xl opacity-90">
          AI 기반 투자 인사이트 & 실시간 뉴스 분석
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 실시간 뉴스 속보 */}
        <div className="bg-[#1e2329] rounded-2xl p-6">
          <h2 className="text-2xl font-bold mb-4">📰 실시간 뉴스 속보</h2>
          {/* 필터 버튼 */}
          {/* 뉴스 리스트 */}
        </div>

        {/* 투자 인사이트 */}
        <div className="bg-[#1e2329] rounded-2xl p-6">
          <h2 className="text-2xl font-bold mb-4">💡 투자 인사이트</h2>
          {/* 암호화폐 검색 */}
          {/* 종목 그리드 */}
          {/* 인사이트 패널 */}
        </div>
      </div>

      {/* 주요 정부 일정 */}
      <div className="bg-[#1e2329] rounded-2xl p-6">
        <h2 className="text-2xl font-bold mb-4">🏛️ 주요 정부 일정</h2>
        {/* 일정 탭 및 리스트 */}
      </div>
    </div>
  );
}
```

### LiveDashboardPage.tsx 구조

```typescript
import { useState, useEffect } from "react";
import { dashboardAPI } from "../services/api";
import { Line, Bar } from "react-chartjs-2";

export function LiveDashboardPage() {
  const [marketData, setMarketData] = useState(null);
  const [sentimentData, setSentimentData] = useState(null);

  useEffect(() => {
    // 실시간 데이터 로드
    dashboardAPI.getSummary().then(setMarketData);
    dashboardAPI.getSentimentTimeline(24).then(setSentimentData);
  }, []);

  return (
    <div className="space-y-6">
      {/* 대시보드 헤더 */}
      <div className="bg-gradient-to-r from-[#667eea] to-[#764ba2] rounded-2xl p-6 text-white">
        <h1 className="text-3xl font-bold">
          ETHUSDT 실시간 시장 심리 & 기술적 지표 통합 대시보드
        </h1>
        <p className="opacity-90">{new Date().toLocaleString()}</p>
      </div>

      {/* 통계 카드 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {/* 현재가, 공포탐욕지수, 거래량, 뉴스감성점수 */}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 뉴스 감성 분석 */}
        <div className="bg-[#1e2329] rounded-2xl p-6">
          <h2 className="text-2xl font-bold mb-4">📰 뉴스 감성 분석</h2>
          {/* 감성 차트 */}
        </div>

        {/* 기술적 지표 */}
        <div className="bg-[#1e2329] rounded-2xl p-6">
          <h2 className="text-2xl font-bold mb-4">📊 기술적 지표 라이브</h2>
          {/* 지표 리스트 */}
        </div>
      </div>

      {/* 지지선/저항선 클러스터 & 실시간 알림 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 지지선/저항선 */}
        {/* 실시간 알림 */}
      </div>
    </div>
  );
}
```

### Navigation.tsx 업데이트 (외부 링크 추가)

```typescript
export function Navigation({ currentPage, onNavigate }: NavigationProps) {
  const navItems = [
    { id: "dashboard" as const, label: "Dashboard", icon: LayoutDashboard },
    { id: "news" as const, label: "News", icon: Newspaper },
    { id: "insights" as const, label: "Insights", icon: Lightbulb },
    { id: "demo" as const, label: "Demo", icon: Play },
    { id: "live-dashboard" as const, label: "Live", icon: Activity },
  ];

  const aboutLinks = [
    {
      label: "Architecture",
      url: "https://eieconcierge.com/cointicker/architecture.html",
    },
    {
      label: "Performance",
      url: "https://eieconcierge.com/cointicker/performance.html",
    },
    {
      label: "Data Pipeline",
      url: "https://eieconcierge.com/cointicker/data-pipeline.html",
    },
  ];

  return (
    <nav>
      {/* 메인 네비게이션 */}
      <div className="flex gap-2">
        {navItems.map((item) => (
          <button onClick={() => onNavigate(item.id)}>{item.label}</button>
        ))}
      </div>

      {/* About 드롭다운 */}
      <DropdownMenu>
        <DropdownMenuTrigger>About</DropdownMenuTrigger>
        <DropdownMenuContent>
          {aboutLinks.map((link) => (
            <a href={link.url} target="_blank" rel="noopener noreferrer">
              {link.label}
            </a>
          ))}
        </DropdownMenuContent>
      </DropdownMenu>
    </nav>
  );
}
```

### App.tsx 업데이트

```typescript
type Page =
  | "dashboard"
  | "news"
  | "insights"
  | "demo"
  | "live-dashboard"
  | "trading-dashboard";

export default function App() {
  const [currentPage, setCurrentPage] = useState<Page>("dashboard");

  return (
    <div className="min-h-screen bg-[#0b0e11]">
      <Navigation currentPage={currentPage} onNavigate={setCurrentPage} />
      <main className="max-w-[1440px] mx-auto px-5 lg:px-8 py-8">
        {currentPage === "dashboard" && <DashboardPage />}
        {currentPage === "news" && <NewsPage />}
        {currentPage === "insights" && <InsightsPage />}
        {currentPage === "demo" && <DemoPage />}
        {currentPage === "live-dashboard" && <LiveDashboardPage />}
        {currentPage === "trading-dashboard" && <TradingDashboardPage />}
      </main>
    </div>
  );
}
```

---

## ✅ 완료 후 작업

1. **테스트**

   - 모든 페이지 정상 작동 확인
   - 네비게이션 확인
   - 외부 링크 연결 확인
   - 반응형 디자인 확인
   - API 연동 확인

2. **public 폴더 정리**
   ```bash
   # 데이터/기능 페이지는 React로 변환했으므로 삭제
   # 기업소개 페이지는 Vercel에 유지 (외부 링크로 사용)
   rm -rf frontend/public/demo.html
   rm -rf frontend/public/dashboard.html
   rm -rf frontend/public/live-dashboard.html
   # architecture.html, performance.html, data-pipeline.html은 Vercel에 유지
   ```

---

## 📌 핵심 포인트

### ✅ React로 변환할 것

- **데이터 구조**: 뉴스, 인사이트, 차트 데이터
- **기능 로직**: 필터링, 검색, 차트 렌더링
- **인터랙티브 요소**: 버튼, 입력, 실시간 업데이트

### 🔗 외부 링크로 연결할 것

- **기업소개 내용**: Architecture, Performance, Data Pipeline
- **정적 설명 페이지**: Vercel에 그대로 유지

### 🎯 우선순위

1. **Demo Page** - 가장 많은 기능 포함 (뉴스, 인사이트, 정부 일정)
2. **Live Dashboard Page** - 실시간 데이터 시각화
3. **Trading Dashboard Page** - Chart.js 통합

---

**다음 단계: Demo Page부터 시작할까요?**
