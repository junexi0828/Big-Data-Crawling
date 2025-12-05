import { SummaryCard } from "./summary-card";
import { FearGreedGauge } from "./fear-greed-gauge";
import { TopCoinsTable } from "./top-coins-table";
import { SentimentTimeline } from "./sentiment-timeline";
import { LatestInsights } from "./latest-insights";

export function DashboardPage() {
  const topCoins = [
    { symbol: "BTC", volume24h: 28500000000, change24h: 2.45 },
    { symbol: "ETH", volume24h: 15200000000, change24h: -1.23 },
    { symbol: "BNB", volume24h: 8900000000, change24h: 3.78 },
    { symbol: "SOL", volume24h: 4200000000, change24h: 5.12 },
    { symbol: "XRP", volume24h: 3800000000, change24h: -0.56 },
  ];

  // Generate mock data for 24h
  const sentimentData24h = Array.from({ length: 24 }, (_, i) => ({
    time: `${i}:00`,
    positive: 0.3 + Math.random() * 0.4,
    neutral: -0.1 + Math.random() * 0.2,
    negative: -0.5 + Math.random() * 0.3,
  }));

  // Generate mock data for 7d
  const sentimentData7d = Array.from({ length: 7 }, (_, i) => ({
    time: `Day ${i + 1}`,
    positive: 0.35 + Math.random() * 0.35,
    neutral: -0.05 + Math.random() * 0.15,
    negative: -0.45 + Math.random() * 0.25,
  }));

  // Generate mock data for 30d
  const sentimentData30d = Array.from({ length: 30 }, (_, i) => ({
    time: `${i + 1}`,
    positive: 0.4 + Math.random() * 0.3,
    neutral: 0 + Math.random() * 0.1,
    negative: -0.4 + Math.random() * 0.2,
  }));

  const latestInsights = [
    {
      id: 1,
      type: "sentiment_shift",
      symbol: "BTC",
      description: "Significant positive sentiment shift detected in Bitcoin discussions",
      severity: "high" as const,
      timestamp: "2 hours ago",
    },
    {
      id: 2,
      type: "volume_spike",
      symbol: "ETH",
      description: "Unusual volume spike detected, 300% above average",
      severity: "medium" as const,
      timestamp: "3 hours ago",
    },
    {
      id: 3,
      type: "trend_reversal",
      symbol: "SOL",
      description: "Potential trend reversal pattern forming",
      severity: "low" as const,
      timestamp: "5 hours ago",
    },
    {
      id: 4,
      type: "sentiment_shift",
      symbol: "BNB",
      description: "Negative sentiment increasing across multiple sources",
      severity: "high" as const,
      timestamp: "6 hours ago",
    },
    {
      id: 5,
      type: "volume_spike",
      symbol: "XRP",
      description: "Trading volume increased by 150%",
      severity: "medium" as const,
      timestamp: "8 hours ago",
    },
  ];

  return (
    <div className="space-y-8">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <SummaryCard
          icon="📰"
          label="Total News"
          value="1,247"
          color="#667eea"
        />
        <SummaryCard
          icon="😊"
          label="Avg Sentiment"
          value="0.65"
          color="#f093fb"
          trend="up"
          trendValue="12%"
        />
        <SummaryCard
          icon="💡"
          label="Recent Insights"
          value="34"
          color="#4facfe"
        />
        <SummaryCard
          icon="🔗"
          label="Active Sources"
          value="18"
          color="#43e97b"
        />
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        <FearGreedGauge value={68} />
        <TopCoinsTable coins={topCoins} />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        <div className="lg:col-span-2">
          <SentimentTimeline 
            data24h={sentimentData24h}
            data7d={sentimentData7d}
            data30d={sentimentData30d}
          />
        </div>
        <LatestInsights insights={latestInsights} />
      </div>
    </div>
  );
}