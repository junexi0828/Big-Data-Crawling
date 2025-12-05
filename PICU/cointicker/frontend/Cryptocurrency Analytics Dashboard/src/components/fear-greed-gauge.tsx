interface FearGreedGaugeProps {
  value: number;
}

export function FearGreedGauge({ value }: FearGreedGaugeProps) {
  const getClassification = (val: number) => {
    if (val <= 20) return { label: "Extreme Fear", color: "#ff6b6b" };
    if (val <= 40) return { label: "Fear", color: "#ffa500" };
    if (val <= 60) return { label: "Neutral", color: "#848e9c" };
    if (val <= 80) return { label: "Greed", color: "#90ee90" };
    return { label: "Extreme Greed", color: "#43e97b" };
  };

  const classification = getClassification(value);
  const rotation = (value / 100) * 180 - 90;

  return (
    <div className="bg-[#1e2329] border border-[#2b3139] rounded-xl p-6 hover:border-[#667eea]/50 transition-all shadow-lg hover:shadow-xl duration-300">
      <h3 className="text-[#eaecef] mb-6">Fear & Greed Index</h3>
      
      <div className="relative w-full max-w-[280px] mx-auto">
        {/* Gauge Background */}
        <div className="relative w-full aspect-square">
          <svg viewBox="0 0 200 120" className="w-full">
            {/* Background arc */}
            <path
              d="M 20 100 A 80 80 0 0 1 180 100"
              fill="none"
              stroke="#2b3139"
              strokeWidth="20"
              strokeLinecap="round"
            />
            
            {/* Colored segments */}
            <path
              d="M 20 100 A 80 80 0 0 1 52 44"
              fill="none"
              stroke="#ff6b6b"
              strokeWidth="20"
              strokeLinecap="round"
            />
            <path
              d="M 52 44 A 80 80 0 0 1 100 20"
              fill="none"
              stroke="#ffa500"
              strokeWidth="20"
              strokeLinecap="round"
            />
            <path
              d="M 100 20 A 80 80 0 0 1 148 44"
              fill="none"
              stroke="#848e9c"
              strokeWidth="20"
              strokeLinecap="round"
            />
            <path
              d="M 148 44 A 80 80 0 0 1 180 100"
              fill="none"
              stroke="#43e97b"
              strokeWidth="20"
              strokeLinecap="round"
            />
            
            {/* Needle */}
            <g transform={`rotate(${rotation} 100 100)`} className="transition-transform duration-500">
              <line
                x1="100"
                y1="100"
                x2="100"
                y2="30"
                stroke={classification.color}
                strokeWidth="3"
                strokeLinecap="round"
              />
              <circle cx="100" cy="100" r="6" fill={classification.color} />
            </g>
          </svg>
        </div>
        
        {/* Value and Classification */}
        <div className="text-center mt-4 space-y-2">
          <div className="text-5xl transition-all duration-500" style={{ color: classification.color }}>
            {value}
          </div>
          <div className="text-lg text-[#848e9c]">{classification.label}</div>
        </div>
      </div>
      
      {/* Legend */}
      <div className="grid grid-cols-2 gap-2 mt-6 text-xs">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-[#ff6b6b]"></div>
          <span className="text-[#848e9c]">Extreme Fear</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-[#ffa500]"></div>
          <span className="text-[#848e9c]">Fear</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-[#848e9c]"></div>
          <span className="text-[#848e9c]">Neutral</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-[#43e97b]"></div>
          <span className="text-[#848e9c]">Greed</span>
        </div>
      </div>
    </div>
  );
}