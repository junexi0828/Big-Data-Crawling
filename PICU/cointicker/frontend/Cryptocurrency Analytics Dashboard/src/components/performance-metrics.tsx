import { useEffect, useState } from "react";
import { Activity, Zap, Clock } from "lucide-react";

export function PerformanceMetrics() {
  const [metrics, setMetrics] = useState({
    renderTime: 0,
    apiResponseTime: 0,
    memoryUsage: 0,
  });

  useEffect(() => {
    const measurePerformance = () => {
      // 렌더링 시간 측정
      if (performance.getEntriesByType) {
        const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
        if (navigation) {
          setMetrics(prev => ({
            ...prev,
            renderTime: navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart,
          }));
        }
      }

      // 메모리 사용량 (Chrome만 지원)
      if ((performance as any).memory) {
        const memory = (performance as any).memory;
        setMetrics(prev => ({
          ...prev,
          memoryUsage: memory.usedJSHeapSize / 1048576, // MB
        }));
      }
    };

    measurePerformance();
    const interval = setInterval(measurePerformance, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-[#1e2329] border border-[#2b3139] rounded-xl p-4">
      <div className="flex items-center gap-4 text-xs text-[#848e9c]">
        <div className="flex items-center gap-1">
          <Clock className="w-3 h-3" />
          <span>렌더: {metrics.renderTime.toFixed(0)}ms</span>
        </div>
        {metrics.memoryUsage > 0 && (
          <div className="flex items-center gap-1">
            <Activity className="w-3 h-3" />
            <span>메모리: {metrics.memoryUsage.toFixed(1)}MB</span>
          </div>
        )}
        <div className="flex items-center gap-1">
          <Zap className="w-3 h-3 text-[#43e97b]" />
          <span>실시간</span>
        </div>
      </div>
    </div>
  );
}

