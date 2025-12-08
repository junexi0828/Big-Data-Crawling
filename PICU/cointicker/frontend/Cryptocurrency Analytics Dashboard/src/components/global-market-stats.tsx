import { useEffect, useState } from "react";
import { TrendingUp, TrendingDown, Globe, DollarSign, BarChart3 } from "lucide-react";
import { externalAPI } from "../services/api";

interface GlobalMarketData {
  total_market_cap: { usd: number };
  total_volume: { usd: number };
  market_cap_percentage: { btc: number; eth: number };
  market_cap_change_percentage_24h_usd: number;
}

export function GlobalMarketStats() {
  const [data, setData] = useState<GlobalMarketData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      try {
        const response = await externalAPI.getGlobalMarketData();
        if (response && response.data) {
          setData(response.data);
        }
      } catch (error) {
        console.error("글로벌 시장 데이터 로드 에러:", error);
      } finally {
        setLoading(false);
      }
    };

    loadData();
    const interval = setInterval(loadData, 60000); // 1분마다 업데이트
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="bg-[#1e2329] border border-[#2b3139] rounded-xl p-6">
        <div className="text-center py-8 text-[#848e9c]">로딩 중...</div>
      </div>
    );
  }

  if (!data) {
    return null;
  }

  const formatCurrency = (value: number) => {
    if (value >= 1e12) return `$${(value / 1e12).toFixed(2)}T`;
    if (value >= 1e9) return `$${(value / 1e9).toFixed(2)}B`;
    if (value >= 1e6) return `$${(value / 1e6).toFixed(2)}M`;
    return `$${value.toLocaleString()}`;
  };

  return (
    <div className="bg-[#1e2329] border border-[#2b3139] rounded-xl p-6 hover:border-[#667eea]/50 transition-all shadow-lg hover:shadow-xl duration-300">
      <div className="flex items-center gap-2 mb-6">
        <Globe className="w-5 h-5 text-[#667eea]" />
        <h3 className="text-[#eaecef] text-lg font-bold">글로벌 시장 통계</h3>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-[#2b3139] rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <DollarSign className="w-4 h-4 text-[#848e9c]" />
            <span className="text-sm text-[#848e9c]">총 시가총액</span>
          </div>
          <div className="text-2xl font-bold text-[#eaecef]">
            {formatCurrency(data.total_market_cap.usd)}
          </div>
        </div>

        <div className="bg-[#2b3139] rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <BarChart3 className="w-4 h-4 text-[#848e9c]" />
            <span className="text-sm text-[#848e9c]">24h 거래량</span>
          </div>
          <div className="text-2xl font-bold text-[#eaecef]">
            {formatCurrency(data.total_volume.usd)}
          </div>
        </div>

        <div className="bg-[#2b3139] rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            {data.market_cap_change_percentage_24h_usd >= 0 ? (
              <TrendingUp className="w-4 h-4 text-[#43e97b]" />
            ) : (
              <TrendingDown className="w-4 h-4 text-[#ff6b6b]" />
            )}
            <span className="text-sm text-[#848e9c]">24h 변동률</span>
          </div>
          <div className={`text-2xl font-bold ${
            data.market_cap_change_percentage_24h_usd >= 0 ? "text-[#43e97b]" : "text-[#ff6b6b]"
          }`}>
            {data.market_cap_change_percentage_24h_usd >= 0 ? "+" : ""}
            {data.market_cap_change_percentage_24h_usd.toFixed(2)}%
          </div>
        </div>

        <div className="bg-[#2b3139] rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-sm text-[#848e9c]">BTC 지배율</span>
          </div>
          <div className="text-2xl font-bold text-[#eaecef]">
            {data.market_cap_percentage.btc.toFixed(1)}%
          </div>
          <div className="text-xs text-[#848e9c] mt-1">
            ETH: {data.market_cap_percentage.eth.toFixed(1)}%
          </div>
        </div>
      </div>
    </div>
  );
}

