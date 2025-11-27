import React from 'react'
import { Link } from 'react-router-dom'
import './NotFound.css'

const NotFound = () => {
  return (
    <div className="not-found">
      <div className="not-found-content">
        <h1>404</h1>
        <h2>페이지를 찾을 수 없습니다</h2>
        <p>요청하신 페이지가 존재하지 않거나 이동되었을 수 있습니다.</p>
        <div className="not-found-actions">
          <Link to="/" className="btn-primary">
            홈으로 가기
          </Link>
          <Link to="/app" className="btn-secondary">
            대시보드로 가기
          </Link>
        </div>
      </div>
    </div>
  )
}

export default NotFound

