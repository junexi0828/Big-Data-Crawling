import { useEffect, useState } from "react";
import { Activity, TrendingUp } from "lucide-react";
import { externalAPI } from "../services/api";

interface DefiChain {
  name: string;
  tvl: number;
  tokenSymbol: string;
  cmcId: string;
  geckoId: string;
}

export function DefiStats() {
  const [chains, setChains] = useState<DefiChain[]>([]);
  const [totalTvl, setTotalTvl] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      try {
        const data = await externalAPI.getDefiTvl();
        if (Array.isArray(data)) {
          // TVL 기준 상위 10개 체인
          const sorted = data
            .filter((chain: any) => chain.tvl && chain.tvl > 0)
            .sort((a: any, b: any) => b.tvl - a.tvl)
            .slice(0, 10)
            .map((chain: any) => ({
              name: chain.name,
              tvl: chain.tvl,
              tokenSymbol: chain.tokenSymbol || "",
              cmcId: chain.cmcId || "",
              geckoId: chain.geckoId || "",
            }));

          setChains(sorted);
          setTotalTvl(data.reduce((sum: number, chain: any) => sum + (chain.tvl || 0), 0));
        }
      } catch (error) {
        console.error("DeFi TVL 데이터 로드 에러:", error);
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
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Activity className="w-5 h-5 text-[#43e97b]" />
          <h3 className="text-[#eaecef] text-lg font-bold">DeFi TVL</h3>
        </div>
        <div className="text-right">
          <div className="text-xs text-[#848e9c]">총 TVL</div>
          <div className="text-lg font-bold text-[#eaecef]">{formatCurrency(totalTvl)}</div>
        </div>
      </div>

      <div className="space-y-2">
        {chains.map((chain, index) => (
          <div
            key={chain.name}
            className="flex items-center justify-between p-3 bg-[#2b3139] rounded-lg"
          >
            <div className="flex items-center gap-3">
              <div className="text-[#848e9c] text-sm font-bold w-6">{index + 1}</div>
              <div>
                <div className="text-[#eaecef] font-semibold">{chain.name}</div>
                {chain.tokenSymbol && (
                  <div className="text-xs text-[#848e9c]">{chain.tokenSymbol}</div>
                )}
              </div>
            </div>
            <div className="text-right">
              <div className="text-[#eaecef] font-semibold">{formatCurrency(chain.tvl)}</div>
              <div className="text-xs text-[#848e9c]">
                {((chain.tvl / totalTvl) * 100).toFixed(1)}%
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

