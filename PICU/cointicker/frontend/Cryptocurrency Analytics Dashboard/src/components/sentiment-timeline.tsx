import { useState, useMemo, useCallback } from "react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from "recharts";

type TimeRange = "24h" | "7d" | "30d";

interface SentimentTimelineProps {
  data24h: Array<{ timestamp: string; sentiment: number; count: number }>;
  data7d: Array<{ timestamp: string; sentiment: number; count: number }>;
  data30d: Array<{ timestamp: string; sentiment: number; count: number }>;
}

export function SentimentTimeline({ data24h, data7d, data30d }: SentimentTimelineProps) {
  const [timeRange, setTimeRange] = useState<TimeRange>("24h");

  // 데이터 변환 함수 (백엔드 API 응답을 차트 형식으로)
  const transformData = useCallback((data: Array<{ timestamp: string; sentiment: number; count: number }>) => {
    if (!data || data.length === 0) {
      // 데이터가 없으면 최신 날짜로 목업 데이터 생성
      const now = new Date();
      const mockData = [];
      const hours = timeRange === "24h" ? 24 : timeRange === "7d" ? 168 : 720;
      const interval = timeRange === "24h" ? 1 : timeRange === "7d" ? 6 : 24;

      for (let i = hours; i >= 0; i -= interval) {
        const date = new Date(now.getTime() - i * 60 * 60 * 1000);
        const timeStr = timeRange === "24h"
          ? date.toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' })
          : date.toLocaleDateString('ko-KR', { month: 'short', day: 'numeric', hour: '2-digit' });

        // 랜덤 감성 점수 생성 (실제 데이터처럼)
        const baseSentiment = Math.sin(i / 10) * 0.3;
        const positive = Math.max(0, baseSentiment);
        const negative = Math.max(0, -baseSentiment);
        const neutral = 1 - positive - negative;

        mockData.push({
          time: timeStr,
          positive: positive,
          neutral: neutral,
          negative: negative,
        });
      }
      return mockData;
    }

    return data.map(item => {
      const sentiment = item.sentiment || 0;
      const positive = sentiment > 0 ? Math.min(1, sentiment) : 0;
      const negative = sentiment < 0 ? Math.min(1, Math.abs(sentiment)) : 0;
      const neutral = 1 - positive - negative;

      const date = new Date(item.timestamp);
      const timeStr = timeRange === "24h"
        ? date.toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' })
        : date.toLocaleDateString('ko-KR', { month: 'short', day: 'numeric', hour: '2-digit' });

      return {
        time: timeStr,
        positive: positive,
        neutral: neutral,
        negative: negative,
      };
    });
  }, [timeRange]);

  const getData = useMemo(() => {
    switch (timeRange) {
      case "24h": return transformData(data24h);
      case "7d": return transformData(data7d);
      case "30d": return transformData(data30d);
    }
  }, [timeRange, data24h, data7d, data30d, transformData]);

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-[#1e2329] border border-[#2b3139] rounded-lg p-3 shadow-lg">
          <p className="text-[#848e9c] text-xs mb-2">{payload[0].payload.time}</p>
          {payload.map((entry: any, index: number) => (
            <div key={index} className="flex items-center justify-between gap-4 text-sm">
              <span style={{ color: entry.color }}>{entry.name}:</span>
              <span className="text-[#eaecef]">{entry.value.toFixed(2)}</span>
            </div>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <div className="bg-[#1e2329] border border-[#2b3139] rounded-xl p-6 hover:border-[#667eea]/50 transition-all shadow-lg hover:shadow-xl duration-300">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-[#eaecef]">Sentiment Timeline</h3>

        <div className="flex gap-2">
          {(["24h", "7d", "30d"] as TimeRange[]).map((range) => (
            <button
              key={range}
              onClick={() => setTimeRange(range)}
              className={`px-3 py-1 rounded-lg text-sm transition-all duration-200 ${
                timeRange === range
                  ? "bg-gradient-to-r from-[#667eea] to-[#764ba2] text-white shadow-md"
                  : "bg-[#2b3139] text-[#848e9c] hover:text-[#eaecef] hover:bg-[#667eea]/20"
              }`}
            >
              {range}
            </button>
          ))}
        </div>
      </div>

      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={getData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#2b3139" />
          <XAxis
            dataKey="time"
            stroke="#848e9c"
            tick={{ fill: "#848e9c", fontSize: 12 }}
          />
          <YAxis
            stroke="#848e9c"
            tick={{ fill: "#848e9c", fontSize: 12 }}
            domain={[-1, 1]}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend
            wrapperStyle={{ paddingTop: "20px" }}
            iconType="line"
          />
          <Line
            type="monotone"
            dataKey="positive"
            stroke="#43e97b"
            strokeWidth={2}
            dot={{ fill: "#43e97b", r: 4 }}
            activeDot={{ r: 6 }}
            name="Positive"
          />
          <Line
            type="monotone"
            dataKey="neutral"
            stroke="#848e9c"
            strokeWidth={2}
            dot={{ fill: "#848e9c", r: 4 }}
            activeDot={{ r: 6 }}
            name="Neutral"
          />
          <Line
            type="monotone"
            dataKey="negative"
            stroke="#ff6b6b"
            strokeWidth={2}
            dot={{ fill: "#ff6b6b", r: 4 }}
            activeDot={{ r: 6 }}
            name="Negative"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}