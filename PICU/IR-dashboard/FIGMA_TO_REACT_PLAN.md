# Figma 디자인 → React 구현 계획

## 📊 현재 상황 분석

### ✅ 이미 구현된 것

- React 기본 구조 (App.jsx, 라우팅)
- 기본 컴포넌트 (SummaryCards, SentimentChart, MarketOverview)
- API 연동 구조 (services/api.js)
- 기본 다크 테마 스타일

### ❌ 부족한 것 (Figma 디자인 기준)

1. **Dashboard 페이지**

   - Fear & Greed Index 게이지 차트
   - Top 5 Volume Coins 테이블
   - Latest Insights 사이드바
   - 상세한 카드 스타일링
   - 트렌드 인디케이터 (↑↓)

2. **News 페이지**

   - 필터링 UI (Source, Date range, Sentiment)
   - 상세한 뉴스 카드 디자인
   - 감성 배지/태그
   - 키워드 칩
   - 페이지네이션

3. **Insights 페이지**

   - 심각도 필터 (High/Medium/Low)
   - Symbol 필터
   - Type 필터
   - 상세한 인사이트 카드 디자인
   - Dismiss 기능

4. **공통**
   - 디자인 시스템 (색상, 타이포그래피, 간격)
   - 반응형 디자인
   - 로딩/에러/빈 상태 UI
   - 호버/액티브 상태

---

## 🎯 권장 접근 방법

### ✅ **옵션 1: 현재 Figma 디자인으로 직접 구현 (추천)**

**이유:**

- Figma 디자인이 이미 충분히 상세하고 완성도가 높음
- 3개 페이지 (Dashboard, News, Insights) 모두 커버됨
- 추가 디자인 요청 불필요

**작업 순서:**

1. Figma 디자인 시스템 추출 (색상, 폰트, 간격)
2. 공통 컴포넌트 구현 (Card, Badge, Button, Filter 등)
3. Dashboard 페이지 상세 구현
4. News 페이지 상세 구현
5. Insights 페이지 상세 구현
6. 반응형 디자인 적용

---

### ❌ 옵션 2: Figma AI에게 더 요청 (비추천)

**이유:**

- 현재 디자인으로 충분함
- 추가 요청 시 일관성 문제 가능
- 개발 시간 지연

**필요한 경우에만:**

- Settings 페이지 디자인
- 모바일 전용 레이아웃
- 추가 차트 타입

---

## 📋 구현 작업 체크리스트

### Phase 1: 디자인 시스템 구축

- [ ] 색상 팔레트 정의 (CSS 변수)
- [ ] 타이포그래피 시스템
- [ ] 간격 시스템 (20px 그리드)
- [ ] 공통 컴포넌트 스타일 (Card, Button, Badge)

### Phase 2: Dashboard 페이지

- [ ] SummaryCards 스타일링 (Figma 기준)
- [ ] Fear & Greed Index 게이지 컴포넌트
- [ ] Top 5 Volume Coins 테이블 컴포넌트
- [ ] Sentiment Timeline 차트 개선
- [ ] Latest Insights 사이드바
- [ ] 트렌드 인디케이터 (↑↓) 추가

### Phase 3: News 페이지

- [ ] 필터 UI (Source, Date, Sentiment)
- [ ] 뉴스 카드 디자인 개선
- [ ] 감성 배지/태그
- [ ] 키워드 칩
- [ ] 페이지네이션 또는 무한 스크롤

### Phase 4: Insights 페이지

- [ ] 필터 UI (Severity, Symbol, Type)
- [ ] 인사이트 카드 디자인 개선
- [ ] Dismiss 기능
- [ ] Generate 버튼 스타일링

### Phase 5: 공통 개선

- [ ] 로딩 상태 (스켈레톤 스크린)
- [ ] 에러 상태 UI
- [ ] 빈 상태 UI
- [ ] 반응형 디자인 (모바일, 태블릿)
- [ ] 접근성 개선 (키보드 네비게이션, ARIA)

---

## 🎨 Figma 디자인에서 추출할 요소

### 색상 팔레트

```css
:root {
  /* Background */
  --bg-primary: #0b0e11;
  --bg-secondary: #1e2329;
  --bg-card: #1e2329;
  --border: #2b3139;

  /* Accent */
  --primary: #667eea;
  --primary-gradient: linear-gradient(135deg, #667eea, #764ba2);
  --accent-gold: #f0b90b;

  /* Status */
  --positive: #43e97b;
  --negative: #ff6b6b;

  /* Text */
  --text-primary: #eaecef;
  --text-secondary: #848e9c;
}
```

### 타이포그래피

- H1: 2.5em, bold, #eaecef
- H2: 2em, semibold, #eaecef
- H3: 1.5em, semibold, #eaecef
- Body: 1em, regular, #848e9c
- Small: 0.875em, regular, #848e9c

### 간격 시스템

- 20px 그리드 시스템
- 카드 패딩: 20px
- 섹션 간격: 40px

---

## 🚀 즉시 시작 가능한 작업

### 1. 디자인 시스템 CSS 파일 생성

```bash
src/styles/
├── design-system.css    # 색상, 타이포그래피, 간격
├── components.css       # 공통 컴포넌트 스타일
└── utilities.css        # 유틸리티 클래스
```

### 2. 공통 컴포넌트 구현

```bash
src/components/common/
├── Card.jsx
├── Badge.jsx
├── Button.jsx
├── Filter.jsx
└── Loading.jsx
```

### 3. Dashboard 컴포넌트 개선

```bash
src/components/dashboard/
├── FearGreedIndex.jsx    # 새로 추가
├── VolumeCoinsTable.jsx   # 새로 추가
└── LatestInsights.jsx     # 새로 추가
```

---

## 💡 추천 워크플로우

1. **지금**: Figma 디자인을 참고하여 디자인 시스템 구축
2. **다음**: Dashboard 페이지부터 상세 구현
3. **그 다음**: News, Insights 순서로 구현
4. **마지막**: 반응형 및 접근성 개선

---

## ❓ 결정 필요 사항

1. **Chart 라이브러리**: Chart.js vs Recharts vs 다른 것?
2. **아이콘**: Emoji vs React Icons vs 다른 것?
3. **상태 관리**: Context API vs Zustand vs 다른 것?
4. **스타일링**: CSS Modules vs Styled Components vs Tailwind?

---

**결론: 현재 Figma 디자인으로 바로 구현 시작하는 것을 추천합니다! 🚀**
