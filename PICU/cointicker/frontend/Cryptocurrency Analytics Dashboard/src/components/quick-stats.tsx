import { useEffect, useState } from "react";
import { TrendingUp, TrendingDown, DollarSign, Activity } from "lucide-react";
import { externalAPI } from "../services/api";

export function QuickStats() {
  const [stats, setStats] = useState({
    btcPrice: 0,
    btcChange: 0,
    ethPrice: 0,
    ethChange: 0,
    totalMarketCap: 0,
    totalVolume: 0,
  });

  useEffect(() => {
    const loadStats = async () => {
      try {
        const [coins, global] = await Promise.all([
          externalAPI.getCoinPrices(),
          externalAPI.getGlobalMarketData(),
        ]);

        const btc = coins.find((c: any) => c.id === 'bitcoin');
        const eth = coins.find((c: any) => c.id === 'ethereum');

        if (btc) {
          setStats(prev => ({
            ...prev,
            btcPrice: btc.current_price,
            btcChange: btc.price_change_percentage_24h || 0,
          }));
        } else {
          // 더미 데이터
          setStats(prev => ({
            ...prev,
            btcPrice: 91039.18,
            btcChange: 1.78,
          }));
        }

        if (eth) {
          setStats(prev => ({
            ...prev,
            ethPrice: eth.current_price,
            ethChange: eth.price_change_percentage_24h || 0,
          }));
        } else {
          // 더미 데이터
          setStats(prev => ({
            ...prev,
            ethPrice: 3096.82,
            ethChange: 1.63,
          }));
        }

        if (global?.data) {
          setStats(prev => ({
            ...prev,
            totalMarketCap: global.data.total_market_cap.usd,
            totalVolume: global.data.total_volume.usd,
          }));
        } else {
          // 더미 데이터
          setStats(prev => ({
            ...prev,
            totalMarketCap: 3.2e12, // $3.2T
            totalVolume: 120e9, // $120B
          }));
        }
      } catch (error) {
        console.error("퀵 스탯 로드 에러:", error);
        // 에러 시 더미 데이터 설정
        setStats({
          btcPrice: 91039.18,
          btcChange: 1.78,
          ethPrice: 3096.82,
          ethChange: 1.63,
          totalMarketCap: 3.2e12,
          totalVolume: 120e9,
        });
      }
    };

    loadStats();
    const interval = setInterval(loadStats, 10000); // 10초마다 업데이트
    return () => clearInterval(interval);
  }, []);

  const formatCurrency = (value: number) => {
    if (value >= 1e12) return `$${(value / 1e12).toFixed(2)}T`;
    if (value >= 1e9) return `$${(value / 1e9).toFixed(2)}B`;
    if (value >= 1e6) return `$${(value / 1e6).toFixed(2)}M`;
    return `$${value.toLocaleString()}`;
  };

  return (
    <div className="bg-[#1e2329] border border-[#2b3139] rounded-xl p-4">
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-[#f7931a] to-[#f7931a]/50 flex items-center justify-center">
            <span className="text-white font-bold text-sm">₿</span>
          </div>
          <div>
            <div className="text-xs text-[#848e9c]">BTC</div>
            <div className="text-sm font-semibold text-[#eaecef]">
              ${stats.btcPrice.toLocaleString()}
            </div>
            <div className={`text-xs flex items-center gap-1 ${
              stats.btcChange >= 0 ? "text-[#43e97b]" : "text-[#ff6b6b]"
            }`}>
              {stats.btcChange >= 0 ? (
                <TrendingUp className="w-3 h-3" />
              ) : (
                <TrendingDown className="w-3 h-3" />
              )}
              {Math.abs(stats.btcChange).toFixed(2)}%
            </div>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-[#627EEA] to-[#627EEA]/50 flex items-center justify-center">
            <span className="text-white font-bold text-sm">Ξ</span>
          </div>
          <div>
            <div className="text-xs text-[#848e9c]">ETH</div>
            <div className="text-sm font-semibold text-[#eaecef]">
              ${stats.ethPrice.toLocaleString()}
            </div>
            <div className={`text-xs flex items-center gap-1 ${
              stats.ethChange >= 0 ? "text-[#43e97b]" : "text-[#ff6b6b]"
            }`}>
              {stats.ethChange >= 0 ? (
                <TrendingUp className="w-3 h-3" />
              ) : (
                <TrendingDown className="w-3 h-3" />
              )}
              {Math.abs(stats.ethChange).toFixed(2)}%
            </div>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <DollarSign className="w-10 h-10 text-[#667eea]" />
          <div>
            <div className="text-xs text-[#848e9c]">시가총액</div>
            <div className="text-sm font-semibold text-[#eaecef]">
              {formatCurrency(stats.totalMarketCap)}
            </div>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <Activity className="w-10 h-10 text-[#43e97b]" />
          <div>
            <div className="text-xs text-[#848e9c]">24h 거래량</div>
            <div className="text-sm font-semibold text-[#eaecef]">
              {formatCurrency(stats.totalVolume)}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

