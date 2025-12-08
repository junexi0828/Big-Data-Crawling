import { useState, useEffect } from "react";
import { NewsCard } from "./news-card";
import { Button } from "./ui/button";
import { RefreshCw } from "lucide-react";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";
import { newsAPI, externalAPI } from "../services/api";

interface NewsItem {
  id: number;
  source: string;
  title: string;
  url: string;
  publishedAt: string;
  keywords: string[];
  sentiment: number;
}

export function NewsPage() {
  const [sourceFilter, setSourceFilter] = useState<string>("all");
  const [sentimentFilter, setSentimentFilter] = useState<string>("all");
  const [newsData, setNewsData] = useState<NewsItem[]>([]);
  const [loading, setLoading] = useState(true);

  // 감성 분석 함수 (demo.html 방식)
  const analyzeSentiment = (title: string, body: string = "") => {
    const titleLower = title.toLowerCase();
    const bodyLower = body.toLowerCase();

    const positiveWords = [
      "surge", "rise", "bull", "gain", "up", "high", "rally",
      "soar", "boost", "positive", "growth"
    ];
    const negativeWords = [
      "fall", "drop", "bear", "crash", "down", "low", "decline",
      "plunge", "negative", "loss"
    ];

    const positiveCount = positiveWords.filter(
      (word) => titleLower.includes(word) || bodyLower.includes(word)
    ).length;
    const negativeCount = negativeWords.filter(
      (word) => titleLower.includes(word) || bodyLower.includes(word)
    ).length;

    if (positiveCount > negativeCount) return 0.5;
    if (negativeCount > positiveCount) return -0.5;
    return 0;
  };

  // 뉴스 데이터 로드
  const loadNews = async () => {
    setLoading(true);
    try {
      // 먼저 백엔드 API 시도
      try {
        const backendData = await newsAPI.getLatestNews(50);
        if (backendData.news && backendData.news.length > 0) {
          const formattedNews = await Promise.all(
            backendData.news.slice(0, 20).map(async (item: any, index: number) => {
              let sentiment = 0;
              try {
                const sentimentRes = await fetch(
                  `${import.meta.env.VITE_API_BASE_URL || "http://localhost:5000"}/api/news/${item.id}/sentiment`
                );
                if (sentimentRes.ok) {
                  const sentimentData = await sentimentRes.json();
                  sentiment = sentimentData.sentiment_score || 0;
                }
              } catch (e) {
                sentiment = analyzeSentiment(item.title, item.content || "");
              }

              const publishedAt = new Date(item.published_at);
              const timeDiff = Math.floor((Date.now() - publishedAt.getTime()) / 60000);
              const timeAgo = timeDiff < 60
                ? `${timeDiff}분 전`
                : `${Math.floor(timeDiff / 60)}시간 전`;

              return {
                id: item.id,
                source: item.source,
                title: item.title,
                url: item.url || "#",
                publishedAt: timeAgo,
                keywords: item.keywords || [],
                sentiment: sentiment,
              };
            })
          );
          setNewsData(formattedNews);
          setLoading(false);
          return;
        }
      } catch (e) {
        console.log("백엔드 뉴스 API 실패, 외부 API 사용");
      }

      // 백엔드 실패 시 CryptoCompare API 사용
      const externalNews = await externalAPI.getCryptoNews();
      const formattedNews = externalNews.slice(0, 20).map((item: any, index: number) => {
        const timeDiff = Math.floor((Date.now() / 1000 - item.published_on) / 60);
        const timeAgo = timeDiff < 60
          ? `${timeDiff}분 전`
          : `${Math.floor(timeDiff / 60)}시간 전`;

        const sentiment = analyzeSentiment(item.title, item.body || "");

        return {
          id: index + 1,
          source: item.source_info?.name || "Unknown",
          title: item.title,
          url: item.url || "#",
          publishedAt: timeAgo,
          keywords: item.tags?.split("|").slice(0, 5) || [],
          sentiment: sentiment,
        };
      });
      setNewsData(formattedNews);
    } catch (error) {
      console.error("뉴스 로드 에러:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadNews();
    // 5분마다 자동 새로고침
    const interval = setInterval(loadNews, 300000);
    return () => clearInterval(interval);
  }, []);

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

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="text-center py-16">
          <div className="text-6xl mb-4 animate-spin">📰</div>
          <h3 className="text-[#eaecef] mb-2">뉴스를 불러오는 중...</h3>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between flex-wrap gap-4">
        <h2 className="text-[#eaecef]">Latest News</h2>

        <Button
          className="bg-gradient-to-r from-[#667eea] to-[#764ba2] hover:opacity-90 transition-opacity"
          onClick={loadNews}
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