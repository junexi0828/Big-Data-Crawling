import React, { useState, useEffect } from 'react'
import { dashboardAPI } from '../services/api'
import SummaryCards from '../components/dashboard/SummaryCards'
import SentimentChart from '../components/dashboard/SentimentChart'
import MarketOverview from '../components/dashboard/MarketOverview'
import './Dashboard.css'

const Dashboard = () => {
  const [summary, setSummary] = useState(null)
  const [sentimentData, setSentimentData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    loadData()
    // 30초마다 자동 새로고침
    const interval = setInterval(loadData, 30000)
    return () => clearInterval(interval)
  }, [])

  const loadData = async () => {
    try {
      setLoading(true)
      const [summaryData, sentimentTimeline] = await Promise.all([
        dashboardAPI.getSummary(),
        dashboardAPI.getSentimentTimeline(7),
      ])
      setSummary(summaryData)
      setSentimentData(sentimentTimeline)
      setError(null)
    } catch (err) {
      console.error('Failed to load dashboard data:', err)
      setError('데이터를 불러오는데 실패했습니다.')
    } finally {
      setLoading(false)
    }
  }

  if (loading && !summary) {
    return (
      <div className="dashboard-loading">
        <div className="loading-spinner"></div>
        <p>데이터를 불러오는 중...</p>
      </div>
    )
  }

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>📊 대시보드</h1>
        <button onClick={loadData} className="refresh-btn" disabled={loading}>
          {loading ? '새로고침 중...' : '🔄 새로고침'}
        </button>
      </div>

      {error && (
        <div className="error-message">
          <p>⚠️ {error}</p>
          <button onClick={loadData}>다시 시도</button>
        </div>
      )}

      {summary && <SummaryCards summary={summary} />}

      <div className="dashboard-grid">
        <div className="dashboard-section">
          <h2>감성 분석 추이</h2>
          {sentimentData ? (
            <SentimentChart data={sentimentData} />
          ) : (
            <div className="chart-placeholder">차트 데이터 로딩 중...</div>
          )}
        </div>

        <div className="dashboard-section">
          <h2>시장 개요</h2>
          {summary ? (
            <MarketOverview summary={summary} />
          ) : (
            <div className="chart-placeholder">데이터 로딩 중...</div>
          )}
        </div>
      </div>
    </div>
  )
}

export default Dashboard

