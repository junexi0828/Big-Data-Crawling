import { Badge } from "./ui/badge";
import { AlertCircle, TrendingUp, Activity } from "lucide-react";

interface Insight {
  id: number;
  type: string;
  symbol: string;
  description: string;
  severity: "high" | "medium" | "low";
  timestamp: string;
}

interface LatestInsightsProps {
  insights: Insight[];
}

export function LatestInsights({ insights }: LatestInsightsProps) {
  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "high": return "bg-[#ff6b6b]/10 text-[#ff6b6b] border-[#ff6b6b]/20";
      case "medium": return "bg-[#f0b90b]/10 text-[#f0b90b] border-[#f0b90b]/20";
      case "low": return "bg-[#43e97b]/10 text-[#43e97b] border-[#43e97b]/20";
      default: return "bg-[#848e9c]/10 text-[#848e9c] border-[#848e9c]/20";
    }
  };

  const getTypeIcon = (type: string) => {
    if (type.includes("sentiment")) return AlertCircle;
    if (type.includes("volume")) return TrendingUp;
    return Activity;
  };

  return (
    <div className="bg-[#1e2329] border border-[#2b3139] rounded-xl p-6 hover:border-[#667eea]/50 transition-all shadow-lg hover:shadow-xl duration-300">
      <h3 className="text-[#eaecef] mb-4">Latest Insights</h3>

      <div className="space-y-3 max-h-[400px] overflow-y-auto pr-2 custom-scrollbar">
        {insights.length === 0 ? (
          // 더미 인사이트 데이터
          [
            {
              id: 1,
              type: "trend_reversal",
              symbol: "ADA",
              description: "ADA 추세 반전 신호: RSI 과매수, MACD 상승",
              severity: "high" as const,
              timestamp: "0분 전",
            },
            {
              id: 2,
              type: "trend_reversal",
              symbol: "ADA",
              description: "ADA 추세 반전 신호: RSI 과매수, MACD 상승",
              severity: "high" as const,
              timestamp: "0분 전",
            },
            {
              id: 3,
              type: "trend_reversal",
              symbol: "ADA",
              description: "ADA 추세 반전 신호: RSI 과매수, MACD 상승",
              severity: "high" as const,
              timestamp: "6분 전",
            },
          ].map((insight) => {
            const Icon = getTypeIcon(insight.type);
            return (
              <div
                key={insight.id}
                className="p-3 bg-[#0b0e11] border border-[#2b3139] rounded-lg hover:border-[#667eea]/30 transition-all duration-200 cursor-pointer hover:scale-[1.02]"
              >
                <div className="flex items-start gap-3">
                  <div className="w-8 h-8 rounded-lg bg-[#667eea]/10 flex items-center justify-center flex-shrink-0 mt-1 transition-transform hover:scale-110 duration-200">
                    <Icon className="w-4 h-4 text-[#667eea]" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1 flex-wrap">
                      <Badge className={`${getSeverityColor(insight.severity)} border text-xs px-2 py-0`}>
                        {insight.severity}
                      </Badge>
                      <Badge className="bg-[#667eea]/10 text-[#667eea] border-[#667eea]/20 border text-xs px-2 py-0">
                        {insight.symbol}
                      </Badge>
                    </div>
                    <p className="text-sm text-[#eaecef] mb-1 line-clamp-2">
                      {insight.description}
                    </p>
                    <p className="text-xs text-[#848e9c]">{insight.timestamp}</p>
                  </div>
                </div>
              </div>
            );
          })
        ) : (
          insights.map((insight) => {
          const Icon = getTypeIcon(insight.type);

          return (
            <div
              key={insight.id}
              className="p-3 bg-[#0b0e11] border border-[#2b3139] rounded-lg hover:border-[#667eea]/30 transition-all duration-200 cursor-pointer hover:scale-[1.02]"
            >
              <div className="flex items-start gap-3">
                <div className="w-8 h-8 rounded-lg bg-[#667eea]/10 flex items-center justify-center flex-shrink-0 mt-1 transition-transform hover:scale-110 duration-200">
                  <Icon className="w-4 h-4 text-[#667eea]" />
                </div>

                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1 flex-wrap">
                    <Badge className={`${getSeverityColor(insight.severity)} border text-xs px-2 py-0`}>
                      {insight.severity}
                    </Badge>
                    <Badge className="bg-[#667eea]/10 text-[#667eea] border-[#667eea]/20 border text-xs px-2 py-0">
                      {insight.symbol}
                    </Badge>
                  </div>

                  <p className="text-sm text-[#eaecef] mb-1 line-clamp-2">
                    {insight.description}
                  </p>

                  <p className="text-xs text-[#848e9c]">{insight.timestamp}</p>
                </div>
              </div>
            </div>
          );
        })
        )}
      </div>

      <style>{`
        .custom-scrollbar::-webkit-scrollbar {
          width: 6px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: #0b0e11;
          border-radius: 3px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: #2b3139;
          border-radius: 3px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background: #667eea;
        }
      `}</style>
    </div>
  );
}