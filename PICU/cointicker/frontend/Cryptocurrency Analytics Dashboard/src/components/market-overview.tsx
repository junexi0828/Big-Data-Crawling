import { useEffect, useState } from "react";
import { TrendingUp, TrendingDown, BarChart3, Activity } from "lucide-react";
import { externalAPI } from "../services/api";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

export function MarketOverview() {
  const [marketData, setMarketData] = useState<any>(null);
  const [historicalData, setHistoricalData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadMarketData();
    const interval = setInterval(loadMarketData, 60000);
    return () => clearInterval(interval);
  }, []);

  const loadMarketData = async () => {
    setLoading(true);
    try {
      const [global, btcHistory] = await Promise.all([
        externalAPI.getGlobalMarketData(),
        externalAPI.getCoinHistory('bitcoin', 7)
      ]);

      if (global && global.data) {
        setMarketData(global.data);
      }

      if (btcHistory && btcHistory.market_caps) {
        const formatted = btcHistory.market_caps.map(([timestamp, value]: [number, number]) => ({
          time: new Date(timestamp).toLocaleDateString('ko-KR', { month: 'short', day: 'numeric' }),
          marketCap: value / 1e12, // T 단위로 변환
        }));
        setHistoricalData(formatted);
      }
    } catch (error) {
      console.error("시장 개요 데이터 로드 에러:", error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="bg-[#1e2329] border border-[#2b3139] rounded-xl p-6">
        <div className="text-center py-8 text-[#848e9c]">로딩 중...</div>
      </div>
    );
  }

  if (!marketData) return null;

  const formatCurrency = (value: number) => {
    if (value >= 1e12) return `$${(value / 1e12).toFixed(2)}T`;
    if (value >= 1e9) return `$${(value / 1e9).toFixed(2)}B`;
    return `$${value.toLocaleString()}`;
  };

  return (
    <div className="bg-[#1e2329] border border-[#2b3139] rounded-xl p-6 hover:border-[#667eea]/50 transition-all shadow-lg hover:shadow-xl duration-300">
      <h3 className="text-[#eaecef] text-lg font-bold mb-6">시장 개요</h3>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-[#2b3139] rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <BarChart3 className="w-4 h-4 text-[#848e9c]" />
            <span className="text-xs text-[#848e9c]">총 시가총액</span>
          </div>
          <div className="text-xl font-bold text-[#eaecef]">
            {formatCurrency(marketData.total_market_cap.usd)}
          </div>
        </div>

        <div className="bg-[#2b3139] rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <Activity className="w-4 h-4 text-[#848e9c]" />
            <span className="text-xs text-[#848e9c]">24h 거래량</span>
          </div>
          <div className="text-xl font-bold text-[#eaecef]">
            {formatCurrency(marketData.total_volume.usd)}
          </div>
        </div>

        <div className="bg-[#2b3139] rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            {marketData.market_cap_change_percentage_24h_usd >= 0 ? (
              <TrendingUp className="w-4 h-4 text-[#43e97b]" />
            ) : (
              <TrendingDown className="w-4 h-4 text-[#ff6b6b]" />
            )}
            <span className="text-xs text-[#848e9c]">24h 변동</span>
          </div>
          <div className={`text-xl font-bold ${
            marketData.market_cap_change_percentage_24h_usd >= 0 ? "text-[#43e97b]" : "text-[#ff6b6b]"
          }`}>
            {marketData.market_cap_change_percentage_24h_usd >= 0 ? "+" : ""}
            {marketData.market_cap_change_percentage_24h_usd.toFixed(2)}%
          </div>
        </div>

        <div className="bg-[#2b3139] rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-xs text-[#848e9c]">BTC 지배율</span>
          </div>
          <div className="text-xl font-bold text-[#eaecef]">
            {marketData.market_cap_percentage.btc.toFixed(1)}%
          </div>
          <div className="text-xs text-[#848e9c] mt-1">
            ETH: {marketData.market_cap_percentage.eth.toFixed(1)}%
          </div>
        </div>
      </div>

      {/* 시가총액 추이 차트 */}
      {historicalData.length > 0 && (
        <div>
          <h4 className="text-[#848e9c] text-sm mb-3">BTC 시가총액 추이 (7일)</h4>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={historicalData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#2b3139" />
              <XAxis dataKey="time" stroke="#848e9c" tick={{ fill: "#848e9c", fontSize: 10 }} />
              <YAxis stroke="#848e9c" tick={{ fill: "#848e9c", fontSize: 10 }} />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#1e2329',
                  border: '1px solid #2b3139',
                  borderRadius: '8px'
                }}
                formatter={(value: number) => `$${value.toFixed(2)}T`}
              />
              <Line
                type="monotone"
                dataKey="marketCap"
                stroke="#667eea"
                strokeWidth={2}
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}

