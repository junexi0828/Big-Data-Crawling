import { ArrowUp, ArrowDown } from "lucide-react";
import { useEffect, useState } from "react";
import { externalAPI } from "../services/api";
import { dashboardAPI } from "../services/api";
import { CoinDetailModal } from "./coin-detail-modal";

interface Coin {
  symbol: string;
  volume24h: number;
  change24h: number;
  price?: number;
  coinId?: string;
}

interface TopCoinsTableProps {
  coins: Coin[];
}

export function TopCoinsTable({ coins: initialCoins }: TopCoinsTableProps) {
  const [coins, setCoins] = useState<Coin[]>(initialCoins);
  const [loading, setLoading] = useState(false);
  const [selectedCoin, setSelectedCoin] = useState<{ coinId: string; symbol: string } | null>(null);

  useEffect(() => {
    const loadCoins = async () => {
      // 백엔드 데이터가 있으면 사용 (유효한 데이터만 필터링)
      if (initialCoins && initialCoins.length > 0) {
        const validCoins = initialCoins.filter(coin => coin && coin.symbol);
        if (validCoins.length > 0) {
          setCoins(validCoins);
          return;
        }
      }

      // 백엔드 데이터가 없으면 CoinGecko API 사용
      setLoading(true);
      try {
        const coinData = await externalAPI.getCoinPrices();
        const formattedCoins = coinData
          .filter((coin: any) => coin && coin.symbol && coin.id) // 유효한 데이터만 필터링
          .slice(0, 5)
          .map((coin: any) => ({
            symbol: (coin.symbol || "?").toUpperCase(),
            volume24h: coin.total_volume || 0,
            change24h: coin.price_change_percentage_24h || 0,
            price: coin.current_price || 0,
            coinId: coin.id || "",
          }));

        if (formattedCoins.length > 0) {
          setCoins(formattedCoins);
        } else {
          // API 데이터가 없으면 더미 데이터 사용
          setCoins([
            { symbol: "BTC", volume24h: 28500000000, change24h: 1.78, price: 91039.18, coinId: "bitcoin" },
            { symbol: "ETH", volume24h: 15200000000, change24h: 1.63, price: 3096.82, coinId: "ethereum" },
            { symbol: "BNB", volume24h: 2100000000, change24h: -0.45, price: 585.23, coinId: "binancecoin" },
            { symbol: "SOL", volume24h: 3200000000, change24h: 2.15, price: 142.56, coinId: "solana" },
            { symbol: "ADA", volume24h: 850000000, change24h: 0.92, price: 0.48, coinId: "cardano" },
          ]);
        }
      } catch (error) {
        console.error("코인 데이터 로드 에러:", error);
        // 에러 시 더미 데이터 설정
        setCoins([
          { symbol: "BTC", volume24h: 28500000000, change24h: 1.78, price: 91039.18, coinId: "bitcoin" },
          { symbol: "ETH", volume24h: 15200000000, change24h: 1.63, price: 3096.82, coinId: "ethereum" },
          { symbol: "BNB", volume24h: 2100000000, change24h: -0.45, price: 585.23, coinId: "binancecoin" },
          { symbol: "SOL", volume24h: 3200000000, change24h: 2.15, price: 142.56, coinId: "solana" },
          { symbol: "ADA", volume24h: 850000000, change24h: 0.92, price: 0.48, coinId: "cardano" },
        ]);
      } finally {
        setLoading(false);
      }
    };

    loadCoins();
    // 30초마다 업데이트
    const interval = setInterval(loadCoins, 30000);
    return () => clearInterval(interval);
  }, [initialCoins]);
  const formatVolume = (volume: number) => {
    if (volume >= 1e9) return `$${(volume / 1e9).toFixed(2)}B`;
    if (volume >= 1e6) return `$${(volume / 1e6).toFixed(2)}M`;
    return `$${volume.toLocaleString()}`;
  };

  if (loading) {
    return (
      <div className="bg-[#1e2329] border border-[#2b3139] rounded-xl p-6">
        <h3 className="text-[#eaecef] mb-4">Top 5 Volume Coins</h3>
        <div className="text-center py-8 text-[#848e9c]">로딩 중...</div>
      </div>
    );
  }

  return (
    <div className="bg-[#1e2329] border border-[#2b3139] rounded-xl p-6 hover:border-[#667eea]/50 transition-all shadow-lg hover:shadow-xl duration-300">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-[#eaecef]">Top 5 Volume Coins</h3>
        {coins.length > 0 && (
          <span className="text-xs text-[#848e9c]">
            마지막 업데이트: {new Date().toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' })}
          </span>
        )}
      </div>

      <div className="space-y-1">
        {/* Header */}
        <div className="grid grid-cols-3 gap-4 pb-3 border-b border-[#2b3139] text-xs text-[#848e9c]">
          <div>Symbol</div>
          <div className="text-right">24h Volume</div>
          <div className="text-right">24h Change</div>
        </div>

        {/* Rows */}
        {coins.length > 0 ? coins
          .filter(coin => coin && coin.symbol) // null/undefined 필터링
          .map((coin, index) => {
            const symbol = coin.symbol || "?";
            const firstChar = symbol.charAt(0) || "?";

            return (
              <div
                key={coin.coinId || index}
                onClick={() => {
                  if (coin.coinId) {
                    setSelectedCoin({ coinId: coin.coinId, symbol: symbol });
                  }
                }}
                className="grid grid-cols-3 gap-4 py-3 border-b border-[#2b3139] last:border-0 hover:bg-[#2b3139]/30 transition-all duration-200 rounded-lg px-2 -mx-2 cursor-pointer"
              >
                <div className="flex items-center gap-2">
                  <div className="w-8 h-8 rounded-full bg-gradient-to-br from-[#667eea] to-[#764ba2] flex items-center justify-center text-sm transition-transform hover:scale-110 duration-200">
                    {firstChar}
                  </div>
                  <span className="text-[#eaecef]">{symbol}</span>
                </div>

                <div className="text-right text-[#eaecef]">
                  {formatVolume(coin.volume24h || 0)}
                </div>

                <div className="text-right flex items-center justify-end gap-1">
                  <span
                    className={`flex items-center gap-1 ${
                      (coin.change24h || 0) >= 0 ? "text-[#43e97b]" : "text-[#ff6b6b]"
                    }`}
                  >
                    {(coin.change24h || 0) >= 0 ? (
                      <ArrowUp className="w-3 h-3" />
                    ) : (
                      <ArrowDown className="w-3 h-3" />
                    )}
                    {Math.abs(coin.change24h || 0).toFixed(2)}%
                  </span>
                </div>
              </div>
            );
          }) : (
          <div className="text-center py-8 text-[#848e9c]">데이터가 없습니다</div>
        )}
      </div>

      {/* 코인 상세 정보 모달 */}
      {selectedCoin && (
        <CoinDetailModal
          coinId={selectedCoin.coinId}
          symbol={selectedCoin.symbol}
          isOpen={!!selectedCoin}
          onClose={() => setSelectedCoin(null)}
        />
      )}
    </div>
  );
}