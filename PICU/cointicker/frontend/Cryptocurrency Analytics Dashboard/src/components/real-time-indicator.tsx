import { useState, useEffect } from "react";
import { Wifi, WifiOff } from "lucide-react";

export function RealTimeIndicator() {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());

  useEffect(() => {
    const updateTime = () => setLastUpdate(new Date());
    const interval = setInterval(updateTime, 1000);

    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      clearInterval(interval);
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('ko-KR', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  };

  return (
    <div className="flex items-center gap-2 text-sm">
      <div className={`flex items-center gap-1 ${
        isOnline ? "text-[#43e97b]" : "text-[#ff6b6b]"
      }`}>
        {isOnline ? (
          <>
            <div className="w-2 h-2 bg-[#43e97b] rounded-full animate-pulse"></div>
            <Wifi className="w-3 h-3" />
          </>
        ) : (
          <>
            <div className="w-2 h-2 bg-[#ff6b6b] rounded-full"></div>
            <WifiOff className="w-3 h-3" />
          </>
        )}
        <span className="text-[#848e9c]">{isOnline ? "실시간" : "오프라인"}</span>
      </div>
      <span className="text-[#848e9c]">|</span>
      <span className="text-[#848e9c]">업데이트: {formatTime(lastUpdate)}</span>
    </div>
  );
}

