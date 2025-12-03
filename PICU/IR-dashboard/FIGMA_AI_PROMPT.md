# Figma AI Design Prompt for CoinTicker Dashboard

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
- Card 1: Total News Count
  - Icon: 📰
  - Large number display
  - Label: "Total News"
  - Color: #667eea

- Card 2: Average Sentiment Score
  - Icon: 😊
  - Score display (decimal format: X.XX)
  - Label: "Avg Sentiment"
  - Color: #f093fb
  - Show trend indicator (up/down arrow)

- Card 3: Recent Insights Count
  - Icon: 💡
  - Number display
  - Label: "Recent Insights"
  - Color: #4facfe

- Card 4: Active Sources
  - Icon: 🔗
  - Number display
  - Label: "Active Sources"
  - Color: #43e97b

**Middle Section - Key Metrics (2 columns)**
- Left Column: Fear & Greed Index
  - Large circular gauge or progress bar
  - Value: 0-100
  - Classification label: "Extreme Fear" / "Fear" / "Neutral" / "Greed" / "Extreme Greed"
  - Color coding based on value

- Right Column: Top 5 Volume Coins
  - Table or list format
  - Columns: Symbol, 24h Volume, 24h Change (%)
  - Highlight positive/negative changes with colors
  - Sortable headers

**Bottom Section - Charts (2 columns)**
- Left Column: Sentiment Timeline Chart
  - Line chart area
  - X-axis: Time (hours/days)
  - Y-axis: Sentiment score (-1.0 to 1.0)
  - Multiple lines: Positive (green), Neutral (gray), Negative (red)
  - Tooltip on hover showing exact values
  - Time range selector: 24h / 7d / 30d

- Right Column: Market Overview
  - Summary of top volume coins
  - Visual representation (bars or cards)
  - Quick stats

**Sidebar (Optional)**
- Latest Insights Preview
  - List of 5-10 most recent insights
  - Each item: Type, Symbol, Severity badge, Timestamp
  - Click to expand details

### Page 2: News Page
Layout: List view with filters

**Header**
- Title: "Latest News"
- Refresh button
- Filter options: Source, Date range, Sentiment

**News List**
- Card-based layout
- Each news card contains:
  - Source badge (colored)
  - Title (clickable, opens URL)
  - Published date/time
  - Keywords tags (chips)
  - Sentiment indicator (icon + score)
  - Expandable details section
- Pagination or infinite scroll
- Empty state: "No news available"

**Sentiment Indicators**
- Positive: Green circle + score
- Negative: Red circle + score
- Neutral: Gray circle + score

### Page 3: Insights Page
Layout: List view with actions

**Header**
- Title: "Investment Insights"
- Action buttons: "Generate New Insights", "Refresh"
- Filter: Severity (High/Medium/Low), Symbol, Type

**Insights List**
- Card-based layout
- Each insight card contains:
  - Severity badge (High: red, Medium: yellow, Low: green)
  - Type label (e.g., "Sentiment Shift", "Volume Spike", "Trend Reversal")
  - Symbol badge
  - Description text (truncated with "Read more")
  - Timestamp
  - Action buttons: "View Details", "Dismiss"
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

### Interactive Elements
- Loading states: Skeleton screens or spinners
- Error states: Red alert boxes with retry button
- Empty states: Centered message with icon
- Hover states: All clickable elements
- Active states: Selected filters, current page

### Responsive Behavior
- Mobile (< 768px): Single column, stacked cards, simplified charts
- Tablet (768px - 1024px): 2 columns, adjusted spacing
- Desktop (> 1024px): Full layout as specified

### Additional Requirements
- Ensure all text is readable (WCAG AA contrast ratio)
- Use consistent icon style (emoji or icon set)
- Include placeholder data for realistic preview
- Show data refresh indicators
- Design for real-time updates (subtle animations)
```

---

## Alternative: Simplified Prompt (If the above is too long)

```
Design a dark-themed cryptocurrency analytics dashboard with:

1. Dashboard page:
   - 4 summary cards: Total News, Avg Sentiment, Recent Insights, Active Sources
   - Fear & Greed Index gauge
   - Top 5 volume coins table
   - Sentiment timeline line chart (positive/neutral/negative lines)
   - Latest insights sidebar

2. News page:
   - Filterable news list with source, date, sentiment indicators
   - Card layout with title, source badge, keywords, sentiment score

3. Insights page:
   - List of investment insights with severity badges (High/Medium/Low)
   - Each card: type, symbol, description, timestamp
   - Generate insights button

Design system:
- Dark background: #0b0e11
- Cards: #1e2329 with #2b3139 borders
- Colors: #667eea (primary), #f0b90b (accent), #43e97b (positive), #ff6b6b (negative)
- Modern, clean, professional
- Fully responsive
- Include loading, error, and empty states
```

---

## Data Structure Reference (For Context)

### Dashboard Summary API Response
```json
{
  "fear_greed_index": {
    "value": 65,
    "classification": "Greed"
  },
  "sentiment_average": 0.45,
  "top_volume_coins": [
    {
      "symbol": "BTC",
      "volume_24h": 15000000000,
      "change_24h": 2.5
    }
  ],
  "latest_insights": [
    {
      "type": "sentiment_shift",
      "symbol": "BTC",
      "description": "Significant positive sentiment shift detected",
      "severity": "high"
    }
  ]
}
```

### Sentiment Timeline API Response
```json
{
  "timeline": [
    {
      "timestamp": "2025-01-15 14:00:00",
      "sentiment": 0.52,
      "count": 15
    }
  ]
}
```

### News API Response
```json
{
  "news": [
    {
      "id": 1,
      "source": "CoinDesk",
      "title": "Bitcoin reaches new high",
      "url": "https://...",
      "published_at": "2025-01-15T14:00:00",
      "keywords": ["bitcoin", "crypto", "bullish"]
    }
  ]
}
```

### Insights API Response
```json
{
  "insights": [
    {
      "id": 1,
      "type": "volume_spike",
      "symbol": "ETH",
      "description": "Unusual volume spike detected",
      "severity": "medium",
      "created_at": "2025-01-15T14:00:00"
    }
  ]
}
```

---

## Usage Instructions

1. **Copy the "Core Prompt"** section above
2. Paste into Figma AI (Figma → AI → Generate Design)
3. Adjust colors/spacing if needed based on your brand
4. Export components for React implementation
5. Use the data structure reference to ensure API compatibility

## Notes

- The design should be component-based for easy React conversion
- All measurements should be in pixels or rem units
- Include hover states and transitions
- Consider accessibility (contrast, focus states)
- Design should work with Chart.js library for charts

