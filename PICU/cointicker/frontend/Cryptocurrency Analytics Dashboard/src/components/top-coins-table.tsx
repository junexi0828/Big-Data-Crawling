import { ArrowUp, ArrowDown } from "lucide-react";

interface Coin {
  symbol: string;
  volume24h: number;
  change24h: number;
}

interface TopCoinsTableProps {
  coins: Coin[];
}

export function TopCoinsTable({ coins }: TopCoinsTableProps) {
  const formatVolume = (volume: number) => {
    if (volume >= 1e9) return `$${(volume / 1e9).toFixed(2)}B`;
    if (volume >= 1e6) return `$${(volume / 1e6).toFixed(2)}M`;
    return `$${volume.toLocaleString()}`;
  };

  return (
    <div className="bg-[#1e2329] border border-[#2b3139] rounded-xl p-6 hover:border-[#667eea]/50 transition-all shadow-lg hover:shadow-xl duration-300">
      <h3 className="text-[#eaecef] mb-4">Top 5 Volume Coins</h3>
      
      <div className="space-y-1">
        {/* Header */}
        <div className="grid grid-cols-3 gap-4 pb-3 border-b border-[#2b3139] text-xs text-[#848e9c]">
          <div>Symbol</div>
          <div className="text-right">24h Volume</div>
          <div className="text-right">24h Change</div>
        </div>
        
        {/* Rows */}
        {coins.map((coin, index) => (
          <div
            key={index}
            className="grid grid-cols-3 gap-4 py-3 border-b border-[#2b3139] last:border-0 hover:bg-[#2b3139]/30 transition-all duration-200 rounded-lg px-2 -mx-2 cursor-pointer"
          >
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-full bg-gradient-to-br from-[#667eea] to-[#764ba2] flex items-center justify-center text-sm transition-transform hover:scale-110 duration-200">
                {coin.symbol.charAt(0)}
              </div>
              <span className="text-[#eaecef]">{coin.symbol}</span>
            </div>
            
            <div className="text-right text-[#eaecef]">
              {formatVolume(coin.volume24h)}
            </div>
            
            <div className="text-right flex items-center justify-end gap-1">
              <span
                className={`flex items-center gap-1 ${
                  coin.change24h >= 0 ? "text-[#43e97b]" : "text-[#ff6b6b]"
                }`}
              >
                {coin.change24h >= 0 ? (
                  <ArrowUp className="w-3 h-3" />
                ) : (
                  <ArrowDown className="w-3 h-3" />
                )}
                {Math.abs(coin.change24h).toFixed(2)}%
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}