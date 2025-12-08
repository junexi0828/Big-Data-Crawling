import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:5000";

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    "Content-Type": "application/json",
  },
});

export const dashboardAPI = {
  getSummary: async () => {
    const response = await api.get('/api/dashboard/summary');
    return response.data;
  },
  getSentimentTimeline: async (days = 7) => {
    // days를 hours로 변환 (1일 = 24시간)
    const hours = days * 24;
    const response = await api.get(`/api/dashboard/sentiment-timeline?hours=${hours}`);
    return response.data;
  },
};

export const newsAPI = {
  getLatestNews: async (limit = 10) => {
    const response = await api.get(`/api/news/latest?limit=${limit}`);
    return response.data;
  },
};

export const insightsAPI = {
  getRecentInsights: async (limit = 5) => {
    const response = await api.get(`/api/insights/recent?limit=${limit}`);
    return response.data;
  },
  generateInsight: async (topic: string) => {
    const response = await api.post('/api/insights/generate', { topic });
    return response.data;
  }
};

// 외부 API (백엔드에 데이터가 없을 때 사용)
export const externalAPI = {
  // CoinGecko API - 코인 가격 데이터
  getCoinPrices: async () => {
    try {
      const response = await fetch(
        "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=8&page=1&sparkline=false&price_change_percentage=24h"
      );
      if (!response.ok) throw new Error('CoinGecko API error');
      return await response.json();
    } catch (error) {
      console.error('CoinGecko API error:', error);
      return [];
    }
  },

  // CoinGecko API - 코인 상세 정보
  getCoinDetail: async (coinId: string) => {
    try {
      const response = await fetch(
        `https://api.coingecko.com/api/v3/coins/${coinId}?localization=false&tickers=false&market_data=true&community_data=false&developer_data=false`
      );
      if (!response.ok) throw new Error('CoinGecko API error');
      return await response.json();
    } catch (error) {
      console.error('CoinGecko API error:', error);
      return null;
    }
  },

  // CryptoCompare API - 뉴스 데이터
  getCryptoNews: async () => {
    try {
      const response = await fetch(
        "https://min-api.cryptocompare.com/data/v2/news/?lang=EN&categories=BTC,ETH,Blockchain"
      );
      if (!response.ok) throw new Error('CryptoCompare API error');
      const result = await response.json();
      return result.Data || [];
    } catch (error) {
      console.error('CryptoCompare API error:', error);
      return [];
    }
  },

  // Binance API - 캔들스틱 데이터
  getBinanceKlines: async (symbol: string, interval: string = "1h", limit: number = 100) => {
    try {
      const response = await fetch(
        `https://api.binance.com/api/v3/klines?symbol=${symbol}&interval=${interval}&limit=${limit}`
      );
      if (!response.ok) throw new Error('Binance API error');
      return await response.json();
    } catch (error) {
      console.error('Binance API error:', error);
      return [];
    }
  },

  // Binance API - 24시간 통계
  getBinance24hrStats: async (symbol: string) => {
    try {
      const response = await fetch(
        `https://api.binance.com/api/v3/ticker/24hr?symbol=${symbol}`
      );
      if (!response.ok) throw new Error('Binance API error');
      return await response.json();
    } catch (error) {
      console.error('Binance API error:', error);
      return null;
    }
  },

  // CoinGecko API - 글로벌 시장 데이터
  getGlobalMarketData: async () => {
    try {
      const response = await fetch(
        "https://api.coingecko.com/api/v3/global"
      );
      if (!response.ok) throw new Error('CoinGecko API error');
      return await response.json();
    } catch (error) {
      console.error('CoinGecko Global API error:', error);
      return null;
    }
  },

  // CoinGecko API - 트렌딩 코인
  getTrendingCoins: async () => {
    try {
      const response = await fetch(
        "https://api.coingecko.com/api/v3/search/trending"
      );
      if (!response.ok) throw new Error('CoinGecko API error');
      return await response.json();
    } catch (error) {
      console.error('CoinGecko Trending API error:', error);
      return { coins: [] };
    }
  },

  // Alternative.me API - Fear & Greed Index
  getFearGreedIndex: async () => {
    try {
      const response = await fetch(
        "https://api.alternative.me/fng/?limit=1"
      );
      if (!response.ok) throw new Error('Alternative.me API error');
      const data = await response.json();
      return data.data && data.data.length > 0 ? data.data[0] : null;
    } catch (error) {
      console.error('Fear & Greed Index API error:', error);
      return null;
    }
  },

  // CoinGecko API - 카테고리별 성과
  getCategories: async () => {
    try {
      const response = await fetch(
        "https://api.coingecko.com/api/v3/coins/categories"
      );
      if (!response.ok) throw new Error('CoinGecko API error');
      return await response.json();
    } catch (error) {
      console.error('CoinGecko Categories API error:', error);
      return [];
    }
  },

  // CoinGecko API - 거래소 데이터
  getExchanges: async () => {
    try {
      const response = await fetch(
        "https://api.coingecko.com/api/v3/exchanges?per_page=10"
      );
      if (!response.ok) throw new Error('CoinGecko API error');
      return await response.json();
    } catch (error) {
      console.error('CoinGecko Exchanges API error:', error);
      return [];
    }
  },

  // DeFiLlama API - DeFi TVL (무료, API 키 불필요)
  getDefiTvl: async () => {
    try {
      const response = await fetch(
        "https://api.llama.fi/v2/chains"
      );
      if (!response.ok) throw new Error('DeFiLlama API error');
      return await response.json();
    } catch (error) {
      console.error('DeFiLlama API error:', error);
      return [];
    }
  },

  // CoinGecko API - 파생상품 데이터
  getDerivatives: async () => {
    try {
      const response = await fetch(
        "https://api.coingecko.com/api/v3/derivatives"
      );
      if (!response.ok) throw new Error('CoinGecko API error');
      return await response.json();
    } catch (error) {
      console.error('CoinGecko Derivatives API error:', error);
      return [];
    }
  },

  // CoinGecko API - 코인 히스토리 (가격 차트용)
  getCoinHistory: async (coinId: string, days: number = 7) => {
    try {
      const response = await fetch(
        `https://api.coingecko.com/api/v3/coins/${coinId}/market_chart?vs_currency=usd&days=${days}`
      );
      if (!response.ok) throw new Error('CoinGecko API error');
      return await response.json();
    } catch (error) {
      console.error('CoinGecko History API error:', error);
      return null;
    }
  }
};