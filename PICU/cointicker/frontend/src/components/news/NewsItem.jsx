import React from 'react'
import { format } from 'date-fns'
import './NewsItem.css'

const NewsItem = ({ news }) => {
  const formatDate = (dateString) => {
    if (!dateString) return '날짜 없음'
    try {
      return format(new Date(dateString), 'yyyy-MM-dd HH:mm')
    } catch {
      return dateString
    }
  }

  const getSentimentColor = (sentiment) => {
    if (sentiment > 0.5) return '#43e97b' // 긍정
    if (sentiment < -0.5) return '#ff6b6b' // 부정
    return '#848e9c' // 중립
  }

  const getSentimentLabel = (sentiment) => {
    if (sentiment > 0.5) return '긍정'
    if (sentiment < -0.5) return '부정'
    return '중립'
  }

  return (
    <div className="news-item">
      <div className="news-header">
        <div className="news-source">{news.source || 'Unknown'}</div>
        {news.sentiment !== undefined && (
          <div
            className="news-sentiment"
            style={{ color: getSentimentColor(news.sentiment) }}
          >
            {getSentimentLabel(news.sentiment)}
          </div>
        )}
      </div>
      <h3 className="news-title">
        {news.url ? (
          <a href={news.url} target="_blank" rel="noopener noreferrer">
            {news.title || '제목 없음'}
          </a>
        ) : (
          news.title || '제목 없음'
        )}
      </h3>
      {news.content && (
        <p className="news-content">{news.content.substring(0, 200)}...</p>
      )}
      <div className="news-footer">
        <span className="news-date">{formatDate(news.published_at)}</span>
        {news.keywords && news.keywords.length > 0 && (
          <div className="news-keywords">
            {news.keywords.slice(0, 3).map((keyword, idx) => (
              <span key={idx} className="keyword-tag">
                {keyword}
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default NewsItem

