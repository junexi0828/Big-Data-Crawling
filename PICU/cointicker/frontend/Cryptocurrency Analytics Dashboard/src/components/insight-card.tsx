import { useState } from "react";
import { Badge } from "./ui/badge";
import { Button } from "./ui/button";
import { AlertCircle, TrendingUp, Activity, Eye, X, ChevronDown, ChevronUp } from "lucide-react";

interface InsightItem {
  id: number;
  type: string;
  symbol: string;
  description: string;
  severity: "high" | "medium" | "low";
  timestamp: string;
  details?: string;
}

interface InsightCardProps {
  insight: InsightItem;
  onDismiss: (id: number) => void;
}

export function InsightCard({ insight, onDismiss }: InsightCardProps) {
  const [expanded, setExpanded] = useState(false);

  const getSeverityInfo = (severity: string) => {
    switch (severity) {
      case "high": 
        return { 
          label: "High", 
          color: "#ff6b6b", 
          bgColor: "bg-[#ff6b6b]/10", 
          borderColor: "border-[#ff6b6b]/20" 
        };
      case "medium": 
        return { 
          label: "Medium", 
          color: "#f0b90b", 
          bgColor: "bg-[#f0b90b]/10", 
          borderColor: "border-[#f0b90b]/20" 
        };
      case "low": 
        return { 
          label: "Low", 
          color: "#43e97b", 
          bgColor: "bg-[#43e97b]/10", 
          borderColor: "border-[#43e97b]/20" 
        };
      default: 
        return { 
          label: "Unknown", 
          color: "#848e9c", 
          bgColor: "bg-[#848e9c]/10", 
          borderColor: "border-[#848e9c]/20" 
        };
    }
  };

  const getTypeIcon = (type: string) => {
    if (type.includes("sentiment")) return AlertCircle;
    if (type.includes("volume")) return TrendingUp;
    return Activity;
  };

  const getTypeLabel = (type: string) => {
    return type.split("_").map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(" ");
  };

  const severityInfo = getSeverityInfo(insight.severity);
  const Icon = getTypeIcon(insight.type);

  return (
    <div className="bg-[#1e2329] border border-[#2b3139] rounded-xl p-5 hover:border-[#667eea]/50 transition-all shadow-lg">
      <div className="flex items-start gap-4">
        <div 
          className="w-12 h-12 rounded-lg flex items-center justify-center flex-shrink-0"
          style={{ backgroundColor: `${severityInfo.color}20` }}
        >
          <Icon className="w-6 h-6" style={{ color: severityInfo.color }} />
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-4 mb-2">
            <div className="flex items-center gap-2 flex-wrap">
              <Badge className={`${severityInfo.bgColor} ${severityInfo.borderColor} border text-xs px-2 py-1`} style={{ color: severityInfo.color }}>
                {severityInfo.label}
              </Badge>
              <Badge className="bg-[#667eea]/10 text-[#667eea] border-[#667eea]/20 border text-xs px-2 py-1">
                {insight.symbol}
              </Badge>
              <span className="text-xs text-[#848e9c]">{getTypeLabel(insight.type)}</span>
            </div>

            <button
              onClick={() => onDismiss(insight.id)}
              className="text-[#848e9c] hover:text-[#ff6b6b] transition-colors flex-shrink-0"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          <p className="text-[#eaecef] mb-2">
            {insight.description}
          </p>

          {insight.details && (
            <div className="mb-2">
              {expanded && (
                <p className="text-sm text-[#848e9c] mb-2">
                  {insight.details}
                </p>
              )}
              <button
                onClick={() => setExpanded(!expanded)}
                className="flex items-center gap-1 text-xs text-[#667eea] hover:text-[#764ba2] transition-colors"
              >
                {expanded ? (
                  <>
                    <ChevronUp className="w-3 h-3" />
                    Show less
                  </>
                ) : (
                  <>
                    <ChevronDown className="w-3 h-3" />
                    Read more
                  </>
                )}
              </button>
            </div>
          )}

          <div className="flex items-center justify-between mt-3 pt-3 border-t border-[#2b3139]">
            <span className="text-xs text-[#848e9c]">{insight.timestamp}</span>
            
            <Button
              size="sm"
              className="bg-[#2b3139] hover:bg-[#667eea] text-[#eaecef] transition-colors h-8"
            >
              <Eye className="w-3 h-3 mr-1" />
              View Details
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
