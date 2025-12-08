import { useEffect, useState, useCallback } from "react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from "recharts";
import { externalAPI } from "../services/api";

interface PriceChartProps {
  symbol: string; // 예: "BTCUSDT"
  interval?: string; // "1m", "5m", "15m", "1h", "4h", "1d", "1w"
}

interface CandleData {
  time: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export function PriceChart({ symbol, interval = "1h" }: PriceChartProps) {
  const [candleData, setCandleData] = useState<CandleData[]>([]);
  const [volumeData, setVolumeData] = useState<Array<{ time: string; volume: number }>>([]);
  const [loading, setLoading] = useState(true);
  const [currentInterval, setCurrentInterval] = useState(interval);

  const loadChartData = useCallback(async () => {
    setLoading(true);
    try {
      // Binance API로 캔들 데이터 가져오기
      const binanceSymbol = symbol.replace('/', '').toUpperCase();
      const intervalMap: { [key: string]: string } = {
        '1m': '1m',
        '5m': '5m',
        '15m': '15m',
        '1h': '1h',
        '4h': '4h',
        '1d': '1d',
        '1w': '1w'
      };
      const binanceInterval = intervalMap[currentInterval] || '1h';
      const limit = currentInterval === '1w' ? 52 : currentInterval === '1d' ? 30 : 100;

      const response = await fetch(
        `https://api.binance.com/api/v3/klines?symbol=${binanceSymbol}&interval=${binanceInterval}&limit=${limit}`
      );

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      const candles: CandleData[] = data.map((candle: any[]) => ({
        time: new Date(candle[0]).toLocaleString('ko-KR', {
          month: 'short',
          day: 'numeric',
          hour: '2-digit',
          minute: '2-digit'
        }),
        open: parseFloat(candle[1]),
        high: parseFloat(candle[2]),
        low: parseFloat(candle[3]),
        close: parseFloat(candle[4]),
        volume: parseFloat(candle[5]),
      }));

      setCandleData(candles);
      setVolumeData(candles.map(c => ({ time: c.time, volume: c.volume })));
    } catch (error) {
      console.error("차트 데이터 로드 에러:", error);
    } finally {
      setLoading(false);
    }
  }, [symbol, currentInterval]);

  useEffect(() => {
    loadChartData();
    // 1분마다 업데이트
    const intervalId = setInterval(loadChartData, 60000);
    return () => clearInterval(intervalId);
  }, [loadChartData]);

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-[#1e2329] border border-[#2b3139] rounded-lg p-3 shadow-lg">
          <p className="text-[#848e9c] text-xs mb-2">{data.time}</p>
          <div className="space-y-1 text-sm">
            <div className="flex justify-between gap-4">
              <span className="text-[#848e9c]">시가:</span>
              <span className="text-[#eaecef]">${data.open.toLocaleString()}</span>
            </div>
            <div className="flex justify-between gap-4">
              <span className="text-[#848e9c]">고가:</span>
              <span className="text-[#43e97b]">${data.high.toLocaleString()}</span>
            </div>
            <div className="flex justify-between gap-4">
              <span className="text-[#848e9c]">저가:</span>
              <span className="text-[#ff6b6b]">${data.low.toLocaleString()}</span>
            </div>
            <div className="flex justify-between gap-4">
              <span className="text-[#848e9c]">종가:</span>
              <span className="text-[#eaecef]">${data.close.toLocaleString()}</span>
            </div>
            {data.volume && (
              <div className="flex justify-between gap-4">
                <span className="text-[#848e9c]">거래량:</span>
                <span className="text-[#eaecef]">${(data.volume / 1e6).toFixed(2)}M</span>
              </div>
            )}
          </div>
        </div>
      );
    }
    return null;
  };

  if (loading && candleData.length === 0) {
    return (
      <div className="bg-[#1e2329] border border-[#2b3139] rounded-xl p-6">
        <div className="text-center py-16">
          <div className="text-6xl mb-4 animate-spin">📈</div>
          <p className="text-[#848e9c]">차트 데이터를 불러오는 중...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-[#1e2329] border border-[#2b3139] rounded-xl p-6 hover:border-[#667eea]/50 transition-all shadow-lg hover:shadow-xl duration-300">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-[#eaecef] text-xl font-bold">{symbol} 가격 차트</h3>

        <div className="flex gap-2">
          {['1m', '5m', '15m', '1h', '4h', '1d', '1w'].map((int) => (
            <button
              key={int}
              onClick={() => setCurrentInterval(int)}
              className={`px-3 py-1 rounded-lg text-sm transition-all duration-200 ${
                currentInterval === int
                  ? "bg-gradient-to-r from-[#667eea] to-[#764ba2] text-white shadow-md"
                  : "bg-[#2b3139] text-[#848e9c] hover:text-[#eaecef] hover:bg-[#667eea]/20"
              }`}
            >
              {int}
            </button>
          ))}
        </div>
      </div>

      {/* 가격 차트 */}
      <div className="mb-4">
        <ResponsiveContainer width="100%" height={400}>
          <LineChart data={candleData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#2b3139" />
            <XAxis
              dataKey="time"
              stroke="#848e9c"
              tick={{ fill: "#848e9c", fontSize: 11 }}
              angle={-45}
              textAnchor="end"
              height={80}
            />
            <YAxis
              stroke="#848e9c"
              tick={{ fill: "#848e9c", fontSize: 12 }}
              domain={['auto', 'auto']}
            />
            <Tooltip content={<CustomTooltip />} />
            <Line
              type="monotone"
              dataKey="close"
              stroke="#667eea"
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 6, fill: "#667eea" }}
              name="가격"
            />
            <Line
              type="monotone"
              dataKey="high"
              stroke="#43e97b"
              strokeWidth={1}
              dot={false}
              strokeDasharray="3 3"
              name="고가"
            />
            <Line
              type="monotone"
              dataKey="low"
              stroke="#ff6b6b"
              strokeWidth={1}
              dot={false}
              strokeDasharray="3 3"
              name="저가"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* 거래량 차트 */}
      <div>
        <h4 className="text-[#848e9c] text-sm mb-2">거래량</h4>
        <ResponsiveContainer width="100%" height={150}>
          <BarChart data={volumeData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#2b3139" />
            <XAxis
              dataKey="time"
              stroke="#848e9c"
              tick={{ fill: "#848e9c", fontSize: 10 }}
              angle={-45}
              textAnchor="end"
              height={60}
            />
            <YAxis
              stroke="#848e9c"
              tick={{ fill: "#848e9c", fontSize: 11 }}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: '#1e2329',
                border: '1px solid #2b3139',
                borderRadius: '8px'
              }}
              labelStyle={{ color: '#848e9c' }}
            />
            <Bar dataKey="volume" fill="#667eea" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

