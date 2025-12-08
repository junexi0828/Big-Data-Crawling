import { useState, useEffect } from "react";
import { Bell, Plus, Trash2, TrendingUp, TrendingDown } from "lucide-react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";
import { externalAPI } from "../services/api";

interface Alert {
  id: string;
  coinId: string;
  coinSymbol: string;
  condition: 'above' | 'below';
  price: number;
  active: boolean;
}

export function PriceAlerts() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [selectedCoin, setSelectedCoin] = useState<string>("");
  const [condition, setCondition] = useState<'above' | 'below'>('above');
  const [price, setPrice] = useState<string>("");
  const [availableCoins, setAvailableCoins] = useState<any[]>([]);
  const [triggeredAlerts, setTriggeredAlerts] = useState<string[]>([]);

  useEffect(() => {
    loadAvailableCoins();
    loadAlerts();
    // 30초마다 알림 체크
    const interval = setInterval(checkAlerts, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadAvailableCoins = async () => {
    try {
      const coins = await externalAPI.getCoinPrices();
      setAvailableCoins(coins.slice(0, 20));
    } catch (error) {
      console.error("코인 목록 로드 에러:", error);
    }
  };

  const loadAlerts = () => {
    const saved = localStorage.getItem('priceAlerts');
    if (saved) {
      setAlerts(JSON.parse(saved));
    }
  };

  const saveAlerts = (newAlerts: Alert[]) => {
    setAlerts(newAlerts);
    localStorage.setItem('priceAlerts', JSON.stringify(newAlerts));
  };

  const addAlert = () => {
    if (!selectedCoin || !price) return;

    const coin = availableCoins.find(c => c.id === selectedCoin);
    if (!coin) return;

    const newAlert: Alert = {
      id: Date.now().toString(),
      coinId: selectedCoin,
      coinSymbol: coin.symbol.toUpperCase(),
      condition,
      price: parseFloat(price),
      active: true,
    };

    saveAlerts([...alerts, newAlert]);
    setSelectedCoin("");
    setPrice("");
  };

  const removeAlert = (id: string) => {
    saveAlerts(alerts.filter(a => a.id !== id));
    setTriggeredAlerts(triggeredAlerts.filter(a => a !== id));
  };

  const checkAlerts = async () => {
    for (const alert of alerts.filter(a => a.active)) {
      try {
        const coinData = await externalAPI.getCoinDetail(alert.coinId);
        if (coinData) {
          const currentPrice = coinData.market_data.current_price.usd;
          const shouldTrigger =
            (alert.condition === 'above' && currentPrice >= alert.price) ||
            (alert.condition === 'below' && currentPrice <= alert.price);

          if (shouldTrigger && !triggeredAlerts.includes(alert.id)) {
            setTriggeredAlerts([...triggeredAlerts, alert.id]);
            // 브라우저 알림
            if ('Notification' in window && Notification.permission === 'granted') {
              new Notification(`${alert.coinSymbol} 가격 알림`, {
                body: `가격이 ${alert.condition === 'above' ? '상승' : '하락'}하여 $${alert.price}에 도달했습니다. 현재가: $${currentPrice.toLocaleString()}`,
                icon: '/favicon.ico',
              });
            }
          }
        }
      } catch (error) {
        console.error(`알림 체크 에러 (${alert.coinSymbol}):`, error);
      }
    }
  };

  useEffect(() => {
    // 알림 권한 요청
    if ('Notification' in window && Notification.permission === 'default') {
      Notification.requestPermission();
    }
  }, []);

  return (
    <div className="bg-[#1e2329] border border-[#2b3139] rounded-xl p-6 hover:border-[#667eea]/50 transition-all shadow-lg hover:shadow-xl duration-300">
      <div className="flex items-center gap-2 mb-6">
        <Bell className="w-5 h-5 text-[#667eea]" />
        <h3 className="text-[#eaecef] text-lg font-bold">가격 알림</h3>
      </div>

      {/* 알림 추가 폼 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-3 mb-6">
        <Select value={selectedCoin} onValueChange={setSelectedCoin}>
          <SelectTrigger className="bg-[#2b3139] border-[#2b3139]">
            <SelectValue placeholder="코인 선택" />
          </SelectTrigger>
          <SelectContent className="bg-[#1e2329] border-[#2b3139] max-h-[300px]">
            {availableCoins.map((coin) => (
              <SelectItem key={coin.id} value={coin.id} className="text-[#eaecef]">
                {coin.symbol.toUpperCase()} - {coin.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        <Select value={condition} onValueChange={(v) => setCondition(v as 'above' | 'below')}>
          <SelectTrigger className="bg-[#2b3139] border-[#2b3139]">
            <SelectValue />
          </SelectTrigger>
          <SelectContent className="bg-[#1e2329] border-[#2b3139]">
            <SelectItem value="above" className="text-[#eaecef]">이상</SelectItem>
            <SelectItem value="below" className="text-[#eaecef]">이하</SelectItem>
          </SelectContent>
        </Select>

        <Input
          type="number"
          placeholder="가격 (USD)"
          value={price}
          onChange={(e) => setPrice(e.target.value)}
          className="bg-[#2b3139] border-[#2b3139] text-[#eaecef]"
        />

        <Button
          onClick={addAlert}
          className="bg-gradient-to-r from-[#667eea] to-[#764ba2] hover:opacity-90"
        >
          <Plus className="w-4 h-4 mr-2" />
          추가
        </Button>
      </div>

      {/* 알림 목록 */}
      <div className="space-y-2">
        {alerts.length === 0 ? (
          <div className="text-center py-8 text-[#848e9c]">
            알림이 없습니다. 위에서 알림을 추가해주세요.
          </div>
        ) : (
          alerts.map((alert) => {
            const isTriggered = triggeredAlerts.includes(alert.id);
            return (
              <div
                key={alert.id}
                className={`flex items-center justify-between p-4 rounded-lg ${
                  isTriggered ? 'bg-[#43e97b]/20 border border-[#43e97b]' : 'bg-[#2b3139]'
                }`}
              >
                <div className="flex items-center gap-4">
                  <div>
                    <div className="text-[#eaecef] font-semibold">{alert.coinSymbol}</div>
                    <div className="text-xs text-[#848e9c]">
                      {alert.condition === 'above' ? '이상' : '이하'} ${alert.price.toLocaleString()}
                    </div>
                  </div>
                  {isTriggered && (
                    <div className="flex items-center gap-1 text-[#43e97b] text-sm">
                      <Bell className="w-4 h-4" />
                      <span>알림 발동!</span>
                    </div>
                  )}
                </div>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => removeAlert(alert.id)}
                  className="text-[#848e9c] hover:text-[#ff6b6b]"
                >
                  <Trash2 className="w-4 h-4" />
                </Button>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}

