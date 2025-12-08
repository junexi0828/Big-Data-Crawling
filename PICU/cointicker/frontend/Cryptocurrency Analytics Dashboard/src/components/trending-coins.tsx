import { useEffect, useState } from "react";
import { TrendingUp, Flame } from "lucide-react";
import { externalAPI } from "../services/api";
import { CoinDetailModal } from "./coin-detail-modal";

interface TrendingCoin {
  item: {
    id: string;
    name: string;
    symbol: string;
    thumb: string;
    data: {
      price: number;
      price_change_percentage_24h: { usd: number };
      market_cap: string;
    };
  };
}

export function TrendingCoins() {
  const [trending, setTrending] = useState<TrendingCoin[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedCoin, setSelectedCoin] = useState<{ coinId: string; symbol: string } | null>(null);

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      try {
        const response = await externalAPI.getTrendingCoins();
        if (response && response.coins && response.coins.length > 0) {
          setTrending(response.coins.slice(0, 10));
        } else {
          // 더미 데이터
          setTrending([
            {
              item: {
                id: "firo",
                name: "Firo",
                symbol: "FIRO",
                thumb: "https://assets.coingecko.com/coins/images/479/large/firo.jpg",
                data: { price: 2.15, price_change_percentage_24h: { usd: -3.31 }, market_cap: "28000000" }
              }
            },
            {
              item: {
                id: "hype",
                name: "Hyperliquid",
                symbol: "HYPE",
                thumb: "https://assets.coingecko.com/coins/images/28253/large/HYPE.png",
                data: { price: 28.99, price_change_percentage_24h: { usd: -2.90 }, market_cap: "1200000000" }
              }
            },
            {
              item: {
                id: "pengu",
                name: "Pudgy Penguins",
                symbol: "PENGU",
                thumb: "https://assets.coingecko.com/coins/images/34420/large/pengu.png",
                data: { price: 0.01, price_change_percentage_24h: { usd: -1.00 }, market_cap: "50000000" }
              }
            },
            {
              item: {
                id: "mon",
                name: "Mon Protocol",
                symbol: "MON",
                thumb: "https://assets.coingecko.com/coins/images/34419/large/mon.png",
                data: { price: 0.03, price_change_percentage_24h: { usd: -0.71 }, market_cap: "80000000" }
              }
            },
            {
              item: {
                id: "bitcoin",
                name: "Bitcoin",
                symbol: "BTC",
                thumb: "https://assets.coingecko.com/coins/images/1/large/bitcoin.png",
                data: { price: 91039.18, price_change_percentage_24h: { usd: 1.78 }, market_cap: "1800000000000" }
              }
            },
            {
              item: {
                id: "zcash",
                name: "Zcash",
                symbol: "ZEC",
                thumb: "https://assets.coingecko.com/coins/images/486/large/zcash.png",
                data: { price: 349.15, price_change_percentage_24h: { usd: 4.25 }, market_cap: "5600000000" }
              }
            },
            {
              item: {
                id: "terra-luna",
                name: "Terra Luna Classic",
                symbol: "LUNC",
                thumb: "https://assets.coingecko.com/coins/images/8284/large/luna.png",
                data: { price: 0.0001, price_change_percentage_24h: { usd: -17.37 }, market_cap: "600000000" }
              }
            },
            {
              item: {
                id: "ethereum",
                name: "Ethereum",
                symbol: "ETH",
                thumb: "https://assets.coingecko.com/coins/images/279/large/ethereum.png",
                data: { price: 3096.82, price_change_percentage_24h: { usd: 1.63 }, market_cap: "370000000000" }
              }
            },
            {
              item: {
                id: "sui",
                name: "Sui",
                symbol: "SUI",
                thumb: "https://assets.coingecko.com/coins/images/26375/large/sui_asset.png",
                data: { price: 1.61, price_change_percentage_24h: { usd: 1.90 }, market_cap: "2000000000" }
              }
            },
            {
              item: {
                id: "power",
                name: "Power",
                symbol: "POWER",
                thumb: "https://assets.coingecko.com/coins/images/34421/large/power.png",
                data: { price: 0.20, price_change_percentage_24h: { usd: -6.49 }, market_cap: "30000000" }
              }
            },
          ]);
        }
      } catch (error) {
        console.error("트렌딩 코인 로드 에러:", error);
        // 에러 시 더미 데이터
        setTrending([
          {
            item: {
              id: "bitcoin",
              name: "Bitcoin",
              symbol: "BTC",
              thumb: "https://assets.coingecko.com/coins/images/1/large/bitcoin.png",
              data: { price: 91039.18, price_change_percentage_24h: { usd: 1.78 }, market_cap: "1800000000000" }
            }
          },
          {
            item: {
              id: "ethereum",
              name: "Ethereum",
              symbol: "ETH",
              thumb: "https://assets.coingecko.com/coins/images/279/large/ethereum.png",
              data: { price: 3096.82, price_change_percentage_24h: { usd: 1.63 }, market_cap: "370000000000" }
            }
          },
        ]);
      } finally {
        setLoading(false);
      }
    };

    loadData();
    const interval = setInterval(loadData, 300000); // 5분마다 업데이트
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="bg-[#1e2329] border border-[#2b3139] rounded-xl p-6">
        <div className="text-center py-8 text-[#848e9c]">로딩 중...</div>
      </div>
    );
  }

  return (
    <>
      <div className="bg-[#1e2329] border border-[#2b3139] rounded-xl p-6 hover:border-[#667eea]/50 transition-all shadow-lg hover:shadow-xl duration-300">
        <div className="flex items-center gap-2 mb-4">
          <Flame className="w-5 h-5 text-[#ff6b6b]" />
          <h3 className="text-[#eaecef] text-lg font-bold">트렌딩 코인</h3>
        </div>

        <div className="space-y-2">
          {trending.map((coin, index) => (
            <div
              key={coin.item.id}
              onClick={() => setSelectedCoin({ coinId: coin.item.id, symbol: coin.item.symbol.toUpperCase() })}
              className="flex items-center justify-between p-3 bg-[#2b3139] rounded-lg hover:bg-[#2b3139]/80 cursor-pointer transition-all"
            >
              <div className="flex items-center gap-3">
                <div className="text-[#848e9c] text-sm font-bold w-6">{index + 1}</div>
                <img
                  src={coin.item.thumb}
                  alt={coin.item.name}
                  className="w-8 h-8 rounded-full"
                  onError={(e) => {
                    (e.target as HTMLImageElement).style.display = 'none';
                  }}
                />
                <div>
                  <div className="text-[#eaecef] font-semibold">{coin.item.symbol.toUpperCase()}</div>
                  <div className="text-xs text-[#848e9c]">{coin.item.name}</div>
                </div>
              </div>
              <div className="text-right">
                <div className="text-[#eaecef] font-semibold">
                  ${coin.item.data.price?.toFixed(2) || "N/A"}
                </div>
                {coin.item.data.price_change_percentage_24h?.usd && (
                  <div className={`text-xs flex items-center gap-1 ${
                    coin.item.data.price_change_percentage_24h.usd >= 0 ? "text-[#43e97b]" : "text-[#ff6b6b]"
                  }`}>
                    <TrendingUp className="w-3 h-3" />
                    {coin.item.data.price_change_percentage_24h.usd >= 0 ? "+" : ""}
                    {coin.item.data.price_change_percentage_24h.usd.toFixed(2)}%
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {selectedCoin && (
        <CoinDetailModal
          coinId={selectedCoin.coinId}
          symbol={selectedCoin.symbol}
          isOpen={!!selectedCoin}
          onClose={() => setSelectedCoin(null)}
        />
      )}
    </>
  );
}

