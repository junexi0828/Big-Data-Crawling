import React, { useState, useEffect } from 'react'
import { insightsAPI } from '../services/api'
import InsightList from '../components/insights/InsightList'
import './Insights.css'

const Insights = () => {
  const [insights, setInsights] = useState([])
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    loadInsights()
    // 5분마다 자동 새로고침
    const interval = setInterval(loadInsights, 300000)
    return () => clearInterval(interval)
  }, [])

  const loadInsights = async () => {
    try {
      setLoading(true)
      const data = await insightsAPI.getRecent(20)
      setInsights(data.insights || [])
      setError(null)
    } catch (err) {
      console.error('Failed to load insights:', err)
      setError('인사이트를 불러오는데 실패했습니다.')
    } finally {
      setLoading(false)
    }
  }

  const handleGenerate = async () => {
    try {
      setGenerating(true)
      await insightsAPI.generate()
      // 생성 후 목록 새로고침
      setTimeout(loadInsights, 2000)
    } catch (err) {
      console.error('Failed to generate insights:', err)
      setError('인사이트 생성에 실패했습니다.')
    } finally {
      setGenerating(false)
    }
  }

  return (
    <div className="insights-page">
      <div className="insights-header">
        <h1>💡 투자 인사이트</h1>
        <div className="header-actions">
          <button
            onClick={handleGenerate}
            className="generate-btn"
            disabled={generating}
          >
            {generating ? '생성 중...' : '✨ 새 인사이트 생성'}
          </button>
          <button onClick={loadInsights} className="refresh-btn" disabled={loading}>
            {loading ? '새로고침 중...' : '🔄 새로고침'}
          </button>
        </div>
      </div>

      {error && (
        <div className="error-message">
          <p>⚠️ {error}</p>
          <button onClick={loadInsights}>다시 시도</button>
        </div>
      )}

      {loading && insights.length === 0 ? (
        <div className="loading">인사이트를 불러오는 중...</div>
      ) : (
        <InsightList insights={insights} />
      )}
    </div>
  )
}

export default Insights

