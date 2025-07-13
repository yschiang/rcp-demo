import React, { useState } from 'react'
import StrategyForm from '../components/StrategyForm'

export default function StrategyBuilder() {
  return (
    <div style={{ padding: '2rem' }}>
      <h2>Strategy Builder</h2>
      <StrategyForm />
    </div>
  )
}
