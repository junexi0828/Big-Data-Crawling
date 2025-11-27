/**
 * API 서비스
 * FastAPI 백엔드와 통신하는 서비스
 */
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 요청 인터셉터
api.interceptors.request.use(
  (config) => {
    // 필요시 토큰 추가 등
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 응답 인터셉터
api.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

/**
 * 대시보드 API
 */
export const dashboardAPI = {
  /**
   * 대시보드 요약 정보 조회
   */
  getSummary: async () => {
    return api.get('/api/dashboard/summary')
  },

  /**
   * 감성 분석 추이 조회
   */
  getSentimentTimeline: async (days = 7) => {
    return api.get('/api/dashboard/sentiment-timeline', {
      params: { days },
    })
  },
}

/**
 * 뉴스 API
 */
export const newsAPI = {
  /**
   * 최신 뉴스 조회
   */
  getLatest: async (limit = 20) => {
    return api.get('/api/news/latest', {
      params: { limit },
    })
  },

  /**
   * 뉴스 검색
   */
  search: async (query, limit = 20) => {
    return api.get('/api/news/search', {
      params: { query, limit },
    })
  },
}

/**
 * 인사이트 API
 */
export const insightsAPI = {
  /**
   * 최신 인사이트 조회
   */
  getRecent: async (limit = 10) => {
    return api.get('/api/insights/recent', {
      params: { limit },
    })
  },

  /**
   * 인사이트 생성
   */
  generate: async () => {
    return api.post('/api/insights/generate')
  },
}

/**
 * 헬스 체크
 */
export const healthCheck = async () => {
  try {
    const response = await api.get('/health')
    return response
  } catch (error) {
    throw error
  }
}

export default api

