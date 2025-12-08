import { useState, useEffect } from "react";
import { X, TrendingUp, TrendingDown, BarChart3 } from "lucide-react";
import { externalAPI } from "../services/api";
import { Button } from "./ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from "recharts";

interface CoinComparisonProps {
  onClose?: () => void;
}

export function CoinComparison({ onClose }: CoinComparisonProps) {
  const [selectedCoins, setSelectedCoins] = useState<string[]>([]);
  const [coinData, setCoinData] = useState<any[]>([]);
  const [availableCoins, setAvailableCoins] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [comparisonData, setComparisonData] = useState<any[]>([]);

  useEffect(() => {
    loadAvailableCoins();
  }, []);

  useEffect(() => {
    if (selectedCoins.length > 0) {
      loadComparisonData();
    }
  }, [selectedCoins]);

  const loadAvailableCoins = async () => {
    try {
      const coins = await externalAPI.getCoinPrices();
      setAvailableCoins(coins.slice(0, 50));
    } catch (error) {
      console.error("코인 목록 로드 에러:", error);
    }
  };

  const loadComparisonData = async () => {
    setLoading(true);
    try {
      const promises = selectedCoins.map(async (coinId) => {
        const detail = await externalAPI.getCoinDetail(coinId);
        if (detail) {
          return {
            id: coinId,
            name: detail.name,
            symbol: detail.symbol.toUpperCase(),
            price: detail.market_data.current_price.usd,
            change24h: detail.market_data.price_change_percentage_24h,
            marketCap: detail.market_data.market_cap.usd,
            volume24h: detail.market_data.total_volume.usd,
            high24h: detail.market_data.high_24h.usd,
            low24h: detail.market_data.low_24h.usd,
          };
        }
        return null;
      });

      const results = await Promise.all(promises);
      setCoinData(results.filter(Boolean));
    } catch (error) {
      console.error("비교 데이터 로드 에러:", error);
    } finally {
      setLoading(false);
    }
  };

  const addCoin = (coinId: string) => {
    if (!selectedCoins.includes(coinId) && selectedCoins.length < 5) {
      setSelectedCoins([...selectedCoins, coinId]);
    }
  };

  const removeCoin = (coinId: string) => {
    setSelectedCoins(selectedCoins.filter(id => id !== coinId));
  };

  const formatCurrency = (value: number) => {
    if (value >= 1e12) return `$${(value / 1e12).toFixed(2)}T`;
    if (value >= 1e9) return `$${(value / 1e9).toFixed(2)}B`;
    if (value >= 1e6) return `$${(value / 1e6).toFixed(2)}M`;
    return `$${value.toLocaleString()}`;
  };

  return (
    <div className="bg-[#1e2329] border border-[#2b3139] rounded-xl p-6 hover:border-[#667eea]/50 transition-all shadow-lg hover:shadow-xl duration-300">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-2">
          <BarChart3 className="w-5 h-5 text-[#667eea]" />
          <h3 className="text-[#eaecef] text-lg font-bold">코인 비교</h3>
        </div>
        {onClose && (
          <Button
            variant="ghost"
            size="icon"
            onClick={onClose}
            className="text-[#848e9c] hover:text-[#eaecef]"
          >
            <X className="w-4 h-4" />
          </Button>
        )}
      </div>

      {/* 코인 선택 */}
      <div className="mb-6">
        <Select onValueChange={addCoin}>
          <SelectTrigger className="w-full bg-[#2b3139] border-[#2b3139]">
            <SelectValue placeholder="비교할 코인 선택 (최대 5개)" />
          </SelectTrigger>
          <SelectContent className="bg-[#1e2329] border-[#2b3139] max-h-[300px]">
            {availableCoins
              .filter(coin => !selectedCoins.includes(coin.id))
              .map((coin) => (
                <SelectItem
                  key={coin.id}
                  value={coin.id}
                  className="text-[#eaecef]"
                >
                  {coin.symbol.toUpperCase()} - {coin.name}
                </SelectItem>
              ))}
          </SelectContent>
        </Select>

        {/* 선택된 코인 태그 */}
        <div className="flex flex-wrap gap-2 mt-3">
          {selectedCoins.map((coinId) => {
            const coin = availableCoins.find(c => c.id === coinId);
            return coin ? (
              <div
                key={coinId}
                className="flex items-center gap-2 bg-[#2b3139] px-3 py-1 rounded-lg"
              >
                <span className="text-[#eaecef] text-sm">{coin.symbol.toUpperCase()}</span>
                <button
                  onClick={() => removeCoin(coinId)}
                  className="text-[#848e9c] hover:text-[#eaecef]"
                >
                  <X className="w-3 h-3" />
                </button>
              </div>
            ) : null;
          })}
        </div>
      </div>

      {loading ? (
        <div className="text-center py-8 text-[#848e9c]">로딩 중...</div>
      ) : coinData.length > 0 ? (
        <div className="space-y-6">
          {/* 비교 테이블 */}
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-[#2b3139]">
                  <th className="text-left py-3 px-4 text-sm text-[#848e9c]">코인</th>
                  <th className="text-right py-3 px-4 text-sm text-[#848e9c]">가격</th>
                  <th className="text-right py-3 px-4 text-sm text-[#848e9c]">24h 변동</th>
                  <th className="text-right py-3 px-4 text-sm text-[#848e9c]">시가총액</th>
                  <th className="text-right py-3 px-4 text-sm text-[#848e9c]">24h 거래량</th>
                  <th className="text-right py-3 px-4 text-sm text-[#848e9c]">24h 고가</th>
                  <th className="text-right py-3 px-4 text-sm text-[#848e9c]">24h 저가</th>
                </tr>
              </thead>
              <tbody>
                {coinData.map((coin) => (
                  <tr key={coin.id} className="border-b border-[#2b3139] hover:bg-[#2b3139]/30">
                    <td className="py-3 px-4">
                      <div className="font-semibold text-[#eaecef]">{coin.symbol}</div>
                      <div className="text-xs text-[#848e9c]">{coin.name}</div>
                    </td>
                    <td className="text-right py-3 px-4 text-[#eaecef]">
                      ${coin.price.toLocaleString()}
                    </td>
                    <td className="text-right py-3 px-4">
                      <span className={`flex items-center justify-end gap-1 ${
                        coin.change24h >= 0 ? "text-[#43e97b]" : "text-[#ff6b6b]"
                      }`}>
                        {coin.change24h >= 0 ? (
                          <TrendingUp className="w-3 h-3" />
                        ) : (
                          <TrendingDown className="w-3 h-3" />
                        )}
                        {coin.change24h >= 0 ? "+" : ""}{coin.change24h.toFixed(2)}%
                      </span>
                    </td>
                    <td className="text-right py-3 px-4 text-[#eaecef]">
                      {formatCurrency(coin.marketCap)}
                    </td>
                    <td className="text-right py-3 px-4 text-[#eaecef]">
                      {formatCurrency(coin.volume24h)}
                    </td>
                    <td className="text-right py-3 px-4 text-[#43e97b]">
                      ${coin.high24h.toLocaleString()}
                    </td>
                    <td className="text-right py-3 px-4 text-[#ff6b6b]">
                      ${coin.low24h.toLocaleString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* 가격 비교 차트 */}
          {coinData.length > 1 && (
            <div>
              <h4 className="text-[#eaecef] mb-4">가격 비교 (정규화)</h4>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={coinData.map((coin, index) => ({
                  name: coin.symbol,
                  value: 100 + (coin.change24h || 0),
                  index
                }))}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#2b3139" />
                  <XAxis dataKey="name" stroke="#848e9c" tick={{ fill: "#848e9c" }} />
                  <YAxis stroke="#848e9c" tick={{ fill: "#848e9c" }} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#1e2329',
                      border: '1px solid #2b3139',
                      borderRadius: '8px'
                    }}
                  />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="value"
                    stroke="#667eea"
                    strokeWidth={2}
                    dot={{ fill: "#667eea", r: 4 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>
      ) : (
        <div className="text-center py-8 text-[#848e9c]">
          비교할 코인을 선택해주세요
        </div>
      )}
    </div>
  );
}

