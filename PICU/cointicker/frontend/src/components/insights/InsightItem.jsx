import React from 'react'
import { format } from 'date-fns'
import './InsightItem.css'

const InsightItem = ({ insight }) => {
  const formatDate = (dateString) => {
    if (!dateString) return '날짜 없음'
    try {
      return format(new Date(dateString), 'yyyy-MM-dd HH:mm')
    } catch {
      return dateString
    }
  }

  const getPriorityColor = (priority) => {
    switch (priority?.toLowerCase()) {
      case 'high':
        return '#ff6b6b'
      case 'medium':
        return '#f0b90b'
      case 'low':
        return '#43e97b'
      default:
        return '#848e9c'
    }
  }

  return (
    <div className="insight-item">
      <div className="insight-header">
        <div className="insight-title">{insight.title || '인사이트 제목 없음'}</div>
        {insight.priority && (
          <div
            className="insight-priority"
            style={{ color: getPriorityColor(insight.priority) }}
          >
            {insight.priority.toUpperCase()}
          </div>
        )}
      </div>
      <div className="insight-content">{insight.content || insight.summary || '내용 없음'}</div>
      {insight.recommendations && insight.recommendations.length > 0 && (
        <div className="insight-recommendations">
          <div className="recommendations-title">권장사항:</div>
          <ul>
            {insight.recommendations.map((rec, idx) => (
              <li key={idx}>{rec}</li>
            ))}
          </ul>
        </div>
      )}
      <div className="insight-footer">
        <span className="insight-date">{formatDate(insight.created_at)}</span>
        {insight.confidence && (
          <span className="insight-confidence">
            신뢰도: {(insight.confidence * 100).toFixed(0)}%
          </span>
        )}
      </div>
    </div>
  )
}

export default InsightItem

