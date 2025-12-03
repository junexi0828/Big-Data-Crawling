import React from 'react'
import './MarketOverview.css'

const MarketOverview = ({ summary }) => {
  if (!summary) return null

  const overviewItems = [
    {
      label: '최근 24시간 뉴스',
      value: summary.last_24h_news || 0,
    },
    {
      label: '긍정 비율',
      value: summary.positive_ratio
        ? `${(summary.positive_ratio * 100).toFixed(1)}%`
        : 'N/A',
    },
    {
      label: '부정 비율',
      value: summary.negative_ratio
        ? `${(summary.negative_ratio * 100).toFixed(1)}%`
        : 'N/A',
    },
    {
      label: '데이터 소스',
      value: summary.data_sources?.join(', ') || 'N/A',
    },
  ]

  return (
    <div className="market-overview">
      {overviewItems.map((item, index) => (
        <div key={index} className="overview-item">
          <div className="overview-label">{item.label}</div>
          <div className="overview-value">{item.value}</div>
        </div>
      ))}
    </div>
  )
}

export default MarketOverview

