import { useState, useEffect } from "react";
import { SummaryCard } from "./summary-card";
import { FearGreedGauge } from "./fear-greed-gauge";
import { TopCoinsTable } from "./top-coins-table";
import { SentimentTimeline } from "./sentiment-timeline";
import { LatestInsights } from "./latest-insights";
import { PriceChart } from "./price-chart";
import { dashboardAPI, insightsAPI, newsAPI, externalAPI } from "../services/api";

// Define a basic type for the summary data for better type safety
interface SummaryData {
  totalNews: number;
  avgSentiment: number;
  sentimentTrend: 'up' | 'down';
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

  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        setError(null);

        // 백엔드 API 시도
        let summaryData, sentiment24hData, sentiment7dData, sentiment30dData, insightsData;
        let totalNewsCount = 0;
        let activeSourcesCount = 0;

        try {
          [summaryData, sentiment24hData, sentiment7dData, sentiment30dData, insightsData] = await Promise.allSettled([
            dashboardAPI.getSummary(),
            dashboardAPI.getSentimentTimeline(1),
            dashboardAPI.getSentimentTimeline(7),
            dashboardAPI.getSentimentTimeline(30),
            insightsAPI.getRecentInsights(5),
          ]).then(results => results.map(r => r.status === 'fulfilled' ? r.value : null));

          // 뉴스 개수 가져오기
          try {
            const newsData = await newsAPI.getLatestNews(100);
            totalNewsCount = newsData.news?.length || 0;
            activeSourcesCount = new Set(newsData.news?.map((n: any) => n.source) || []).size;
          } catch (e) {
            console.log("백엔드 뉴스 실패, 외부 API 사용");
            // 백엔드 뉴스 실패 시 외부 API 사용
            const externalNews = await externalAPI.getCryptoNews();
            totalNewsCount = externalNews.length;
            activeSourcesCount = new Set(externalNews.map((n: any) => n.source_info?.name).filter(Boolean)).size;
          }
        } catch (err) {
          console.log("백엔드 API 실패, 외부 API 사용", err);
          // 외부 API로 대체
          try {
            const externalNews = await externalAPI.getCryptoNews();
            totalNewsCount = externalNews.length;
            activeSourcesCount = new Set(externalNews.map((n: any) => n.source_info?.name).filter(Boolean)).size;
          } catch (e) {
            console.error("외부 API도 실패:", e);
          }

          // 외부 API로 기본 데이터 생성
          summaryData = summaryData || {
            fear_greed_index: { value: 50, classification: "Neutral" },
            sentiment_average: 0,
            top_volume_coins: [],
            latest_insights: []
          };
          sentiment24hData = sentiment24hData || { timeline: [] };
          sentiment7dData = sentiment7dData || { timeline: [] };
          sentiment30dData = sentiment30dData || { timeline: [] };
          insightsData = insightsData || { insights: [] };
        }

        // API 응답 구조를 프론트엔드 형식으로 변환
        const transformedSummary: SummaryData = {
          totalNews: totalNewsCount,
          avgSentiment: summaryData?.sentiment_average || 0,
          sentimentTrend: (summaryData?.sentiment_average || 0) >= 0 ? 'up' : 'down',
          sentimentTrendValue: `${(summaryData?.sentiment_average || 0) >= 0 ? '+' : ''}${(summaryData?.sentiment_average || 0).toFixed(2)}`,
          recentInsights: insightsData?.insights?.length || summaryData?.latest_insights?.length || 0,
          activeSources: activeSourcesCount,
          fearGreedValue: summaryData?.fear_greed_index?.value || 50,
          topCoins: summaryData?.top_volume_coins || []
        };
        setSummary(transformedSummary);
        // API 응답 구조에 맞게 데이터 추출
        setSentiment24h(sentiment24hData?.timeline || []);
        setSentiment7d(sentiment7dData?.timeline || []);
        setSentiment30d(sentiment30dData?.timeline || []);
        setInsights(insightsData?.insights || []);
      } catch (err) {
        console.error("Failed to load dashboard data:", err);
        setError("Failed to load data. Please make sure the backend server is running.");
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
        <p className="text-[#848e9c] text-sm">외부 API로 데이터를 불러오는 중...</p>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <SummaryCard
          icon="📰"
          label="Total News"
          value={summary?.totalNews?.toLocaleString() ?? 'N/A'}
          color="#667eea"
        />
        <SummaryCard
          icon="😊"
          label="Avg Sentiment"
          value={summary?.avgSentiment?.toFixed(2) ?? 'N/A'}
          color="#f093fb"
          trend={summary?.sentimentTrend}
          trendValue={summary?.sentimentTrendValue}
        />
        <SummaryCard
          icon="💡"
          label="Recent Insights"
          value={summary?.recentInsights?.toLocaleString() ?? 'N/A'}
          color="#4facfe"
        />
        <SummaryCard
          icon="🔗"
          label="Active Sources"
          value={summary?.activeSources?.toLocaleString() ?? 'N/A'}
          color="#43e97b"
        />
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        <FearGreedGauge value={summary?.fearGreedValue ?? 50} />
        <TopCoinsTable coins={summary?.topCoins ?? []} />
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

      {/* 가격 차트 (기본 BTC) */}
      <PriceChart
        symbol={summary?.topCoins && summary.topCoins.length > 0
          ? (summary.topCoins[0].symbol?.replace('/', '') || "BTCUSDT")
          : "BTCUSDT"
        }
        interval="1h"
      />
    </div>
  );
}
