# Figma 프로젝트 + 기존 API 연동 통합 계획

## 📊 현재 상황

### ✅ Figma 프로젝트 (`Cryptocurrency Analytics Dashboard`)

- **완성된 UI**: Dashboard, News, Insights 페이지
- **기술 스택**: TypeScript, Tailwind CSS, Radix UI, Recharts
- **상태**: 목업 데이터만 사용 중, API 연동 없음

### ✅ 기존 frontend (`src/`)

- **API 연동**: `services/api.js` - 백엔드와 통신하는 핵심 코드
- **기본 컴포넌트**: 기본적인 UI만 있음
- **상태**: API 연동 구조는 완성, UI는 미완성

---

## 🎯 통합 전략

### **방법: Figma 프로젝트를 메인으로 사용 + API 연동 추가**

1. **Figma 프로젝트를 메인으로 사용** (완성된 UI)
2. **기존 `services/api.js`를 Figma 프로젝트로 이동**
3. **Figma 컴포넌트에 API 연동 추가**
4. **기존 frontend/src 폴더 삭제** (API 코드는 이미 이동됨)

---

## 📋 작업 순서

### Phase 1: API 연동 코드 이동

- [ ] `src/services/api.js` → `Cryptocurrency Analytics Dashboard/src/services/api.ts`로 복사
- [ ] TypeScript로 변환 (axios import 유지)
- [ ] API 타입 정의 추가

### Phase 2: Figma 컴포넌트에 API 연동

- [ ] `dashboard-page.tsx`: API에서 데이터 가져오기
- [ ] `news-page.tsx`: API에서 뉴스 가져오기
- [ ] `insights-page.tsx`: API에서 인사이트 가져오기
- [ ] 로딩/에러 상태 처리 추가

### Phase 3: Vite 설정 통합

- [ ] `vite.config.ts`에 API proxy 설정 추가
- [ ] 포트 동기화 설정 유지
- [ ] 환경 변수 설정

### Phase 4: 기존 frontend 정리

- [ ] `src/` 폴더 삭제 (API 코드는 이미 이동됨)
- [ ] `public/` 폴더는 유지 (정적 HTML 파일)
- [ ] `package.json` 통합

---

## 🔧 구체적 작업

### 1. API 서비스 파일 생성

**위치**: `Cryptocurrency Analytics Dashboard/src/services/api.ts`

```typescript
import axios from "axios";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:5000";

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    "Content-Type": "application/json",
  },
});

// ... 기존 api.js 내용을 TypeScript로 변환
```

### 2. Dashboard 컴포넌트 수정

**파일**: `dashboard-page.tsx`

```typescript
import { useState, useEffect } from "react";
import { dashboardAPI } from "../services/api";
// ... 기존 import

export function DashboardPage() {
  const [summary, setSummary] = useState(null);
  const [sentimentData, setSentimentData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [summaryData, sentimentTimeline] = await Promise.all([
        dashboardAPI.getSummary(),
        dashboardAPI.getSentimentTimeline(7),
      ]);
      setSummary(summaryData);
      setSentimentData(sentimentTimeline);
    } catch (err) {
      console.error("Failed to load dashboard data:", err);
    } finally {
      setLoading(false);
    }
  };

  // ... 기존 JSX에서 목업 데이터를 API 데이터로 교체
}
```

### 3. Vite 설정 수정

**파일**: `vite.config.ts`

```typescript
export default defineConfig({
  plugins: [react()],
  server: {
    port: parseInt(process.env.PORT || process.env.VITE_PORT || "3000", 10),
    proxy: {
      "/api": {
        target:
          process.env.VITE_API_BASE_URL ||
          `http://localhost:${process.env.BACKEND_PORT || "5000"}`,
        changeOrigin: true,
      },
    },
  },
  // ... 기존 설정
});
```

---

## 🗑️ 삭제할 파일/폴더

### 삭제 가능 (API 코드 이동 후)

- `src/components/` (기존 컴포넌트들)
- `src/pages/` (기존 페이지들)
- `src/index.css` (Figma 프로젝트에 있음)

### 유지해야 할 것

- `public/` 폴더 (정적 HTML 파일들)
- `vite.config.js` (참고용, Figma 프로젝트로 통합)
- `package.json` (의존성 확인용)

---

## ✅ 최종 구조

```
frontend/
├── Cryptocurrency Analytics Dashboard/  # 메인 프로젝트
│   ├── src/
│   │   ├── services/
│   │   │   └── api.ts                   # API 연동 (기존 api.js에서 이동)
│   │   ├── components/
│   │   │   ├── dashboard-page.tsx       # API 연동 추가
│   │   │   ├── news-page.tsx            # API 연동 추가
│   │   │   └── insights-page.tsx        # API 연동 추가
│   │   └── ...
│   ├── vite.config.ts                   # API proxy 설정 추가
│   └── package.json
├── public/                               # 정적 HTML 파일 (유지)
└── [기존 frontend/src 삭제]
```

---

## 🚀 실행 계획

1. **지금**: API 연동 코드를 Figma 프로젝트로 이동
2. **다음**: 컴포넌트에 API 연동 추가
3. **그 다음**: 테스트 및 검증
4. **마지막**: 기존 frontend/src 폴더 삭제

---

**결론: Figma 프로젝트를 메인으로 사용하고, 기존 API 연동 코드만 통합하면 됩니다! 🎯**
