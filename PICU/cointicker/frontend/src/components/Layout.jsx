import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import './Layout.css'

const Layout = ({ children }) => {
  const location = useLocation()

  const navItems = [
    { path: '/app', label: '대시보드', icon: '📊' },
    { path: '/app/news', label: '뉴스', icon: '📰' },
    { path: '/app/insights', label: '인사이트', icon: '💡' },
    { path: '/app/settings', label: '설정', icon: '⚙️' },
  ]

  return (
    <div className="layout">
      <header className="header">
        <div className="header-content">
          <Link to="/app" className="logo">
            <span className="logo-icon">🪙</span>
            <span className="logo-text">CoinTicker</span>
          </Link>
          <nav className="nav">
            <Link
              to="/"
              className={`nav-item ${location.pathname === '/' ? 'active' : ''}`}
            >
              <span className="nav-icon">🏠</span>
              <span className="nav-label">홈</span>
            </Link>
            {navItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                className={`nav-item ${
                  location.pathname === item.path ? 'active' : ''
                }`}
              >
                <span className="nav-icon">{item.icon}</span>
                <span className="nav-label">{item.label}</span>
              </Link>
            ))}
          </nav>
        </div>
      </header>
      <main className="main-content">{children}</main>
      <footer className="footer">
        <p>CoinTicker - AI 기반 암호화폐 투자 인사이트 플랫폼</p>
        <p>© 2025 | 빅데이터 파이프라인 & 실시간 감성 분석</p>
      </footer>
    </div>
  )
}

export default Layout

