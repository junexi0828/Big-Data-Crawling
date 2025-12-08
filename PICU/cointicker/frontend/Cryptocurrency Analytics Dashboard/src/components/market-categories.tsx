import { useEffect, useState } from "react";
import { TrendingUp, TrendingDown, Layers } from "lucide-react";
import { externalAPI } from "../services/api";

interface Category {
  id: string;
  name: string;
  market_cap: number;
  market_cap_change_24h: number;
  top_3_coins: Array<{ id: string; name: string }>;
}

export function MarketCategories() {
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      try {
        const data = await externalAPI.getCategories();
        // 시가총액 기준 상위 8개 카테고리
        const sorted = data
          .sort((a: Category, b: Category) => b.market_cap - a.market_cap)
          .slice(0, 8);
        setCategories(sorted);
      } catch (error) {
        console.error("카테고리 데이터 로드 에러:", error);
      } finally {
        setLoading(false);
      }
    };

    loadData();
    const interval = setInterval(loadData, 300000); // 5분마다 업데이트
    return () => clearInterval(interval);
  }, []);

  const formatCurrency = (value: number) => {
    if (value >= 1e12) return `$${(value / 1e12).toFixed(2)}T`;
    if (value >= 1e9) return `$${(value / 1e9).toFixed(2)}B`;
    if (value >= 1e6) return `$${(value / 1e6).toFixed(2)}M`;
    return `$${value.toLocaleString()}`;
  };

  if (loading) {
    return (
      <div className="bg-[#1e2329] border border-[#2b3139] rounded-xl p-6">
        <div className="text-center py-8 text-[#848e9c]">로딩 중...</div>
      </div>
    );
  }

  return (
    <div className="bg-[#1e2329] border border-[#2b3139] rounded-xl p-6 hover:border-[#667eea]/50 transition-all shadow-lg hover:shadow-xl duration-300">
      <div className="flex items-center gap-2 mb-4">
        <Layers className="w-5 h-5 text-[#667eea]" />
        <h3 className="text-[#eaecef] text-lg font-bold">카테고리별 성과</h3>
      </div>

      <div className="space-y-3">
        {categories.map((category) => (
          <div
            key={category.id}
            className="bg-[#2b3139] rounded-lg p-4 hover:bg-[#2b3139]/80 transition-all"
          >
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <span className="text-[#eaecef] font-semibold">{category.name}</span>
                {category.top_3_coins && category.top_3_coins.length > 0 && (
                  <span className="text-xs text-[#848e9c]">
                    ({category.top_3_coins.map(c => c.name).join(", ")})
                  </span>
                )}
              </div>
              <div className={`flex items-center gap-1 text-sm ${
                category.market_cap_change_24h >= 0 ? "text-[#43e97b]" : "text-[#ff6b6b]"
              }`}>
                {category.market_cap_change_24h >= 0 ? (
                  <TrendingUp className="w-3 h-3" />
                ) : (
                  <TrendingDown className="w-3 h-3" />
                )}
                {category.market_cap_change_24h >= 0 ? "+" : ""}
                {category.market_cap_change_24h.toFixed(2)}%
              </div>
            </div>
            <div className="text-sm text-[#848e9c]">
              시가총액: {formatCurrency(category.market_cap)}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

