import { TrendingUp, TrendingDown } from "lucide-react";

interface SummaryCardProps {
  icon: string;
  label: string;
  value: string | number;
  color: string;
  trend?: "up" | "down";
  trendValue?: string;
}

export function SummaryCard({ icon, label, value, color, trend, trendValue }: SummaryCardProps) {
  return (
    <div className="bg-[#1e2329] border border-[#2b3139] rounded-xl p-5 hover:border-[#667eea]/50 transition-all shadow-lg hover:shadow-xl hover:scale-[1.02] duration-300">
      <div className="flex items-start justify-between mb-3">
        <div 
          className="w-12 h-12 rounded-lg flex items-center justify-center text-2xl transition-transform hover:scale-110 duration-300"
          style={{ backgroundColor: `${color}20` }}
        >
          {icon}
        </div>
        {trend && trendValue && (
          <div className={`flex items-center gap-1 px-2 py-1 rounded-md ${
            trend === "up" ? "bg-[#43e97b]/10 text-[#43e97b]" : "bg-[#ff6b6b]/10 text-[#ff6b6b]"
          }`}>
            {trend === "up" ? (
              <TrendingUp className="w-3 h-3" />
            ) : (
              <TrendingDown className="w-3 h-3" />
            )}
            <span className="text-xs">{trendValue}</span>
          </div>
        )}
      </div>
      
      <div className="space-y-1">
        <div className="text-3xl text-[#eaecef] transition-colors duration-300" style={{ color }}>{value}</div>
        <div className="text-sm text-[#848e9c]">{label}</div>
      </div>
    </div>
  );
}