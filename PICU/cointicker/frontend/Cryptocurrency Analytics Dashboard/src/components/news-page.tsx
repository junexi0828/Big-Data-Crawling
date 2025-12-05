import { useState } from "react";
import { NewsCard } from "./news-card";
import { Button } from "./ui/button";
import { RefreshCw } from "lucide-react";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";

export function NewsPage() {
  const [sourceFilter, setSourceFilter] = useState<string>("all");
  const [sentimentFilter, setSentimentFilter] = useState<string>("all");

  const newsData = [
    {
      id: 1,
      source: "CoinDesk",
      title: "Bitcoin Surges Past $65,000 as Institutional Adoption Grows",
      url: "https://example.com",
      publishedAt: "2 hours ago",
      keywords: ["bitcoin", "btc", "institutional", "adoption", "bullish"],
      sentiment: 0.75,
    },
    {
      id: 2,
      source: "CryptoNews",
      title: "Ethereum 2.0 Staking Reaches New Milestone with 30M ETH Locked",
      url: "https://example.com",
      publishedAt: "4 hours ago",
      keywords: ["ethereum", "eth", "staking", "eth2", "defi"],
      sentiment: 0.62,
    },
    {
      id: 3,
      source: "Bloomberg",
      title: "SEC Delays Decision on Bitcoin ETF Applications",
      url: "https://example.com",
      publishedAt: "6 hours ago",
      keywords: ["bitcoin", "etf", "sec", "regulation"],
      sentiment: -0.35,
    },
    {
      id: 4,
      source: "Decrypt",
      title: "Solana Network Experiences Brief Outage, Recovery Underway",
      url: "https://example.com",
      publishedAt: "8 hours ago",
      keywords: ["solana", "sol", "network", "outage"],
      sentiment: -0.58,
    },
    {
      id: 5,
      source: "CoinTelegraph",
      title: "DeFi Total Value Locked Crosses $100 Billion Mark",
      url: "https://example.com",
      publishedAt: "10 hours ago",
      keywords: ["defi", "tvl", "finance", "growth"],
      sentiment: 0.48,
    },
    {
      id: 6,
      source: "The Block",
      title: "NFT Market Shows Signs of Recovery with Rising Floor Prices",
      url: "https://example.com",
      publishedAt: "12 hours ago",
      keywords: ["nft", "market", "recovery", "floor price"],
      sentiment: 0.32,
    },
    {
      id: 7,
      source: "CoinDesk",
      title: "Cardano Launches Major Smart Contract Upgrade",
      url: "https://example.com",
      publishedAt: "14 hours ago",
      keywords: ["cardano", "ada", "smart contracts", "upgrade"],
      sentiment: 0.55,
    },
    {
      id: 8,
      source: "CryptoNews",
      title: "Binance Introduces New Staking Options for Multiple Tokens",
      url: "https://example.com",
      publishedAt: "16 hours ago",
      keywords: ["binance", "bnb", "staking", "exchange"],
      sentiment: 0.28,
    },
  ];

  const filteredNews = newsData.filter((news) => {
    const matchesSource = sourceFilter === "all" || news.source === sourceFilter;
    const matchesSentiment = 
      sentimentFilter === "all" ||
      (sentimentFilter === "positive" && news.sentiment > 0.2) ||
      (sentimentFilter === "neutral" && news.sentiment >= -0.2 && news.sentiment <= 0.2) ||
      (sentimentFilter === "negative" && news.sentiment < -0.2);
    
    return matchesSource && matchesSentiment;
  });

  const sources = ["all", ...Array.from(new Set(newsData.map((n) => n.source)))];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between flex-wrap gap-4">
        <h2 className="text-[#eaecef]">Latest News</h2>
        
        <Button 
          className="bg-gradient-to-r from-[#667eea] to-[#764ba2] hover:opacity-90 transition-opacity"
        >
          <RefreshCw className="w-4 h-4 mr-2" />
          Refresh
        </Button>
      </div>

      {/* Filters */}
      <div className="flex gap-4 flex-wrap">
        <div className="flex items-center gap-2">
          <span className="text-sm text-[#848e9c]">Source:</span>
          <Select value={sourceFilter} onValueChange={setSourceFilter}>
            <SelectTrigger className="w-[180px] bg-[#1e2329] border-[#2b3139]">
              <SelectValue />
            </SelectTrigger>
            <SelectContent className="bg-[#1e2329] border-[#2b3139]">
              {sources.map((source) => (
                <SelectItem key={source} value={source} className="text-[#eaecef]">
                  {source === "all" ? "All Sources" : source}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-sm text-[#848e9c]">Sentiment:</span>
          <Select value={sentimentFilter} onValueChange={setSentimentFilter}>
            <SelectTrigger className="w-[180px] bg-[#1e2329] border-[#2b3139]">
              <SelectValue />
            </SelectTrigger>
            <SelectContent className="bg-[#1e2329] border-[#2b3139]">
              <SelectItem value="all" className="text-[#eaecef]">All</SelectItem>
              <SelectItem value="positive" className="text-[#eaecef]">Positive</SelectItem>
              <SelectItem value="neutral" className="text-[#eaecef]">Neutral</SelectItem>
              <SelectItem value="negative" className="text-[#eaecef]">Negative</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* News List */}
      <div className="space-y-4">
        {filteredNews.length > 0 ? (
          filteredNews.map((news) => (
            <NewsCard key={news.id} news={news} />
          ))
        ) : (
          <div className="text-center py-16">
            <div className="text-6xl mb-4">📰</div>
            <h3 className="text-[#eaecef] mb-2">No news available</h3>
            <p className="text-[#848e9c]">Try adjusting your filters</p>
          </div>
        )}
      </div>
    </div>
  );
}