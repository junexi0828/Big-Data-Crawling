import React from 'react'
import { Link } from 'react-router-dom'
import './Home.css'

const Home = () => {
  return (
    <div className="home-page">
      <div className="hero">
        <h1>🪙 CoinTicker</h1>
        <p className="subtitle">AI 기반 암호화폐 투자 인사이트 플랫폼</p>
        <p className="description">
          산재된 암호화폐 정보를 자동으로 수집·분석하여,<br />
          실시간 시장 동향과 투자 기회를 한눈에 제공합니다.
        </p>
        <div className="badges">
          <span className="badge">🤖 AI 감성 분석</span>
          <span className="badge">📊 실시간 모니터링</span>
          <span className="badge">💰 99.8% 비용 절감</span>
          <span className="badge">🚀 라즈베리파이 클러스터</span>
        </div>
        <div className="cta-buttons">
          <Link to="/app" className="cta-primary">
            실시간 대시보드 시작하기 →
          </Link>
          <Link to="/app/news" className="cta-secondary">
            최신 뉴스 보기
          </Link>
        </div>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-number">100%</div>
          <div className="stat-label">정보 수집 시간 절감</div>
        </div>
        <div className="stat-card">
          <div className="stat-number">99.8%</div>
          <div className="stat-label">운영 비용 절감</div>
        </div>
        <div className="stat-card">
          <div className="stat-number">2,500개</div>
          <div className="stat-label">일일 데이터 처리량</div>
        </div>
        <div className="stat-card">
          <div className="stat-number">16,700%</div>
          <div className="stat-label">첫 해 ROI</div>
        </div>
      </div>

      <div className="features">
        <h2>🎯 핵심 기능</h2>
        <div className="features-grid">
          <div className="feature-card">
            <div className="feature-icon">⏱️</div>
            <h3>시간 절약</h3>
            <p>매일 30~60분 소요되던 정보 수집을 완전 자동화. 0분으로 단축하여 100% 시간 절감.</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">🎯</div>
            <h3>실시간성</h3>
            <p>5~30분 주기로 자동 업데이트. 24/7 시장 모니터링으로 투자 기회를 놓치지 않습니다.</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">📊</div>
            <h3>객관성</h3>
            <p>FinBERT AI 모델 기반 감성 분석. 주관적 판단을 배제한 정량화된 투자 신호를 제공합니다.</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">💰</div>
            <h3>초저비용</h3>
            <p>연간 운영비 $80. 기존 Bloomberg Terminal 대비 99.8% 비용 절감 달성.</p>
          </div>
        </div>
      </div>

      <div className="data-sources">
        <h2>🔗 5개 핵심 데이터 소스</h2>
        <div className="sources-grid">
          <div className="source-item">
            <div className="source-icon">🇰🇷</div>
            <div className="source-name">Upbit Trends</div>
            <div className="source-desc">실시간 거래량 & 트렌드</div>
          </div>
          <div className="source-item">
            <div className="source-icon">📰</div>
            <div className="source-name">Coinness</div>
            <div className="source-desc">암호화폐 전문 뉴스</div>
          </div>
          <div className="source-item">
            <div className="source-icon">📊</div>
            <div className="source-name">SaveTicker</div>
            <div className="source-desc">가격 & 기술적 지표</div>
          </div>
          <div className="source-item">
            <div className="source-icon">🤖</div>
            <div className="source-name">Perplexity</div>
            <div className="source-desc">AI 뉴스 요약</div>
          </div>
          <div className="source-item">
            <div className="source-icon">😨</div>
            <div className="source-name">CNN F&G</div>
            <div className="source-desc">공포·탐욕 지수</div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Home

