import { useEffect, useState } from "react";
import { X, TrendingUp, TrendingDown, DollarSign, BarChart3, Activity, Sparkles } from "lucide-react";
import { externalAPI } from "../services/api";
import { Button } from "./ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "./ui/dialog";

interface CoinDetailModalProps {
  coinId: string;
  symbol: string;
  isOpen: boolean;
  onClose: () => void;
}

interface CoinDetail {
  name: string;
  symbol: string;
  price: number;
  change24h: number;
  high24h: number;
  low24h: number;
  marketCap: number;
  volume24h: number;
  marketCapRank: number;
  recommendation: string;
  description: string;
}

export function CoinDetailModal({ coinId, symbol, isOpen, onClose }: CoinDetailModalProps) {
  const [loading, setLoading] = useState(true);
  const [coinDetail, setCoinDetail] = useState<CoinDetail | null>(null);

  useEffect(() => {
    if (isOpen && coinId) {
      loadCoinDetail();
    }
  }, [isOpen, coinId]);

  const loadCoinDetail = async () => {
    setLoading(true);
    try {
      const data = await externalAPI.getCoinDetail(coinId);
      if (data) {
        const price = data.market_data.current_price.usd;
        const change24h = data.market_data.price_change_percentage_24h;
        const marketCap = data.market_data.market_cap.usd;
        const volume24h = data.market_data.total_volume.usd;
        const high24h = data.market_data.high_24h.usd;
        const low24h = data.market_data.low_24h.usd;

        // AI 기반 투자 인사이트 생성 (demo.html 방식)
        const recommendation =
          change24h > 5
            ? "강력 매수"
            : change24h > 2
            ? "매수"
            : change24h > -2
            ? "관망"
            : change24h > -5
            ? "매도"
            : "강력 매도";

        const description = `현재 ${data.name}은(는) 24시간 동안 ${Math.abs(change24h).toFixed(2)}% ${change24h > 0 ? "상승" : "하락"}했습니다. ${
          change24h > 3
            ? "강한 상승세를 보이고 있어 단기 투자 기회로 볼 수 있습니다."
            : change24h < -3
            ? "하락세가 지속되고 있어 주의가 필요합니다."
            : "안정적인 움직임을 보이고 있습니다."
        } 시가총액 기준 ${data.market_cap_rank || "N/A"}위를 기록하고 있으며, 24시간 거래량은 $${(volume24h / 1e9).toFixed(2)}B로 ${
          volume24h > marketCap * 0.05 ? "높은" : "보통"
        } 유동성을 보이고 있습니다.`;

        setCoinDetail({
          name: data.name,
          symbol: data.symbol.toUpperCase(),
          price,
          change24h,
          high24h,
          low24h,
          marketCap,
          volume24h,
          marketCapRank: data.market_cap_rank || 0,
          recommendation,
          description,
        });
      }
    } catch (error) {
      console.error("코인 상세 정보 로드 에러:", error);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="bg-[#1e2329] border-[#2b3139] text-[#eaecef] max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-2xl font-bold flex items-center justify-between">
            <span>
              {loading ? "로딩 중..." : coinDetail ? `${coinDetail.name} (${coinDetail.symbol})` : symbol}
            </span>
            <Button
              variant="ghost"
              size="icon"
              onClick={onClose}
              className="text-[#848e9c] hover:text-[#eaecef]"
            >
              <X className="w-5 h-5" />
            </Button>
          </DialogTitle>
        </DialogHeader>

        {loading ? (
          <div className="text-center py-16">
            <div className="text-6xl mb-4 animate-spin">💰</div>
            <p className="text-[#848e9c]">인사이트를 분석하는 중...</p>
          </div>
        ) : coinDetail ? (
          <div className="space-y-6">
            {/* AI 추천 */}
            <div className="bg-gradient-to-r from-[#667eea]/20 to-[#764ba2]/20 border border-[#667eea]/30 rounded-xl p-6">
              <div className="flex items-center gap-3 mb-3">
                <Sparkles className="w-6 h-6 text-[#667eea]" />
                <h3 className="text-xl font-bold">AI 추천: <span className={coinDetail.change24h > 0 ? "text-[#43e97b]" : "text-[#ff6b6b]"}>{coinDetail.recommendation}</span></h3>
              </div>
              <p className="text-[#848e9c] leading-relaxed">{coinDetail.description}</p>
            </div>

            {/* 주요 지표 */}
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              <div className="bg-[#2b3139] rounded-lg p-4">
                <div className="flex items-center gap-2 mb-2">
                  <DollarSign className="w-4 h-4 text-[#848e9c]" />
                  <span className="text-sm text-[#848e9c]">현재가</span>
                </div>
                <div className="text-2xl font-bold text-[#eaecef]">
                  ${coinDetail.price.toLocaleString()}
                </div>
              </div>

              <div className="bg-[#2b3139] rounded-lg p-4">
                <div className="flex items-center gap-2 mb-2">
                  {coinDetail.change24h > 0 ? (
                    <TrendingUp className="w-4 h-4 text-[#43e97b]" />
                  ) : (
                    <TrendingDown className="w-4 h-4 text-[#ff6b6b]" />
                  )}
                  <span className="text-sm text-[#848e9c]">24시간 변동</span>
                </div>
                <div className={`text-2xl font-bold ${coinDetail.change24h > 0 ? "text-[#43e97b]" : "text-[#ff6b6b]"}`}>
                  {coinDetail.change24h > 0 ? "+" : ""}{coinDetail.change24h.toFixed(2)}%
                </div>
              </div>

              <div className="bg-[#2b3139] rounded-lg p-4">
                <div className="flex items-center gap-2 mb-2">
                  <TrendingUp className="w-4 h-4 text-[#43e97b]" />
                  <span className="text-sm text-[#848e9c]">24시간 최고가</span>
                </div>
                <div className="text-2xl font-bold text-[#43e97b]">
                  ${coinDetail.high24h.toLocaleString()}
                </div>
              </div>

              <div className="bg-[#2b3139] rounded-lg p-4">
                <div className="flex items-center gap-2 mb-2">
                  <TrendingDown className="w-4 h-4 text-[#ff6b6b]" />
                  <span className="text-sm text-[#848e9c]">24시간 최저가</span>
                </div>
                <div className="text-2xl font-bold text-[#ff6b6b]">
                  ${coinDetail.low24h.toLocaleString()}
                </div>
              </div>

              <div className="bg-[#2b3139] rounded-lg p-4">
                <div className="flex items-center gap-2 mb-2">
                  <BarChart3 className="w-4 h-4 text-[#848e9c]" />
                  <span className="text-sm text-[#848e9c]">시가총액</span>
                </div>
                <div className="text-2xl font-bold text-[#eaecef]">
                  ${(coinDetail.marketCap / 1e9).toFixed(2)}B
                </div>
                <div className="text-xs text-[#848e9c] mt-1">순위: {coinDetail.marketCapRank}위</div>
              </div>

              <div className="bg-[#2b3139] rounded-lg p-4">
                <div className="flex items-center gap-2 mb-2">
                  <Activity className="w-4 h-4 text-[#848e9c]" />
                  <span className="text-sm text-[#848e9c]">24시간 거래량</span>
                </div>
                <div className="text-2xl font-bold text-[#eaecef]">
                  ${(coinDetail.volume24h / 1e9).toFixed(2)}B
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="text-center py-16">
            <p className="text-[#848e9c]">데이터를 불러올 수 없습니다.</p>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}

