import React, { useState } from 'react'
import './Settings.css'

const Settings = () => {
  const [apiUrl, setApiUrl] = useState(
    localStorage.getItem('apiUrl') || 'http://localhost:5000'
  )
  const [refreshInterval, setRefreshInterval] = useState(
    localStorage.getItem('refreshInterval') || '30'
  )

  const handleSave = () => {
    localStorage.setItem('apiUrl', apiUrl)
    localStorage.setItem('refreshInterval', refreshInterval)
    alert('설정이 저장되었습니다!')
  }

  return (
    <div className="settings-page">
      <h1>⚙️ 설정</h1>

      <div className="settings-section">
        <h2>API 설정</h2>
        <div className="setting-item">
          <label>API 서버 주소</label>
          <input
            type="text"
            value={apiUrl}
            onChange={(e) => setApiUrl(e.target.value)}
            placeholder="http://localhost:5000"
          />
        </div>
      </div>

      <div className="settings-section">
        <h2>새로고침 설정</h2>
        <div className="setting-item">
          <label>자동 새로고침 간격 (초)</label>
          <input
            type="number"
            value={refreshInterval}
            onChange={(e) => setRefreshInterval(e.target.value)}
            min="10"
            max="300"
          />
        </div>
      </div>

      <div className="settings-actions">
        <button onClick={handleSave} className="save-btn">
          💾 설정 저장
        </button>
      </div>
    </div>
  )
}

export default Settings

