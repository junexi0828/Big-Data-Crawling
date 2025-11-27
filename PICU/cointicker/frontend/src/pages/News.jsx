import React, { useState, useEffect } from 'react'
import { newsAPI } from '../services/api'
import NewsList from '../components/news/NewsList'
import './News.css'

const News = () => {
  const [news, setNews] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    loadNews()
    // 1분마다 자동 새로고침
    const interval = setInterval(loadNews, 60000)
    return () => clearInterval(interval)
  }, [])

  const loadNews = async () => {
    try {
      setLoading(true)
      const data = await newsAPI.getLatest(50)
      setNews(data.news || [])
      setError(null)
    } catch (err) {
      console.error('Failed to load news:', err)
      setError('뉴스를 불러오는데 실패했습니다.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="news-page">
      <div className="news-header">
        <h1>📰 최신 뉴스</h1>
        <button onClick={loadNews} className="refresh-btn" disabled={loading}>
          {loading ? '새로고침 중...' : '🔄 새로고침'}
        </button>
      </div>

      {error && (
        <div className="error-message">
          <p>⚠️ {error}</p>
          <button onClick={loadNews}>다시 시도</button>
        </div>
      )}

      {loading && news.length === 0 ? (
        <div className="loading">뉴스를 불러오는 중...</div>
      ) : (
        <NewsList news={news} />
      )}
    </div>
  )
}

export default News

