# Figma AI Design Prompt for CoinTicker Dashboard - Part 2

## 상세 컴포넌트 및 고급 기능 디자인

이 프롬프트는 Part 1의 기본 디자인을 기반으로, 구현 시 필요한 상세 컴포넌트와 고급 기능에 대한 디자인을 요청합니다.

---

## Core Prompt Part 2 (Copy this to Figma AI)

```
Based on the existing CoinTicker Dashboard design (Part 1), create detailed designs for the following advanced components and features:

### Design System Refinements

**Color Palette Extensions**
- Gradient definitions for all accent colors
- Hover state color variations (10-15% brighter)
- Active state color variations (5-10% darker)
- Disabled state colors (50% opacity with gray overlay)
- Focus ring colors for accessibility (#667eea with 20% opacity)

**Typography Extensions**
- Code/monospace font for numbers and data
- Font weights: 400 (regular), 500 (medium), 600 (semibold), 700 (bold)
- Line heights: 1.2 (headings), 1.5 (body), 1.4 (small text)
- Letter spacing: -0.02em (headings), 0 (body)

**Spacing System**
- Base unit: 4px
- Scale: 4, 8, 12, 16, 20, 24, 32, 40, 48, 64px
- Component spacing: 20px (cards), 16px (compact), 24px (spacious)
- Section spacing: 40px (desktop), 24px (tablet), 20px (mobile)

---

### Component 1: Fear & Greed Index Gauge (Detailed)

**Layout Requirements**
- Circular gauge (recommended) or semi-circular gauge
- Size: 300px × 300px (desktop), 250px × 250px (tablet), 200px × 200px (mobile)
- Center position for value display

**Visual Design**
- Background circle: #1e2329 with #2b3139 border
- Gauge arc: Gradient based on value
  - 0-20 (Extreme Fear): #ff6b6b to #ff8787
  - 21-40 (Fear): #ffa94d to #ffc069
  - 41-60 (Neutral): #ffd43b to #f0b90b
  - 61-80 (Greed): #51cf66 to #43e97b
  - 81-100 (Extreme Greed): #43e97b to #69db7c
- Needle/indicator: White (#eaecef) with shadow
- Value display: Large number (3em, bold) in center
- Classification label: Below value (1.2em, semibold)
- Percentage indicator: Small text below classification

**Interactive States**
- Hover: Subtle glow effect on gauge
- Loading: Skeleton circle with pulsing animation
- Error: Red border with error icon

**Example States to Show**
- Extreme Fear (15)
- Neutral (50)
- Extreme Greed (85)

---

### Component 2: Top 5 Volume Coins Table (Detailed)

**Table Structure**
- Header row: Sticky on scroll
- 5 data rows (Top 5 coins)
- Columns: Rank, Symbol, 24h Volume, 24h Change (%)

**Column Specifications**

1. **Rank Column**
   - Width: 60px
   - Badge style: Circular, #667eea background
   - Number: White, bold, 1em

2. **Symbol Column**
   - Width: 120px
   - Large symbol text: 1.5em, bold, #eaecef
   - Optional: Small coin icon/logo placeholder

3. **24h Volume Column**
   - Width: 180px
   - Format: Abbreviated (e.g., "15.2B", "1.5M")
   - Font: Monospace, 1em, #848e9c
   - Right-aligned

4. **24h Change Column**
   - Width: 120px
   - Format: "+X.XX%" or "-X.XX%"
   - Color coding:
     - Positive: #43e97b with ↑ icon
     - Negative: #ff6b6b with ↓ icon
     - Zero: #848e9c
   - Font: 1em, semibold, right-aligned
   - Background: Subtle colored background (10% opacity)

**Table Styling**
- Background: #1e2329
- Border: 1px solid #2b3139
- Border radius: 12px
- Row padding: 16px vertical, 20px horizontal
- Row hover: Background #2b3139, border-left: 3px solid #667eea
- Alternating rows: Subtle background difference (optional)

**Header Styling**
- Background: #0b0e11
- Text: #848e9c, 0.875em, semibold, uppercase
- Sortable indicators: Arrow icons (↑↓) when sortable
- Hover: Text color changes to #eaecef

**Empty State**
- Centered message: "No volume data available"
- Icon: 📊
- Text: #848e9c

---

### Component 3: Latest Insights Sidebar (Detailed)

**Layout**
- Fixed or sticky sidebar (right side on desktop)
- Width: 320px (desktop), full width (mobile)
- Max height: Scrollable container
- Background: #1e2329 with #2b3139 border

**Header Section**
- Title: "Latest Insights" (H3 style)
- Refresh button: Icon button, top-right
- Count badge: Small, #667eea background

**Insight Item Card**
- Background: #0b0e11 (subtle difference from sidebar)
- Border: 1px solid #2b3139
- Border radius: 8px
- Padding: 16px
- Margin bottom: 12px
- Hover: Border color changes to #667eea, slight elevation

**Insight Item Content**
1. **Header Row**
   - Severity badge: Left (High/Medium/Low)
   - Timestamp: Right (relative time, e.g., "2h ago")
   - Font: 0.75em, #848e9c

2. **Type Label**
   - Text: Uppercase, 0.875em, semibold, #667eea
   - Margin: 8px 0

3. **Symbol Badge**
   - Pill shape, #2b3139 background
   - Text: 0.875em, bold, #eaecef
   - Margin: 4px 0

4. **Description Preview**
   - Text: 0.875em, #848e9c, 2 lines max (truncated with "...")
   - Line height: 1.4

5. **Expand Indicator** (if expandable)
   - Icon: Chevron down
   - Color: #667eea
   - Click to expand full description

**Empty State**
- Centered message: "No insights yet"
- Icon: 💡
- Text: #848e9c
- CTA button: "Generate Insights" (optional)

---

### Component 4: News Page Filters (Detailed)

**Filter Bar Layout**
- Horizontal layout (desktop), vertical stack (mobile)
- Background: #1e2329
- Border: 1px solid #2b3139
- Border radius: 12px
- Padding: 20px
- Margin bottom: 24px

**Filter Components**

1. **Source Filter**
   - Type: Multi-select dropdown or chip group
   - Options: CoinDesk, CoinTelegraph, Decrypt, etc.
   - Selected state: #667eea background, white text
   - Unselected state: #2b3139 background, #848e9c text
   - Chip style: Rounded pill, 8px padding

2. **Date Range Filter**
   - Type: Dropdown or date picker
   - Options: Today, Last 7 days, Last 30 days, Custom range
   - Style: Select dropdown with #2b3139 background
   - Selected text: #eaecef
   - Icon: Calendar icon

3. **Sentiment Filter**
   - Type: Toggle buttons or chip group
   - Options: All, Positive, Neutral, Negative
   - Active state: Gradient background (#667eea to #764ba2)
   - Inactive state: #2b3139 background
   - Icons: 😊 (positive), 😐 (neutral), 😞 (negative)

4. **Clear Filters Button**
   - Style: Text button, #848e9c color
   - Hover: #eaecef color
   - Position: Right side of filter bar

**Filter Interaction States**
- Hover: Background lightens by 10%
- Active: Border highlight (#667eea)
- Disabled: 50% opacity

---

### Component 5: News Card (Detailed)

**Card Layout**
- Background: #1e2329
- Border: 1px solid #2b3139
- Border radius: 12px
- Padding: 24px
- Margin bottom: 20px
- Hover: Border color #667eea, slight shadow, transform scale(1.01)

**Card Content Structure**

1. **Header Section**
   - Source badge: Left (colored pill, e.g., CoinDesk = blue)
   - Published time: Right (relative time, #848e9c, 0.875em)
   - Margin bottom: 12px

2. **Title Section**
   - Font: 1.25em, semibold, #eaecef
   - Line height: 1.4
   - Margin bottom: 12px
   - Hover: Color changes to #667eea
   - Clickable: Opens URL in new tab

3. **Keywords Section**
   - Container: Flex wrap
   - Keyword chips:
     - Background: #2b3139
     - Text: #848e9c, 0.75em
     - Padding: 4px 8px
     - Border radius: 4px
     - Margin: 4px 4px 4px 0
   - Margin bottom: 12px

4. **Sentiment Indicator Section**
   - Layout: Horizontal flex
   - Sentiment icon: Circle (20px)
     - Positive: Green (#43e97b)
     - Negative: Red (#ff6b6b)
     - Neutral: Gray (#848e9c)
   - Sentiment score: Next to icon, 0.875em, #848e9c
   - Format: "+0.XX" or "-0.XX"

5. **Expandable Details** (Optional)
   - Toggle button: "Show more" / "Show less"
   - Additional info: Summary, full keywords, related symbols
   - Animation: Smooth expand/collapse

**Empty State**
- Centered layout
- Icon: 📰 (large, 64px)
- Title: "No news available"
- Message: "Try adjusting your filters"
- Text: #848e9c

---

### Component 6: Insights Page Filters (Detailed)

**Filter Bar Layout**
- Similar to News filters but with different options
- Background: #1e2329
- Border: 1px solid #2b3139
- Border radius: 12px
- Padding: 20px
- Margin bottom: 24px

**Filter Components**

1. **Severity Filter**
   - Type: Chip group or toggle buttons
   - Options: All, High, Medium, Low
   - Color coding:
     - High: #ff6b6b background
     - Medium: #f0b90b background
     - Low: #43e97b background
   - Active state: Full opacity, white text
   - Inactive state: 30% opacity, border only

2. **Symbol Filter**
   - Type: Searchable dropdown or multi-select
   - Options: BTC, ETH, BNB, etc. (all available symbols)
   - Search input: #2b3139 background, #eaecef text
   - Selected items: Chips with #667eea background

3. **Type Filter**
   - Type: Multi-select dropdown
   - Options: Sentiment Shift, Volume Spike, Trend Reversal, Price Alert, etc.
   - Selected state: #667eea background
   - Unselected state: #2b3139 background

4. **Action Buttons**
   - "Generate New Insights": Primary button (gradient)
   - "Refresh": Secondary button
   - Position: Right side of filter bar

---

### Component 7: Insight Card (Detailed)

**Card Layout**
- Background: #1e2329
- Border: 1px solid #2b3139
- Border radius: 12px
- Padding: 24px
- Margin bottom: 20px
- Hover: Border color #667eea, elevation

**Card Content Structure**

1. **Header Section**
   - Severity badge: Left (High/Medium/Low with color)
   - Timestamp: Right (relative time, #848e9c)
   - Margin bottom: 16px

2. **Type and Symbol Row**
   - Type label: Uppercase, 0.875em, semibold, #667eea
   - Symbol badge: Pill, #2b3139 background, bold text
   - Layout: Horizontal flex, space-between

3. **Description Section**
   - Text: 1em, #eaecef, line height 1.5
   - Truncated: 3 lines max with "..."
   - "Read more" link: #667eea, click to expand
   - Expanded state: Full description visible

4. **Action Buttons Row**
   - "View Details": Primary button (outline style)
   - "Dismiss": Secondary button (text style, #848e9c)
   - Layout: Horizontal flex, gap 12px
   - Margin top: 16px

**Grouping Options**
- Group by date: Date header above group
- Group by severity: Severity header with color coding

**Empty State**
- Centered layout
- Icon: 💡 (large, 64px)
- Title: "No insights available"
- Message: "Generate new insights to get started"
- CTA: "Generate Insights" button (primary)

---

### Component 8: Loading States (Detailed)

**Skeleton Screens**

1. **Card Skeleton**
   - Background: #1e2329
   - Shimmer effect: Gradient animation (#2b3139 → #2b3139 → #1e2329)
   - Placeholder shapes:
     - Header: Rectangle, 40% width, 20px height
     - Body: Rectangle, 100% width, 60px height
     - Footer: Rectangle, 30% width, 16px height
   - Border radius: 12px
   - Animation: 1.5s ease-in-out infinite

2. **Table Skeleton**
   - Rows: 5 placeholder rows
   - Each row: 3-4 rectangles (columns)
   - Height: 48px per row
   - Spacing: 12px between rows

3. **Chart Skeleton**
   - Container: #1e2329 background
   - Placeholder: Wavy line pattern or grid
   - Animation: Subtle pulse

**Spinner**
- Type: Circular spinner
- Color: #667eea
- Size: 40px (default), 24px (small), 64px (large)
- Animation: Rotate 1s linear infinite

**Progress Bar** (for data loading)
- Background: #2b3139
- Fill: Gradient (#667eea to #764ba2)
- Height: 4px
- Animation: Smooth progress fill

---

### Component 9: Error States (Detailed)

**Error Card**
- Background: #1e2329
- Border: 2px solid #ff6b6b
- Border radius: 12px
- Padding: 24px
- Layout: Centered content

**Error Content**
- Icon: ⚠️ or error icon (64px, #ff6b6b)
- Title: "Something went wrong" (H3, #eaecef)
- Message: Error description (#848e9c)
- Retry button: Primary button style
- Dismiss button: Text button (optional)

**Inline Error** (for forms/filters)
- Background: #ff6b6b with 10% opacity
- Border: 1px solid #ff6b6b
- Text: #ff6b6b, 0.875em
- Padding: 12px
- Border radius: 8px
- Icon: Small warning icon

---

### Component 10: Empty States (Detailed)

**Empty State Layout**
- Centered content
- Padding: 64px vertical, 32px horizontal
- Max width: 400px

**Empty State Content**
- Icon: Large (64px), #848e9c
- Title: H3 style, #eaecef, margin-top: 24px
- Message: Body text, #848e9c, margin-top: 12px
- CTA Button: Primary button (if applicable)
- Illustration: Optional decorative element

**Variations**
- No data: "No data available"
- No results: "No results found. Try different filters."
- Error: "Failed to load data"
- Empty list: "List is empty"

---

### Component 11: Trend Indicator (Detailed)

**Trend Indicator Component**
- Layout: Inline with value
- Size: 16px × 16px icon

**Upward Trend**
- Icon: ↑ (arrow up)
- Color: #43e97b
- Animation: Subtle bounce on value change

**Downward Trend**
- Icon: ↓ (arrow down)
- Color: #ff6b6b
- Animation: Subtle bounce on value change

**Neutral/No Change**
- Icon: → (arrow right) or dash
- Color: #848e9c

**Usage Examples**
- Summary cards: Next to value
- Table cells: Inline with percentage
- Chart tooltips: Next to data point

---

### Responsive Design Specifications

**Mobile (< 768px)**
- Single column layout
- Cards: Full width, reduced padding (16px)
- Tables: Horizontal scroll or card conversion
- Filters: Vertical stack, full width
- Sidebar: Bottom sheet or hidden menu
- Font sizes: 0.9em scale
- Spacing: 16px base unit

**Tablet (768px - 1024px)**
- 2-column layout where applicable
- Cards: 2 per row
- Tables: Full width with adjusted columns
- Filters: 2-column grid
- Sidebar: Collapsible or bottom
- Font sizes: 0.95em scale
- Spacing: 18px base unit

**Desktop (> 1024px)**
- Full layout as specified
- 3-4 column grids
- Sidebar: Fixed or sticky
- All features visible
- Full spacing and typography

---

### Animation & Transitions

**Micro-interactions**
- Button hover: 0.2s ease
- Card hover: 0.3s ease
- Filter toggle: 0.15s ease
- Expand/collapse: 0.3s ease

**Page Transitions**
- Route change: Fade 0.3s
- Data update: Subtle fade-in 0.5s

**Loading Animations**
- Skeleton shimmer: 1.5s infinite
- Spinner: 1s linear infinite
- Progress: Smooth fill

---

### Accessibility Requirements

**Focus States**
- Focus ring: 2px solid #667eea, 4px offset
- Focus visible on all interactive elements
- Keyboard navigation: Tab order logical

**Color Contrast**
- Text on background: WCAG AA minimum (4.5:1)
- Interactive elements: WCAG AA minimum
- Error states: High contrast (#ff6b6b on dark)

**ARIA Labels**
- All icons: aria-label
- Buttons: Descriptive labels
- Form inputs: Labels and hints
- Status messages: aria-live regions

---

### Export Requirements

**Component Organization**
- Group by page (Dashboard, News, Insights)
- Sub-group by component type
- Name components descriptively

**Design Tokens**
- Export color palette as variables
- Export typography scale
- Export spacing scale
- Export border radius values

**Assets**
- Icons: SVG format preferred
- Illustrations: SVG or PNG (2x resolution)
- Export states: Default, Hover, Active, Disabled, Error, Loading

---

### Additional Notes

- All components should be pixel-perfect and production-ready
- Include multiple states for each component
- Show component variations (e.g., different severity levels)
- Use realistic placeholder data
- Ensure consistency with Part 1 design
- Consider dark mode only (no light mode needed)
- Design for Chart.js library compatibility
- Include hover tooltips where helpful
```

---

## Usage Instructions

1. **Copy the "Core Prompt Part 2"** section above
2. Paste into Figma AI after completing Part 1 design
3. Reference Part 1 design for consistency
4. Export components separately for React implementation
5. Use design tokens for CSS variable mapping

## Integration with Part 1

- Part 1: Overall layout and page structure
- Part 2: Detailed component specifications and states
- Combine both for complete design system

## Next Steps After Design

1. Extract design tokens (colors, spacing, typography)
2. Create component library in React
3. Implement responsive breakpoints
4. Add animations and transitions
5. Test accessibility compliance

---

**Note**: This prompt focuses on the detailed implementation aspects that were identified as missing in the React implementation plan. Use this to create production-ready component designs.
