import { useState, useEffect, useMemo } from "react";
import { Search, X } from "lucide-react";
import { Input } from "./ui/input";
import { externalAPI } from "../services/api";
import { CoinDetailModal } from "./coin-detail-modal";

export function CoinSearch() {
  const [searchQuery, setSearchQuery] = useState("");
  const [coins, setCoins] = useState<any[]>([]);
  const [filteredCoins, setFilteredCoins] = useState<any[]>([]);
  const [selectedCoin, setSelectedCoin] = useState<{ coinId: string; symbol: string } | null>(null);
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    loadCoins();
  }, []);

  useEffect(() => {
    if (searchQuery.length > 0) {
      const filtered = coins.filter(
        (coin) =>
          coin.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
          coin.symbol.toLowerCase().includes(searchQuery.toLowerCase())
      ).slice(0, 10);
      setFilteredCoins(filtered);
      setIsOpen(true);
    } else {
      setIsOpen(false);
    }
  }, [searchQuery, coins]);

  const loadCoins = async () => {
    try {
      const data = await externalAPI.getCoinPrices();
      // 더 많은 코인 로드 (100개)
      const moreCoins = await fetch(
        "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=100&page=1&sparkline=false"
      ).then(res => res.json()).catch(() => []);
      setCoins(moreCoins);
    } catch (error) {
      console.error("코인 목록 로드 에러:", error);
    }
  };

  return (
    <div className="relative w-full max-w-md">
      <div className="relative">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-[#848e9c]" />
        <Input
          type="text"
          placeholder="코인 검색..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="pl-10 pr-10 bg-[#2b3139] border-[#2b3139] text-[#eaecef] placeholder:text-[#848e9c]"
        />
        {searchQuery && (
          <button
            onClick={() => setSearchQuery("")}
            className="absolute right-3 top-1/2 transform -translate-y-1/2 text-[#848e9c] hover:text-[#eaecef]"
          >
            <X className="w-4 h-4" />
          </button>
        )}
      </div>

      {/* 검색 결과 드롭다운 */}
      {isOpen && filteredCoins.length > 0 && (
        <div className="absolute top-full mt-2 w-full bg-[#1e2329] border border-[#2b3139] rounded-lg shadow-xl z-50 max-h-[400px] overflow-y-auto">
          {filteredCoins.map((coin) => (
            <button
              key={coin.id}
              onClick={() => {
                setSelectedCoin({ coinId: coin.id, symbol: coin.symbol.toUpperCase() });
                setSearchQuery("");
                setIsOpen(false);
              }}
              className="w-full flex items-center gap-3 p-3 hover:bg-[#2b3139] transition-colors text-left"
            >
              <img
                src={coin.image}
                alt={coin.name}
                className="w-8 h-8 rounded-full"
                onError={(e) => {
                  (e.target as HTMLImageElement).style.display = 'none';
                }}
              />
              <div className="flex-1">
                <div className="text-[#eaecef] font-semibold">{coin.symbol.toUpperCase()}</div>
                <div className="text-xs text-[#848e9c]">{coin.name}</div>
              </div>
              <div className="text-right">
                <div className="text-[#eaecef] font-semibold">${coin.current_price?.toLocaleString()}</div>
                {coin.price_change_percentage_24h && (
                  <div className={`text-xs ${
                    coin.price_change_percentage_24h >= 0 ? "text-[#43e97b]" : "text-[#ff6b6b]"
                  }`}>
                    {coin.price_change_percentage_24h >= 0 ? "+" : ""}
                    {coin.price_change_percentage_24h.toFixed(2)}%
                  </div>
                )}
              </div>
            </button>
          ))}
        </div>
      )}
      {isOpen && searchQuery && filteredCoins.length === 0 && (
        <div className="absolute top-full mt-2 w-full bg-[#1e2329] border border-[#2b3139] rounded-lg shadow-xl z-50 p-4 text-center text-[#848e9c]">
          검색 결과가 없습니다
        </div>
      )}

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

