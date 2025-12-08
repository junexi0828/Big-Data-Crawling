import { useState, useEffect } from "react";
import { Wallet, Plus, Trash2, TrendingUp, TrendingDown, DollarSign } from "lucide-react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";
import { externalAPI } from "../services/api";

interface PortfolioItem {
  id: string;
  coinId: string;
  coinSymbol: string;
  amount: number;
  purchasePrice: number;
}

export function PortfolioTracker() {
  const [portfolio, setPortfolio] = useState<PortfolioItem[]>([]);
  const [selectedCoin, setSelectedCoin] = useState<string>("");
  const [amount, setAmount] = useState<string>("");
  const [purchasePrice, setPurchasePrice] = useState<string>("");
  const [availableCoins, setAvailableCoins] = useState<any[]>([]);
  const [portfolioValue, setPortfolioValue] = useState({ total: 0, profit: 0, profitPercent: 0 });

  useEffect(() => {
    loadAvailableCoins();
    loadPortfolio();
  }, []);

  useEffect(() => {
    if (portfolio.length > 0) {
      calculatePortfolioValue();
    }
  }, [portfolio]);

  const loadAvailableCoins = async () => {
    try {
      const coins = await externalAPI.getCoinPrices();
      setAvailableCoins(coins.slice(0, 50));
    } catch (error) {
      console.error("코인 목록 로드 에러:", error);
    }
  };

  const loadPortfolio = () => {
    const saved = localStorage.getItem('portfolio');
    if (saved) {
      setPortfolio(JSON.parse(saved));
    }
  };

  const savePortfolio = (newPortfolio: PortfolioItem[]) => {
    setPortfolio(newPortfolio);
    localStorage.setItem('portfolio', JSON.stringify(newPortfolio));
  };

  const addToPortfolio = () => {
    if (!selectedCoin || !amount || !purchasePrice) return;

    const coin = availableCoins.find(c => c.id === selectedCoin);
    if (!coin) return;

    const newItem: PortfolioItem = {
      id: Date.now().toString(),
      coinId: selectedCoin,
      coinSymbol: coin.symbol.toUpperCase(),
      amount: parseFloat(amount),
      purchasePrice: parseFloat(purchasePrice),
    };

    savePortfolio([...portfolio, newItem]);
    setSelectedCoin("");
    setAmount("");
    setPurchasePrice("");
  };

  const removeFromPortfolio = (id: string) => {
    savePortfolio(portfolio.filter(item => item.id !== id));
  };

  const calculatePortfolioValue = async () => {
    let totalValue = 0;
    let totalCost = 0;

    for (const item of portfolio) {
      try {
        const coinData = await externalAPI.getCoinDetail(item.coinId);
        if (coinData) {
          const currentPrice = coinData.market_data.current_price.usd;
          const value = item.amount * currentPrice;
          const cost = item.amount * item.purchasePrice;

          totalValue += value;
          totalCost += cost;
        }
      } catch (error) {
        console.error(`포트폴리오 계산 에러 (${item.coinSymbol}):`, error);
      }
    }

    const profit = totalValue - totalCost;
    const profitPercent = totalCost > 0 ? (profit / totalCost) * 100 : 0;

    setPortfolioValue({ total: totalValue, profit, profitPercent });
  };

  const formatCurrency = (value: number) => {
    if (value >= 1e9) return `$${(value / 1e9).toFixed(2)}B`;
    if (value >= 1e6) return `$${(value / 1e6).toFixed(2)}M`;
    return `$${value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  };

  return (
    <div className="bg-[#1e2329] border border-[#2b3139] rounded-xl p-6 hover:border-[#667eea]/50 transition-all shadow-lg hover:shadow-xl duration-300">
      <div className="flex items-center gap-2 mb-6">
        <Wallet className="w-5 h-5 text-[#667eea]" />
        <h3 className="text-[#eaecef] text-lg font-bold">포트폴리오 추적</h3>
      </div>

      {/* 포트폴리오 요약 */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="bg-[#2b3139] rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <DollarSign className="w-4 h-4 text-[#848e9c]" />
            <span className="text-sm text-[#848e9c]">총 가치</span>
          </div>
          <div className="text-2xl font-bold text-[#eaecef]">
            {formatCurrency(portfolioValue.total)}
          </div>
        </div>
        <div className="bg-[#2b3139] rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            {portfolioValue.profit >= 0 ? (
              <TrendingUp className="w-4 h-4 text-[#43e97b]" />
            ) : (
              <TrendingDown className="w-4 h-4 text-[#ff6b6b]" />
            )}
            <span className="text-sm text-[#848e9c]">손익</span>
          </div>
          <div className={`text-2xl font-bold ${
            portfolioValue.profit >= 0 ? "text-[#43e97b]" : "text-[#ff6b6b]"
          }`}>
            {portfolioValue.profit >= 0 ? "+" : ""}{formatCurrency(portfolioValue.profit)}
          </div>
        </div>
        <div className="bg-[#2b3139] rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-sm text-[#848e9c]">수익률</span>
          </div>
          <div className={`text-2xl font-bold ${
            portfolioValue.profitPercent >= 0 ? "text-[#43e97b]" : "text-[#ff6b6b]"
          }`}>
            {portfolioValue.profitPercent >= 0 ? "+" : ""}{portfolioValue.profitPercent.toFixed(2)}%
          </div>
        </div>
      </div>

      {/* 포트폴리오 추가 폼 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-3 mb-6">
        <Select value={selectedCoin} onValueChange={setSelectedCoin}>
          <SelectTrigger className="bg-[#2b3139] border-[#2b3139]">
            <SelectValue placeholder="코인 선택" />
          </SelectTrigger>
          <SelectContent className="bg-[#1e2329] border-[#2b3139] max-h-[300px]">
            {availableCoins.map((coin) => (
              <SelectItem key={coin.id} value={coin.id} className="text-[#eaecef]">
                {coin.symbol.toUpperCase()} - {coin.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        <Input
          type="number"
          placeholder="수량"
          value={amount}
          onChange={(e) => setAmount(e.target.value)}
          className="bg-[#2b3139] border-[#2b3139] text-[#eaecef]"
        />

        <Input
          type="number"
          placeholder="매수 가격 (USD)"
          value={purchasePrice}
          onChange={(e) => setPurchasePrice(e.target.value)}
          className="bg-[#2b3139] border-[#2b3139] text-[#eaecef]"
        />

        <Button
          onClick={addToPortfolio}
          className="bg-gradient-to-r from-[#667eea] to-[#764ba2] hover:opacity-90"
        >
          <Plus className="w-4 h-4 mr-2" />
          추가
        </Button>
      </div>

      {/* 포트폴리오 목록 */}
      <div className="space-y-2">
        {portfolio.length === 0 ? (
          <div className="text-center py-8 text-[#848e9c]">
            포트폴리오가 비어있습니다. 위에서 코인을 추가해주세요.
          </div>
        ) : (
          portfolio.map((item) => (
            <PortfolioItemRow
              key={item.id}
              item={item}
              onRemove={removeFromPortfolio}
            />
          ))
        )}
      </div>
    </div>
  );
}

function PortfolioItemRow({ item, onRemove }: { item: PortfolioItem; onRemove: (id: string) => void }) {
  const [currentPrice, setCurrentPrice] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadPrice = async () => {
      try {
        const coinData = await externalAPI.getCoinDetail(item.coinId);
        if (coinData) {
          setCurrentPrice(coinData.market_data.current_price.usd);
        }
      } catch (error) {
        console.error("가격 로드 에러:", error);
      } finally {
        setLoading(false);
      }
    };

    loadPrice();
    const interval = setInterval(loadPrice, 30000);
    return () => clearInterval(interval);
  }, [item.coinId]);

  if (loading) {
    return (
      <div className="bg-[#2b3139] rounded-lg p-4">
        <div className="text-[#848e9c]">로딩 중...</div>
      </div>
    );
  }

  const value = item.amount * (currentPrice || 0);
  const cost = item.amount * item.purchasePrice;
  const profit = value - cost;
  const profitPercent = cost > 0 ? (profit / cost) * 100 : 0;

  return (
    <div className="bg-[#2b3139] rounded-lg p-4">
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-4">
            <div>
              <div className="text-[#eaecef] font-semibold">{item.coinSymbol}</div>
              <div className="text-xs text-[#848e9c]">
                {item.amount} 개 × ${item.purchasePrice.toLocaleString()}
              </div>
            </div>
            <div className="text-right">
              <div className="text-[#eaecef] font-semibold">
                ${value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </div>
              <div className={`text-xs flex items-center gap-1 ${
                profit >= 0 ? "text-[#43e97b]" : "text-[#ff6b6b]"
              }`}>
                {profit >= 0 ? (
                  <TrendingUp className="w-3 h-3" />
                ) : (
                  <TrendingDown className="w-3 h-3" />
                )}
                {profit >= 0 ? "+" : ""}${profit.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })} ({profitPercent >= 0 ? "+" : ""}{profitPercent.toFixed(2)}%)
              </div>
            </div>
          </div>
        </div>
        <Button
          variant="ghost"
          size="icon"
          onClick={() => onRemove(item.id)}
          className="text-[#848e9c] hover:text-[#ff6b6b] ml-4"
        >
          <Trash2 className="w-4 h-4" />
        </Button>
      </div>
    </div>
  );
}

