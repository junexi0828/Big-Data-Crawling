import { useEffect, useState, useCallback } from "react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Area, AreaChart } from "recharts";
import { externalAPI } from "../services/api";

interface AdvancedChartProps {
  coinId: string;
  days?: number;
}

export function AdvancedChart({ coinId, days = 7 }: AdvancedChartProps) {
  const [chartData, setChartData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedPeriod, setSelectedPeriod] = useState<number>(days);

  const loadChartData = useCallback(async () => {
    setLoading(true);
    try {
      const data = await externalAPI.getCoinHistory(coinId, selectedPeriod);
      if (data && data.prices) {
        const formatted = data.prices.map(([timestamp, price]: [number, number]) => ({
          time: new Date(timestamp).toLocaleDateString('ko-KR', { month: 'short', day: 'numeric' }),
          price: price,
          volume: data.total_volumes?.find(([t]: [number, number]) => t === timestamp)?.[1] || 0,
        }));
        setChartData(formatted);
      }
    } catch (error) {
      console.error("차트 데이터 로드 에러:", error);
    } finally {
      setLoading(false);
    }
  }, [coinId, selectedPeriod]);

  useEffect(() => {
    loadChartData();
  }, [loadChartData]);

  if (loading) {
    return (
      <div className="bg-[#1e2329] border border-[#2b3139] rounded-xl p-6">
        <div className="text-center py-8 text-[#848e9c]">로딩 중...</div>
      </div>
    );
  }

  return (
    <div className="bg-[#1e2329] border border-[#2b3139] rounded-xl p-6 hover:border-[#667eea]/50 transition-all shadow-lg hover:shadow-xl duration-300">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-[#eaecef] text-lg font-bold">고급 가격 차트</h3>
        <div className="flex gap-2">
          {[1, 7, 30, 90, 365].map((period) => (
            <button
              key={period}
              onClick={() => setSelectedPeriod(period)}
              className={`px-3 py-1 rounded-lg text-sm transition-all ${
                selectedPeriod === period
                  ? "bg-gradient-to-r from-[#667eea] to-[#764ba2] text-white"
                  : "bg-[#2b3139] text-[#848e9c] hover:text-[#eaecef]"
              }`}
            >
              {period === 1 ? "24h" : period === 7 ? "7d" : period === 30 ? "30d" : period === 90 ? "90d" : "1y"}
            </button>
          ))}
        </div>
      </div>

      <ResponsiveContainer width="100%" height={400}>
        <AreaChart data={chartData}>
          <defs>
            <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#667eea" stopOpacity={0.3}/>
              <stop offset="95%" stopColor="#667eea" stopOpacity={0}/>
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#2b3139" />
          <XAxis dataKey="time" stroke="#848e9c" tick={{ fill: "#848e9c", fontSize: 12 }} />
          <YAxis stroke="#848e9c" tick={{ fill: "#848e9c", fontSize: 12 }} />
          <Tooltip
            contentStyle={{
              backgroundColor: '#1e2329',
              border: '1px solid #2b3139',
              borderRadius: '8px'
            }}
          />
          <Area
            type="monotone"
            dataKey="price"
            stroke="#667eea"
            fillOpacity={1}
            fill="url(#colorPrice)"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}

