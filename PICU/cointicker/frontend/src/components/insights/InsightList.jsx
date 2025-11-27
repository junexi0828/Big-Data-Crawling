import React from 'react'
import InsightItem from './InsightItem'
import './InsightList.css'

const InsightList = ({ insights }) => {
  if (!insights || insights.length === 0) {
    return (
      <div className="insights-empty">
        <p>표시할 인사이트가 없습니다.</p>
        <p className="empty-hint">새 인사이트를 생성해보세요!</p>
      </div>
    )
  }

  return (
    <div className="insights-list">
      {insights.map((insight, index) => (
        <InsightItem key={insight.id || index} insight={insight} />
      ))}
    </div>
  )
}

export default InsightList

