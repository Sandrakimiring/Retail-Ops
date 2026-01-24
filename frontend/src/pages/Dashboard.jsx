import { useState, useEffect } from 'react'
import api, { formatCurrency, formatPercent } from '../utils/api'

function Dashboard() {
    const [summary, setSummary] = useState(null)
    const [topAnomalies, setTopAnomalies] = useState([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        async function loadData() {
            try {
                const summaryData = await api.getDashboardSummary()
                setSummary(summaryData)

                const anomalies = await api.getAnomalies()
                setTopAnomalies(anomalies.slice(0, 5))
            } catch (error) {
                console.error('Error loading dashboard:', error)
            } finally {
                setLoading(false)
            }
        }
        loadData()
    }, [])

    if (loading) {
        return (
            <div className="loading-container">
                <div className="spinner"></div>
            </div>
        )
    }

    if (!summary) {
        return (
            <div className="empty-state">
                <div className="empty-state-icon">📊</div>
                <div className="empty-state-title">No Data Available</div>
                <div className="empty-state-description">Run the data pipeline to generate insights.</div>
            </div>
        )
    }

    const getHealthClass = () => {
        if (summary.healthScore >= 80) return 'positive'
        if (summary.healthScore >= 60) return ''
        return 'negative'
    }

    return (
        <div>
            {/* Metrics Row */}
            <div className="dashboard-metrics">
                <div className="card metric-card">
                    <div className="card-title">Health Score</div>
                    <div className="metric-value">{summary.healthScore}%</div>
                    <div className={`metric-change ${getHealthClass()}`}>
                        {summary.healthScore >= 80 ? 'Healthy' : summary.healthScore >= 60 ? '⚠️ Warning' : '⚠️ At Risk'}
                    </div>
                </div>

                <div className="card metric-card">
                    <div className="card-title">Total Revenue</div>
                    <div className="metric-value">{formatCurrency(summary.totalRevenue)}</div>
                    <div className="metric-label">Latest day</div>
                </div>

                <div className="card metric-card">
                    <div className="card-title">Active Anomalies</div>
                    <div className="metric-value">{summary.totalAnomalies}</div>
                    <div className="metric-label">{summary.severityCounts.critical} critical</div>
                </div>

                <div className="card metric-card">
                    <div className="card-title">Avg Margin</div>
                    <div className="metric-value">{formatPercent(summary.avgMargin)}</div>
                    <div className="metric-label">Across stores</div>
                </div>
            </div>

            {/* Charts Row */}
            <div className="dashboard-charts">
                <div className="card">
                    <div className="card-header">
                        <h3 className="card-title">Severity Breakdown</h3>
                    </div>
                    <div style={{ padding: '1rem' }}>
                        <div style={{ display: 'flex', gap: '2rem', justifyContent: 'center' }}>
                            <SeverityBar label="Critical" count={summary.severityCounts.critical} color="var(--critical)" />
                            <SeverityBar label="High" count={summary.severityCounts.high} color="var(--danger)" />
                            <SeverityBar label="Medium" count={summary.severityCounts.medium} color="var(--warning)" />
                            <SeverityBar label="Low" count={summary.severityCounts.low} color="var(--success)" />
                        </div>
                    </div>
                </div>

                <div className="card">
                    <div className="card-header">
                        <h3 className="card-title">Top Issues</h3>
                    </div>
                    <ul className="issues-list">
                        {topAnomalies.map((anomaly, index) => (
                            <li key={anomaly.anomalyId} className="issue-item">
                                <span className="issue-rank">{index + 1}</span>
                                <span className={`severity-dot ${anomaly.severity}`}></span>
                                <div style={{ flex: 1 }}>
                                    <div style={{ fontWeight: 500 }}>
                                        Store {anomaly.store_id} - {formatMetric(anomaly.metric)}
                                    </div>
                                    <div className="text-sm text-muted">
                                        {anomaly.duration_days} days • {formatCurrency(anomaly.max_impact)}
                                    </div>
                                </div>
                            </li>
                        ))}
                    </ul>
                </div>
            </div>
        </div>
    )
}

function SeverityBar({ label, count, color }) {
    const maxHeight = 120
    const height = Math.max(20, (count / 10) * maxHeight)

    return (
        <div style={{ textAlign: 'center' }}>
            <div style={{
                width: 40,
                height: maxHeight,
                background: 'var(--border)',
                borderRadius: 'var(--radius-md)',
                display: 'flex',
                alignItems: 'flex-end',
                marginBottom: '0.5rem'
            }}>
                <div style={{
                    width: '100%',
                    height,
                    background: color,
                    borderRadius: 'var(--radius-md)'
                }}></div>
            </div>
            <div style={{ fontSize: '1.25rem', fontWeight: 700 }}>{count}</div>
            <div className="text-sm text-muted">{label}</div>
        </div>
    )
}

function formatMetric(metric) {
    const names = {
        'total_revenue': 'Revenue',
        'gross_margin': 'Margin',
        'stockout_rate': 'Stockout'
    }
    return names[metric] || metric
}

export default Dashboard
