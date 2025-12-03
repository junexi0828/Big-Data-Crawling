import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Home from './pages/Home'
import Dashboard from './pages/Dashboard'
import News from './pages/News'
import Insights from './pages/Insights'
import Settings from './pages/Settings'
import NotFound from './pages/NotFound'

function App() {
  return (
    <Router>
      <Routes>
        {/* 홈 페이지 (소개) - 레이아웃 없음 */}
        <Route path="/" element={<Home />} />

        {/* 앱 페이지들 - 레이아웃 있음 */}
        <Route path="/app" element={<Layout><Dashboard /></Layout>} />
        <Route path="/app/news" element={<Layout><News /></Layout>} />
        <Route path="/app/insights" element={<Layout><Insights /></Layout>} />
        <Route path="/app/settings" element={<Layout><Settings /></Layout>} />

        {/* 404 페이지 */}
        <Route path="*" element={<NotFound />} />
      </Routes>
    </Router>
  )
}

export default App

