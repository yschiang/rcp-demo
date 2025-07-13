import React from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import StrategyBuilder from './pages/StrategyBuilder'
import StrategyList from './pages/StrategyList'

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <header className="bg-white shadow">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between h-16">
              <div className="flex items-center">
                <h1 className="text-xl font-semibold text-gray-900">
                  Wafer Sampling Strategy System
                </h1>
              </div>
            </div>
          </div>
        </header>

        <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
          <Routes>
            <Route path="/strategies" element={<StrategyList />} />
            <Route path="/strategy-builder" element={<StrategyBuilder />} />
            <Route path="/strategies/:id" element={<div>Strategy Detail (TODO)</div>} />
            <Route path="/strategies/:id/edit" element={<div>Strategy Edit (TODO)</div>} />
            <Route path="/" element={<Navigate to="/strategies" replace />} />
          </Routes>
        </main>
      </div>
    </Router>
  )
}

export default App