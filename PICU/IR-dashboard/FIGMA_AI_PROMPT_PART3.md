# Figma AI Design Prompt for CoinTicker Dashboard - Complete Version

## 전체 디자인 요청 (기본 구조 + 상세 컴포넌트)

이 프롬프트는 기본 구조와 상세 컴포넌트를 모두 포함합니다. Part 1과 Part 3의 내용을 통합하여 단독으로 사용 가능합니다.

---

## Core Prompt (Copy this to Figma AI)

```
Create a modern, professional cryptocurrency analytics dashboard UI design with the following specifications:

### Design System
- Dark theme with primary background: #0b0e11
- Secondary background: #1e2329
- Accent colors: #667eea (primary), #f0b90b (crypto gold), #43e97b (positive), #ff6b6b (negative)
- Typography: Modern sans-serif, clean and readable
- Border radius: 8-12px for cards, 20px for containers
- Spacing: 20px grid system
- Responsive design: Mobile-first, breakpoints at 768px, 1024px, 1440px

### Page 1: Main Dashboard
Layout: Single page with grid system

**Top Section - Summary Cards (4 cards in a row)**
- Card 1: Total News Count (Icon: 📰, Color: #667eea)
- Card 2: Average Sentiment Score (Icon: 😊, Color: #f093fb, with trend indicator ↑↓)
- Card 3: Recent Insights Count (Icon: 💡, Color: #4facfe)
- Card 4: Active Sources (Icon: 🔗, Color: #43e97b)

**Middle Section - Key Metrics (2 columns)**
- Left Column: Fear & Greed Index (see detailed specs below)
- Right Column: Top 5 Volume Coins (see detailed specs below)

**Bottom Section - Charts (2 columns)**
- Left Column: Sentiment Timeline Chart
  - Line chart with multiple lines (Positive: green, Neutral: gray, Negative: red)
  - X-axis: Time, Y-axis: Sentiment score (-1.0 to 1.0)
  - Time range selector: 24h / 7d / 30d
  - Tooltip on hover
- Right Column: Market Overview
  - Summary of top volume coins with visual representation

**Sidebar (Right side)**
- Latest Insights Preview (see detailed specs below)

### Page 2: News Page
Layout: List view with filters

**Header**
- Title: "Latest News"
- Refresh button
- Filter options (see detailed specs below)

**News List**
- Card-based layout (see detailed specs below)
- Pagination or infinite scroll
- Empty state: "No news available"

### Page 3: Insights Page
Layout: List view with actions

**Header**
- Title: "Investment Insights"
- Action buttons: "Generate New Insights", "Refresh"
- Filter options (see detailed specs below)

**Insights List**
- Card-based layout (see detailed specs below)
- Group by date or severity
- Empty state: "No insights available. Generate new insights?"

### Component Specifications

**Cards**
- Background: #1e2329
- Border: 1px solid #2b3139
- Padding: 20px
- Hover effect: Slight elevation, border color change
- Shadow: Subtle, dark

**Buttons**
- Primary: Gradient (#667eea to #764ba2)
- Secondary: #2b3139 background
- Hover: Brightness increase
- Disabled: 50% opacity
- Border radius: 8px
- Padding: 10px 20px

**Charts**
- Background: Transparent or #0b0e11
- Grid lines: #2b3139
- Text color: #848e9c
- Tooltip: Dark background (#1e2329)

**Badges/Tags**
- Rounded pills
- Small padding
- Color-coded by category
- Font size: 12-14px

**Typography Hierarchy**
- H1: 2.5em, bold, #eaecef
- H2: 2em, semibold, #eaecef
- H3: 1.5em, semibold, #eaecef
- Body: 1em, regular, #848e9c
- Small: 0.875em, regular, #848e9c

---

### Detailed Component Specifications

**1. Fear & Greed Index Gauge**

### 1. Fear & Greed Index Gauge
- Circular gauge: 300px × 300px
- Background: #1e2329, border: #2b3139
- Gauge arc colors by value:
  * 0-20 (Extreme Fear): #ff6b6b
  * 21-40 (Fear): #ffa94d
  * 41-60 (Neutral): #f0b90b
  * 61-80 (Greed): #43e97b
  * 81-100 (Extreme Greed): #69db7c
- Center: Large value (3em, bold), classification label below
- States: Loading (skeleton), Error (red border)

### 2. Top 5 Volume Coins Table
- Columns: Rank (badge), Symbol (1.5em bold), 24h Volume (monospace, abbreviated), 24h Change (% with ↑↓ icon)
- Styling: #1e2329 background, #2b3139 border, 12px radius
- Row hover: #2b3139 background, left border #667eea
- Header: #0b0e11 background, sortable with arrows
- Change colors: Positive #43e97b, Negative #ff6b6b

### 3. Latest Insights Sidebar
- Width: 320px, sticky right
- Header: "Latest Insights" + refresh button + count badge
- Insight cards: #0b0e11 background, 8px radius, 16px padding
- Each card: Severity badge + timestamp, Type label (uppercase, #667eea), Symbol badge, Description (2 lines max), Expand indicator
- Hover: Border #667eea

### 4. News Page Filters
- Filter bar: #1e2329 background, 12px radius, 20px padding
- Source filter: Multi-select chips (selected: #667eea, unselected: #2b3139)
- Date range: Dropdown (#2b3139 background)
- Sentiment filter: Toggle buttons (All/Positive/Neutral/Negative) with icons
- Clear filters: Text button right side

### 5. News Card
- Layout: #1e2329 background, 12px radius, 24px padding
- Header: Source badge (colored) + published time
- Title: 1.25em semibold, clickable, hover: #667eea
- Keywords: Chips (#2b3139 background, 4px radius)
- Sentiment: Circle icon (20px) + score (Positive: #43e97b, Negative: #ff6b6b, Neutral: #848e9c)
- Hover: Border #667eea, slight scale

### 6. Insights Page Filters
- Filter bar: Same style as News filters
- Severity filter: Chips (High: #ff6b6b, Medium: #f0b90b, Low: #43e97b)
- Symbol filter: Searchable multi-select dropdown
- Type filter: Multi-select (Sentiment Shift, Volume Spike, Trend Reversal, etc.)
- Action buttons: "Generate New Insights" (primary gradient), "Refresh" (secondary)

### 7. Insight Card
- Layout: #1e2329 background, 12px radius, 24px padding
- Header: Severity badge + timestamp
- Type & Symbol: Type label (uppercase, #667eea) + Symbol badge
- Description: 1em, 3 lines max, "Read more" link (#667eea)
- Actions: "View Details" (outline), "Dismiss" (text)
- Hover: Border #667eea

### 8. Trend Indicator
- Inline arrow icon: 16px × 16px
- Up: ↑ #43e97b
- Down: ↓ #ff6b6b
- Neutral: → #848e9c
- Usage: Next to values in summary cards, tables

### 9. Loading States
- Skeleton cards: Shimmer animation (#2b3139 → #1e2329), placeholder rectangles
- Spinner: Circular, #667eea, 40px
- Progress bar: 4px height, gradient fill

### 10. Error States
- Error card: #1e2329 background, 2px red border, centered
- Content: Error icon (64px, #ff6b6b), title, message, retry button
- Inline error: Red background (10% opacity), red border, warning icon

### 11. Empty States
- Centered layout, 64px icon (#848e9c)
- Title (H3), message (body text), optional CTA button
- Variations: No data, No results, Error, Empty list

### Design System Extensions
- Hover states: 10-15% brighter colors
- Active states: 5-10% darker colors
- Disabled: 50% opacity
- Focus ring: 2px solid #667eea, 4px offset
- Transitions: 0.2-0.3s ease

### Interactive Elements
- Loading states: Skeleton screens or spinners (see detailed specs above)
- Error states: Red alert boxes with retry button (see detailed specs above)
- Empty states: Centered message with icon (see detailed specs above)
- Hover states: All clickable elements
- Active states: Selected filters, current page

### Responsive Behavior
- Mobile (< 768px): Single column, stacked cards, simplified charts, vertical filters, sidebar bottom
- Tablet (768px - 1024px): 2 columns, adjusted spacing
- Desktop (> 1024px): Full layout as specified

### Additional Requirements
- Ensure all text is readable (WCAG AA contrast ratio - 4.5:1 minimum)
- Use consistent icon style (emoji or icon set)
- Include placeholder data for realistic preview
- Show data refresh indicators
- Design for real-time updates (subtle animations)
- All components should be pixel-perfect and production-ready
- Include multiple states for each component (Default, Hover, Active, Disabled, Loading, Error)
- Export design tokens: colors, spacing, typography as variables
```

---

## 사용 방법

1. **Core Prompt 섹션 전체를 복사**하여 Figma AI에 전달
2. 기본 구조와 상세 컴포넌트가 모두 포함되어 있어 단독으로 사용 가능
3. 각 컴포넌트의 모든 상태(Default, Hover, Loading, Error 등) 포함
4. 디자인 토큰(색상, 간격, 타이포그래피) 별도로 export

---

## 핵심 포인트

- **완전성**: 기본 구조와 상세 컴포넌트 모두 포함
- **간결함**: 불필요한 설명 제거, 핵심 스펙만 포함
- **구현 중심**: React 구현에 필요한 최소한의 디자인 정보
- **완성도**: 모든 상태와 반응형 포함

---

**참고**: 이 프롬프트는 기본 레이아웃과 상세 컴포넌트 디자인을 모두 포함합니다. 단독으로 사용 가능합니다.
