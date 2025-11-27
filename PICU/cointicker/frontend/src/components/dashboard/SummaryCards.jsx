import React from 'react'
import './SummaryCards.css'

const SummaryCards = ({ summary }) => {
  if (!summary) return null

  const cards = [
    {
      title: '총 뉴스 수',
      value: summary.total_news || 0,
      icon: '📰',
      color: '#667eea',
    },
    {
      title: '평균 감성 점수',
      value: summary.avg_sentiment
        ? summary.avg_sentiment.toFixed(2)
        : 'N/A',
      icon: '😊',
      color: '#f093fb',
    },
    {
      title: '최신 인사이트',
      value: summary.recent_insights || 0,
      icon: '💡',
      color: '#4facfe',
    },
    {
      title: '활성 소스',
      value: summary.active_sources || 0,
      icon: '🔗',
      color: '#43e97b',
    },
  ]

  return (
    <div className="summary-cards">
      {cards.map((card, index) => (
        <div key={index} className="summary-card">
          <div className="card-icon" style={{ color: card.color }}>
            {card.icon}
          </div>
          <div className="card-content">
            <div className="card-value">{card.value}</div>
            <div className="card-title">{card.title}</div>
          </div>
        </div>
      ))}
    </div>
  )
}

export default SummaryCards

