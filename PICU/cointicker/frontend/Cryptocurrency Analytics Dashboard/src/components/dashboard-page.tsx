import { useState, useEffect } from "react";
import { SummaryCard } from "./summary-card";
import { FearGreedGauge } from "./fear-greed-gauge";
import { TopCoinsTable } from "./top-coins-table";
import { SentimentTimeline } from "./sentiment-timeline";
import { LatestInsights } from "./latest-insights";
import { PriceChart } from "./price-chart";
import { GlobalMarketStats } from "./global-market-stats";
import { TrendingCoins } from "./trending-coins";
import { MarketCategories } from "./market-categories";
import { DefiStats } from "./defi-stats";
import { CoinComparison } from "./coin-comparison";
import { PriceAlerts } from "./price-alerts";
import { PortfolioTracker } from "./portfolio-tracker";
import { RealTimeIndicator } from "./real-time-indicator";
import { MarketOverview } from "./market-overview";
import { PerformanceMetrics } from "./performance-metrics";
import { QuickStats } from "./quick-stats";
import {
  dashboardAPI,
  insightsAPI,
  newsAPI,
  externalAPI,
} from "../services/api";

// Define a basic type for the summary data for better type safety
interface SummaryData {
  totalNews: number;
  avgSentiment: number;
  sentimentTrend: "up" | "down";
  sentimentTrendValue: string;
  recentInsights: number;
  activeSources: number;
  fearGreedValue: number;
  topCoins: any[]; // Replace 'any' with a proper type later
}

export function DashboardPage() {
  // State for our data and loading status
  const [summary, setSummary] = useState<SummaryData | null>(null);
  const [sentiment24h, setSentiment24h] = useState([]);
  const [sentiment7d, setSentiment7d] = useState([]);
  const [sentiment30d, setSentiment30d] = useState([]);
  const [insights, setInsights] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [fearGreedValue, setFearGreedValue] = useState(50);

  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        setError(null);

        // 백엔드 API 시도
        let summaryData,
          sentiment24hData,
          sentiment7dData,
          sentiment30dData,
          insightsData;
        let totalNewsCount = 0;
        let activeSourcesCount = 0;
        let topCoinsData: any[] = [];

        // 백엔드 API 호출 (실패해도 계속 진행)
        const [
          summaryResult,
          sentiment24hResult,
          sentiment7dResult,
          sentiment30dResult,
          insightsResult,
        ] = await Promise.allSettled([
          dashboardAPI.getSummary(),
          dashboardAPI.getSentimentTimeline(1),
          dashboardAPI.getSentimentTimeline(7),
          dashboardAPI.getSentimentTimeline(30),
          insightsAPI.getRecentInsights(5),
        ]);

        summaryData =
          summaryResult.status === "fulfilled" ? summaryResult.value : null;
        sentiment24hData =
          sentiment24hResult.status === "fulfilled"
            ? sentiment24hResult.value
            : null;
        sentiment7dData =
          sentiment7dResult.status === "fulfilled"
            ? sentiment7dResult.value
            : null;
        sentiment30dData =
          sentiment30dResult.status === "fulfilled"
            ? sentiment30dResult.value
            : null;
        insightsData =
          insightsResult.status === "fulfilled" ? insightsResult.value : null;

        // 뉴스 데이터 가져오기 (백엔드 우선, 실패 시 외부 API)
        try {
          const newsData = await newsAPI.getLatestNews(100);
          if (newsData?.news && newsData.news.length > 0) {
            totalNewsCount = newsData.news.length;
            activeSourcesCount = new Set(
              newsData.news.map((n: any) => n.source).filter(Boolean)
            ).size;
          } else {
            throw new Error("No news data");
          }
        } catch (e) {
          console.log("백엔드 뉴스 실패, 외부 API 사용");
          try {
            const externalNews = await externalAPI.getCryptoNews();
            if (externalNews && externalNews.length > 0) {
              totalNewsCount = externalNews.length;
              activeSourcesCount = new Set(
                externalNews
                  .map((n: any) => n.source_info?.name)
                  .filter(Boolean)
              ).size;
            }
          } catch (err) {
            console.error("외부 뉴스 API도 실패:", err);
          }
        }

        // Top Coins 데이터 가져오기 (백엔드 우선, 실패 시 외부 API)
        if (
          summaryData?.top_volume_coins &&
          summaryData.top_volume_coins.length > 0
        ) {
          topCoinsData = summaryData.top_volume_coins;
        } else {
          console.log("백엔드 Top Coins 없음, 외부 API 사용");
          try {
            const externalCoins = await externalAPI.getCoinPrices();
            if (externalCoins && externalCoins.length > 0) {
              topCoinsData = externalCoins.slice(0, 5).map((coin: any) => ({
                symbol: (coin.symbol || "?").toUpperCase(),
                volume24h: coin.total_volume || 0,
                change24h: coin.price_change_percentage_24h || 0,
                price: coin.current_price || 0,
                coinId: coin.id || "",
              }));
            }
          } catch (err) {
            console.error("외부 코인 API 실패:", err);
          }
        }

        // Insights 데이터 가져오기 (백엔드 우선, 실패 시 더미 데이터)
        if (!insightsData?.insights || insightsData.insights.length === 0) {
          console.log("백엔드 Insights 없음, 더미 데이터 사용");
          insightsData = {
            insights: [
              {
                id: 1,
                type: "trend_reversal",
                symbol: "ADA",
                description: "ADA 추세 반전 신호: RSI 과매수, MACD 상승",
                severity: "high",
                created_at: new Date().toISOString(),
              },
              {
                id: 2,
                type: "trend_reversal",
                symbol: "ADA",
                description: "ADA 추세 반전 신호: RSI 과매수, MACD 상승",
                severity: "high",
                created_at: new Date(Date.now() - 6 * 60000).toISOString(),
              },
              {
                id: 3,
                type: "trend_reversal",
                symbol: "ADA",
                description: "ADA 추세 반전 신호: RSI 과매수, MACD 상승",
                severity: "high",
                created_at: new Date(Date.now() - 6 * 60000).toISOString(),
              },
            ],
          };
        }

        // Sentiment 데이터 확인 및 더미 데이터 생성
        const generateDummySentiment = (
          hours: number
        ): Array<{ timestamp: string; sentiment: number; count: number }> => {
          const now = new Date();
          const timeline: Array<{
            timestamp: string;
            sentiment: number;
            count: number;
          }> = [];
          const interval = hours <= 24 ? 1 : hours <= 168 ? 6 : 24;

          for (let i = hours; i >= 0; i -= interval) {
            const timestamp = new Date(now.getTime() - i * 60 * 60 * 1000);
            const baseSentiment = Math.sin(i / 10) * 0.3;
            timeline.push({
              timestamp: timestamp.toISOString(),
              sentiment: baseSentiment,
              count: Math.floor(Math.random() * 100) + 50,
            });
          }
          return timeline;
        };

        if (
          !sentiment24hData?.timeline ||
          sentiment24hData.timeline.length === 0
        ) {
          sentiment24hData = { timeline: generateDummySentiment(24) };
        }
        if (
          !sentiment7dData?.timeline ||
          sentiment7dData.timeline.length === 0
        ) {
          sentiment7dData = { timeline: generateDummySentiment(168) };
        }
        if (
          !sentiment30dData?.timeline ||
          sentiment30dData.timeline.length === 0
        ) {
          sentiment30dData = { timeline: generateDummySentiment(720) };
        }

        // Summary 데이터 확인 및 기본값 설정
        if (!summaryData) {
          summaryData = {
            fear_greed_index: { value: 20, classification: "Extreme Fear" },
            sentiment_average: 0.15,
            top_volume_coins: [
              {
                symbol: "BTC",
                volume24h: 28500000000,
                change24h: 1.78,
                price: 91039.18,
              },
              {
                symbol: "ETH",
                volume24h: 15200000000,
                change24h: 1.63,
                price: 3096.82,
              },
              {
                symbol: "BNB",
                volume24h: 2100000000,
                change24h: -0.45,
                price: 585.23,
              },
              {
                symbol: "SOL",
                volume24h: 3200000000,
                change24h: 2.15,
                price: 142.56,
              },
              {
                symbol: "ADA",
                volume24h: 850000000,
                change24h: 0.92,
                price: 0.48,
              },
            ],
            latest_insights: [],
          };
        }

        // API 응답 구조를 프론트엔드 형식으로 변환
        const transformedSummary: SummaryData = {
          totalNews: totalNewsCount,
          avgSentiment: summaryData?.sentiment_average || 0,
          sentimentTrend:
            (summaryData?.sentiment_average || 0) >= 0 ? "up" : "down",
          sentimentTrendValue: `${
            (summaryData?.sentiment_average || 0) >= 0 ? "+" : ""
          }${(summaryData?.sentiment_average || 0).toFixed(2)}`,
          recentInsights:
            insightsData?.insights?.length ||
            summaryData?.latest_insights?.length ||
            0,
          activeSources: activeSourcesCount,
          fearGreedValue: summaryData?.fear_greed_index?.value || 50,
          topCoins:
            topCoinsData.length > 0
              ? topCoinsData
              : summaryData?.top_volume_coins || [],
        };
        setSummary(transformedSummary);
        // API 응답 구조에 맞게 데이터 추출
        setSentiment24h(sentiment24hData?.timeline || []);
        setSentiment7d(sentiment7dData?.timeline || []);
        setSentiment30d(sentiment30dData?.timeline || []);
        setInsights(insightsData?.insights || []);

        // Fear & Greed Index 가져오기 (Alternative.me API)
        try {
          const fearGreed = await externalAPI.getFearGreedIndex();
          if (fearGreed && fearGreed.value) {
            setFearGreedValue(parseInt(fearGreed.value));
          }
        } catch (e) {
          console.log("Fear & Greed Index 로드 실패, 기본값 사용");
        }
      } catch (err) {
        console.error("Failed to load dashboard data:", err);
        setError(
          "Failed to load data. Please make sure the backend server is running."
        );
      } finally {
        setLoading(false);
      }
    };

    loadData();
    // 30초마다 자동 새로고침
    const interval = setInterval(loadData, 30000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="text-center p-10">
        <div className="text-6xl mb-4 animate-spin">📊</div>
        <p className="text-[#eaecef] text-lg">대시보드를 불러오는 중...</p>
        <p className="text-[#848e9c] text-sm mt-2">잠시만 기다려주세요</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center p-10">
        <div className="text-6xl mb-4">⚠️</div>
        <p className="text-red-500 text-lg mb-2">{error}</p>
        <p className="text-[#848e9c] text-sm">
          외부 API로 데이터를 불러오는 중...
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* 실시간 인디케이터 & 성능 메트릭 */}
      <div className="flex items-center justify-between flex-wrap gap-4">
        <PerformanceMetrics />
        <RealTimeIndicator />
      </div>

      {/* 퀵 스탯 */}
      <QuickStats />

      {/* 시장 개요 */}
      <MarketOverview />

      {/* 글로벌 시장 통계 */}
      <GlobalMarketStats />

      {/* Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <SummaryCard
          icon="📰"
          label="Total News"
          value={summary?.totalNews?.toLocaleString() ?? "N/A"}
          color="#667eea"
        />
        <SummaryCard
          icon="😊"
          label="Avg Sentiment"
          value={summary?.avgSentiment?.toFixed(2) ?? "N/A"}
          color="#f093fb"
          trend={summary?.sentimentTrend}
          trendValue={summary?.sentimentTrendValue}
        />
        <SummaryCard
          icon="💡"
          label="Recent Insights"
          value={summary?.recentInsights?.toLocaleString() ?? "N/A"}
          color="#4facfe"
        />
        <SummaryCard
          icon="🔗"
          label="Active Sources"
          value={summary?.activeSources?.toLocaleString() ?? "N/A"}
          color="#43e97b"
        />
      </div>

      {/* Key Metrics & Trending */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        <FearGreedGauge value={fearGreedValue} />
        <TopCoinsTable coins={summary?.topCoins ?? []} />
        <TrendingCoins />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        <div className="lg:col-span-2">
          <SentimentTimeline
            data24h={sentiment24h}
            data7d={sentiment7d}
            data30d={sentiment30d}
          />
        </div>
        <LatestInsights insights={insights} />
      </div>

      {/* Market Categories & DeFi Stats */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        <MarketCategories />
        <DefiStats />
      </div>

      {/* 가격 차트 (기본 BTC) */}
      <PriceChart
        symbol={
          summary?.topCoins && summary.topCoins.length > 0
            ? summary.topCoins[0].symbol?.replace("/", "") || "BTCUSDT"
            : "BTCUSDT"
        }
        interval="1h"
      />

      {/* 고급 기능 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        <CoinComparison />
        <PriceAlerts />
      </div>

      {/* 포트폴리오 추적 */}
      <PortfolioTracker />
    </div>
  );
}
