import { useState, useEffect } from "react";
import { NewsCard } from "./news-card";
import { Button } from "./ui/button";
import { RefreshCw, Search } from "lucide-react";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";
import { Input } from "./ui/input";
import { DataExport } from "./data-export";
import { newsAPI, externalAPI } from "../services/api";

interface NewsItem {
  id: number | string;
  source: string;
  title: string;
  url: string;
  publishedAt: string;
  keywords: string[];
  sentiment: number;
  isBackend?: boolean;
}

export function NewsPage() {
  const [sourceFilter, setSourceFilter] = useState<string>("all");
  const [sentimentFilter, setSentimentFilter] = useState<string>("all");
  const [searchQuery, setSearchQuery] = useState<string>("");
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
      const backendNewsList: NewsItem[] = [];
      const externalNewsList: NewsItem[] = [];
      const seenUrls = new Set<string>();
      const seenTitles = new Set<string>();

      // 백엔드 API와 외부 API를 동시에 호출
      const [backendResult, externalResult] = await Promise.allSettled([
        newsAPI.getLatestNews(50),
        externalAPI.getCryptoNews(),
      ]);

      // 백엔드 뉴스 처리 (우선 처리)
      if (backendResult.status === "fulfilled" && backendResult.value?.news) {
        const backendNews = await Promise.all(
          backendResult.value.news.map(async (item: any) => {
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

            const urlKey = (item.url || "#").toLowerCase();
            const titleKey = (item.title || "").toLowerCase();

            // 백엔드 뉴스는 항상 추가 (중복 체크만 하고 기록)
            if (!seenUrls.has(urlKey) && !seenTitles.has(titleKey)) {
              seenUrls.add(urlKey);
              seenTitles.add(titleKey);
            }

            return {
              id: item.id,
              source: item.source || "Backend",
              title: item.title,
              url: item.url || "#",
              publishedAt: timeAgo,
              publishedAtRaw: publishedAt.getTime(),
              keywords: item.keywords || [],
              sentiment: sentiment,
              isBackend: true,
            };
          })
        );

        // 백엔드 뉴스는 모두 추가 (중복 제거 없이)
        backendNewsList.push(...backendNews);
      }

      // 외부 API 뉴스 처리 (백엔드와 중복되지 않는 것만)
      if (externalResult.status === "fulfilled" && externalResult.value) {
        const externalNews = externalResult.value.map((item: any, index: number) => {
          const timeDiff = Math.floor((Date.now() / 1000 - item.published_on) / 60);
          const timeAgo = timeDiff < 60
            ? `${timeDiff}분 전`
            : `${Math.floor(timeDiff / 60)}시간 전`;

          const sentiment = analyzeSentiment(item.title, item.body || "");

          return {
            id: `external_${item.id || index}`,
            source: item.source_info?.name || "External",
            title: item.title,
            url: item.url || "#",
            publishedAt: timeAgo,
            publishedAtRaw: item.published_on * 1000,
            keywords: item.tags?.split("|").slice(0, 5) || [],
            sentiment: sentiment,
            isBackend: false,
          };
        });

        // 외부 API 뉴스는 백엔드와 중복되지 않는 것만 추가
        externalNews.forEach((news) => {
          const urlKey = news.url.toLowerCase();
          const titleKey = news.title.toLowerCase();
          if (!seenUrls.has(urlKey) && !seenTitles.has(titleKey)) {
            seenUrls.add(urlKey);
            seenTitles.add(titleKey);
            externalNewsList.push(news);
          }
        });
      }

      // 백엔드 뉴스 그룹 내 정렬 (최신순)
      backendNewsList.sort((a, b) => {
        const aTime = (a as any).publishedAtRaw || 0;
        const bTime = (b as any).publishedAtRaw || 0;
        return bTime - aTime;
      });

      // 외부 API 뉴스 그룹 내 정렬 (최신순)
      externalNewsList.sort((a, b) => {
        const aTime = (a as any).publishedAtRaw || 0;
        const bTime = (b as any).publishedAtRaw || 0;
        return bTime - aTime;
      });

      // 백엔드 뉴스를 먼저, 그 다음 외부 API 뉴스
      const allNews = [...backendNewsList, ...externalNewsList];

      setNewsData(allNews.slice(0, 50)); // 최대 50개까지 표시
    } catch (error) {
      console.error("뉴스 로드 에러:", error);
      // 에러 시 더미 뉴스 데이터
      const dummyNews = [
        {
          id: 1,
          source: "perplexity_finance",
          title: "Coinbase 50 Index",
          url: "#",
          publishedAt: "10시간 전",
          keywords: ["코인베이스", "Cryptocurrency", "Crypto", "Index", "Market", "Trading", "Digital Assets", "Blockchain"],
          sentiment: 0,
        },
        {
          id: 2,
          source: "saveticker",
          title: "블룸버그 버블 논란 속에서도... 자산운용사 '주식 비중 유지' 블룸버그가 글로벌 자산운용사 39명을 인터뷰한 결과,",
          url: "#",
          publishedAt: "10시간 전",
          keywords: ["강세", "주식"],
          sentiment: 0,
        },
        {
          id: 3,
          source: "cryptonews",
          title: "Bitcoin Reaches New All-Time High Amid Institutional Adoption",
          url: "#",
          publishedAt: "2시간 전",
          keywords: ["Bitcoin", "BTC", "Institutional", "Adoption", "Bull Market"],
          sentiment: 0.5,
        },
        {
          id: 4,
          source: "coindesk",
          title: "Ethereum 2.0 Staking Reaches Milestone with 32 Million ETH",
          url: "#",
          publishedAt: "5시간 전",
          keywords: ["Ethereum", "ETH", "Staking", "Blockchain", "DeFi"],
          sentiment: 0.3,
        },
        {
          id: 5,
          source: "theblock",
          title: "Regulatory Concerns Impact Crypto Market Sentiment",
          url: "#",
          publishedAt: "8시간 전",
          keywords: ["Regulation", "Crypto", "Market", "Policy", "Compliance"],
          sentiment: -0.2,
        },
      ];
      setNewsData(dummyNews);
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
    const matchesSearch =
      !searchQuery ||
      news.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      news.keywords.some(k => k.toLowerCase().includes(searchQuery.toLowerCase()));

    return matchesSource && matchesSentiment && matchesSearch;
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
        <div>
          <h2 className="text-[#eaecef]">Latest News</h2>
          <p className="text-sm text-[#848e9c] mt-1">
            백엔드 뉴스와 외부 API 뉴스를 함께 표시합니다
          </p>
        </div>

        <div className="flex items-center gap-2">
          <DataExport data={filteredNews} filename="crypto-news" />
          <Button
            className="bg-gradient-to-r from-[#667eea] to-[#764ba2] hover:opacity-90 transition-opacity"
            onClick={loadNews}
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh
          </Button>
        </div>
      </div>

      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-[#848e9c]" />
        <Input
          type="text"
          placeholder="뉴스 검색..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="pl-10 bg-[#2b3139] border-[#2b3139] text-[#eaecef] placeholder:text-[#848e9c]"
        />
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