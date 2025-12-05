import { Badge } from "./ui/badge";
import { ExternalLink, Circle } from "lucide-react";
import { useState } from "react";

interface NewsItem {
  id: number;
  source: string;
  title: string;
  url: string;
  publishedAt: string;
  keywords: string[];
  sentiment: number;
}

interface NewsCardProps {
  news: NewsItem;
}

export function NewsCard({ news }: NewsCardProps) {
  const [expanded, setExpanded] = useState(false);

  const getSentimentInfo = (sentiment: number) => {
    if (sentiment > 0.2) {
      return { label: "Positive", color: "#43e97b", bgColor: "bg-[#43e97b]/10", borderColor: "border-[#43e97b]/20" };
    } else if (sentiment < -0.2) {
      return { label: "Negative", color: "#ff6b6b", bgColor: "bg-[#ff6b6b]/10", borderColor: "border-[#ff6b6b]/20" };
    }
    return { label: "Neutral", color: "#848e9c", bgColor: "bg-[#848e9c]/10", borderColor: "border-[#848e9c]/20" };
  };

  const getSourceColor = (source: string) => {
    const colors = ["#667eea", "#f0b90b", "#43e97b", "#ff6b6b", "#f093fb", "#4facfe"];
    const index = source.split("").reduce((acc, char) => acc + char.charCodeAt(0), 0) % colors.length;
    return colors[index];
  };

  const sentimentInfo = getSentimentInfo(news.sentiment);
  const sourceColor = getSourceColor(news.source);

  return (
    <div className="bg-[#1e2329] border border-[#2b3139] rounded-xl p-5 hover:border-[#667eea]/50 transition-all shadow-lg">
      <div className="flex items-start justify-between gap-4 mb-3">
        <Badge 
          className="border text-xs px-2 py-1"
          style={{ 
            backgroundColor: `${sourceColor}20`, 
            color: sourceColor,
            borderColor: `${sourceColor}40`
          }}
        >
          {news.source}
        </Badge>
        
        <div className="flex items-center gap-2">
          <Circle 
            className="w-2 h-2 fill-current"
            style={{ color: sentimentInfo.color }}
          />
          <span className="text-xs" style={{ color: sentimentInfo.color }}>
            {sentimentInfo.label} ({news.sentiment.toFixed(2)})
          </span>
        </div>
      </div>

      <a 
        href={news.url}
        target="_blank"
        rel="noopener noreferrer"
        className="group"
      >
        <h4 className="text-[#eaecef] mb-2 group-hover:text-[#667eea] transition-colors flex items-start gap-2">
          {news.title}
          <ExternalLink className="w-4 h-4 flex-shrink-0 opacity-0 group-hover:opacity-100 transition-opacity mt-1" />
        </h4>
      </a>

      <div className="flex items-center justify-between mb-3">
        <span className="text-xs text-[#848e9c]">{news.publishedAt}</span>
      </div>

      <div className="flex flex-wrap gap-2 mb-3">
        {news.keywords.slice(0, expanded ? news.keywords.length : 3).map((keyword, index) => (
          <Badge 
            key={index}
            className="bg-[#2b3139] text-[#848e9c] border-[#2b3139] text-xs px-2 py-0"
          >
            {keyword}
          </Badge>
        ))}
        {news.keywords.length > 3 && (
          <button
            onClick={() => setExpanded(!expanded)}
            className="text-xs text-[#667eea] hover:text-[#764ba2] transition-colors"
          >
            {expanded ? "Show less" : `+${news.keywords.length - 3} more`}
          </button>
        )}
      </div>
    </div>
  );
}
