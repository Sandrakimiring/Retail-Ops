import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Anomalies from './pages/Anomalies'
import Trends from './pages/Trends'
import Explorer from './pages/Explorer'
import Settings from './pages/Settings'

function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Dashboard />} />
        <Route path="anomalies" element={<Anomalies />} />
        <Route path="trends" element={<Trends />} />
        <Route path="explorer" element={<Explorer />} />
        <Route path="settings" element={<Settings />} />
      </Route>
    </Routes>
  )
}

export default App
