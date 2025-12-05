import { useState } from "react";
import { InsightCard } from "./insight-card";
import { Button } from "./ui/button";
import { RefreshCw, Sparkles } from "lucide-react";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";

export function InsightsPage() {
  const [severityFilter, setSeverityFilter] = useState<string>("all");
  const [symbolFilter, setSymbolFilter] = useState<string>("all");
  const [typeFilter, setTypeFilter] = useState<string>("all");

  const [insights, setInsights] = useState([
    {
      id: 1,
      type: "sentiment_shift",
      symbol: "BTC",
      description: "Significant positive sentiment shift detected in Bitcoin discussions across major platforms",
      severity: "high" as const,
      timestamp: "2 hours ago",
      details: "Analysis of 5,000+ social media posts and news articles shows a 45% increase in positive sentiment. This shift correlates with institutional adoption announcements and technical breakout patterns.",
    },
    {
      id: 2,
      type: "volume_spike",
      symbol: "ETH",
      description: "Unusual volume spike detected - 300% above 30-day average",
      severity: "high" as const,
      timestamp: "3 hours ago",
      details: "Trading volume has reached $18.2B in the last 24 hours, significantly higher than the 30-day average of $6.1B. This spike is accompanied by increased on-chain activity.",
    },
    {
      id: 3,
      type: "trend_reversal",
      symbol: "SOL",
      description: "Potential trend reversal pattern forming on 4-hour chart",
      severity: "medium" as const,
      timestamp: "5 hours ago",
      details: "Technical indicators suggest a bullish reversal pattern. RSI has moved out of oversold territory, and a golden cross is forming on shorter timeframes.",
    },
    {
      id: 4,
      type: "sentiment_shift",
      symbol: "BNB",
      description: "Negative sentiment increasing across multiple news sources",
      severity: "medium" as const,
      timestamp: "6 hours ago",
      details: "Recent regulatory concerns and network issues have led to a 28% increase in negative sentiment over the past 48 hours.",
    },
    {
      id: 5,
      type: "volume_spike",
      symbol: "XRP",
      description: "Trading volume increased by 150% following legal developments",
      severity: "low" as const,
      timestamp: "8 hours ago",
      details: "Volume surge appears to be driven by positive legal news. Current volume at $4.2B represents a significant increase from baseline.",
    },
    {
      id: 6,
      type: "trend_reversal",
      symbol: "ADA",
      description: "Bearish divergence forming on daily chart",
      severity: "low" as const,
      timestamp: "10 hours ago",
      details: "Price making higher highs while momentum indicators show lower highs, suggesting potential weakness in the current uptrend.",
    },
    {
      id: 7,
      type: "sentiment_shift",
      symbol: "DOGE",
      description: "Social media mentions increased by 200% in last 12 hours",
      severity: "medium" as const,
      timestamp: "12 hours ago",
      details: "Viral social media activity has driven a surge in mentions. Sentiment is mixed with both positive and negative discussions trending.",
    },
    {
      id: 8,
      type: "volume_spike",
      symbol: "MATIC",
      description: "On-chain activity shows unusual wallet movements",
      severity: "high" as const,
      timestamp: "14 hours ago",
      details: "Large wallet movements detected. Over $500M in tokens moved to exchanges in the past 24 hours, which could signal upcoming volatility.",
    },
  ]);

  const filteredInsights = insights.filter((insight) => {
    const matchesSeverity = severityFilter === "all" || insight.severity === severityFilter;
    const matchesSymbol = symbolFilter === "all" || insight.symbol === symbolFilter;
    const matchesType = typeFilter === "all" || insight.type === typeFilter;
    
    return matchesSeverity && matchesSymbol && matchesType;
  });

  const symbols = ["all", ...Array.from(new Set(insights.map((i) => i.symbol)))];
  const types = ["all", ...Array.from(new Set(insights.map((i) => i.type)))];

  const handleDismiss = (id: number) => {
    setInsights(insights.filter((insight) => insight.id !== id));
  };

  const getTypeLabel = (type: string) => {
    if (type === "all") return "All Types";
    return type.split("_").map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(" ");
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between flex-wrap gap-4">
        <h2 className="text-[#eaecef]">Investment Insights</h2>
        
        <div className="flex gap-2">
          <Button 
            className="bg-gradient-to-r from-[#667eea] to-[#764ba2] hover:opacity-90 transition-opacity"
          >
            <Sparkles className="w-4 h-4 mr-2" />
            Generate New Insights
          </Button>
          <Button 
            className="bg-[#2b3139] hover:bg-[#667eea] text-[#eaecef] transition-colors"
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh
          </Button>
        </div>
      </div>

      {/* Filters */}
      <div className="flex gap-4 flex-wrap">
        <div className="flex items-center gap-2">
          <span className="text-sm text-[#848e9c]">Severity:</span>
          <Select value={severityFilter} onValueChange={setSeverityFilter}>
            <SelectTrigger className="w-[160px] bg-[#1e2329] border-[#2b3139]">
              <SelectValue />
            </SelectTrigger>
            <SelectContent className="bg-[#1e2329] border-[#2b3139]">
              <SelectItem value="all" className="text-[#eaecef]">All</SelectItem>
              <SelectItem value="high" className="text-[#eaecef]">High</SelectItem>
              <SelectItem value="medium" className="text-[#eaecef]">Medium</SelectItem>
              <SelectItem value="low" className="text-[#eaecef]">Low</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-sm text-[#848e9c]">Symbol:</span>
          <Select value={symbolFilter} onValueChange={setSymbolFilter}>
            <SelectTrigger className="w-[160px] bg-[#1e2329] border-[#2b3139]">
              <SelectValue />
            </SelectTrigger>
            <SelectContent className="bg-[#1e2329] border-[#2b3139]">
              {symbols.map((symbol) => (
                <SelectItem key={symbol} value={symbol} className="text-[#eaecef]">
                  {symbol === "all" ? "All Symbols" : symbol}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-sm text-[#848e9c]">Type:</span>
          <Select value={typeFilter} onValueChange={setTypeFilter}>
            <SelectTrigger className="w-[200px] bg-[#1e2329] border-[#2b3139]">
              <SelectValue />
            </SelectTrigger>
            <SelectContent className="bg-[#1e2329] border-[#2b3139]">
              {types.map((type) => (
                <SelectItem key={type} value={type} className="text-[#eaecef]">
                  {getTypeLabel(type)}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Insights List */}
      <div className="space-y-4">
        {filteredInsights.length > 0 ? (
          filteredInsights.map((insight) => (
            <InsightCard key={insight.id} insight={insight} onDismiss={handleDismiss} />
          ))
        ) : (
          <div className="text-center py-16">
            <div className="text-6xl mb-4">💡</div>
            <h3 className="text-[#eaecef] mb-2">No insights available</h3>
            <p className="text-[#848e9c] mb-4">Try adjusting your filters or generate new insights</p>
            <Button 
              className="bg-gradient-to-r from-[#667eea] to-[#764ba2] hover:opacity-90 transition-opacity"
            >
              <Sparkles className="w-4 h-4 mr-2" />
              Generate New Insights
            </Button>
          </div>
        )}
      </div>
    </div>
  );
}