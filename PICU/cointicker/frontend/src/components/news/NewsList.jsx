import React from 'react'
import NewsItem from './NewsItem'
import './NewsList.css'

const NewsList = ({ news }) => {
  if (!news || news.length === 0) {
    return (
      <div className="news-empty">
        <p>표시할 뉴스가 없습니다.</p>
      </div>
    )
  }

  return (
    <div className="news-list">
      {news.map((item, index) => (
        <NewsItem key={item.id || index} news={item} />
      ))}
    </div>
  )
}

export default NewsList

