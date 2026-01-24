import { useState, useEffect } from 'react'
import api, { formatCurrency } from '../utils/api'

function Explorer() {
    const [stores, setStores] = useState([])
    const [categories, setCategories] = useState([])
    const [selected, setSelected] = useState(null)
    const [entityData, setEntityData] = useState(null)
    const [loading, setLoading] = useState(false)

    useEffect(() => {
        async function loadEntities() {
            const [storesData, categoriesData] = await Promise.all([
                api.getStores(),
                api.getCategories()
            ])
            setStores(storesData)
            setCategories(categoriesData)
        }
        loadEntities()
    }, [])

    const selectEntity = async (type, id) => {
        setSelected({ type, id })
        setLoading(true)

        try {
            const { kpiDaily, anomalies } = await api.loadData()

            let entityRows, entityAnomalies, metadata

            if (type === 'store') {
                entityRows = kpiDaily.filter(r => String(r.store_id) === String(id))
                entityAnomalies = anomalies.filter(a => String(a.store_id) === String(id))
                const storeInfo = stores.find(s => String(s.store_id) === String(id)) || {}
                metadata = { name: `Store ${id}`, ...storeInfo }
            } else {
                entityRows = kpiDaily.filter(r => r.category === id)
                entityAnomalies = anomalies.filter(a => a.category === id)
                metadata = { name: id, type: 'Category' }
            }

            // Calculate health metrics
            const calcHealth = (rows, metric) => {
                const values = rows.map(r => r[metric]).filter(v => v != null)
                if (values.length === 0) return 50
                const mean = values.reduce((a, b) => a + b, 0) / values.length
                const variance = values.reduce((sum, v) => sum + Math.pow(v - mean, 2), 0) / values.length
                const cv = Math.sqrt(variance) / (mean || 1)
                return Math.max(0, Math.min(100, Math.round(100 - cv * 100)))
            }

            setEntityData({
                metadata,
                revenueHealth: calcHealth(entityRows, 'total_revenue'),
                marginHealth: calcHealth(entityRows, 'gross_margin'),
                stockoutHealth: 100 - calcHealth(entityRows, 'stockout_rate'),
                anomalies: entityAnomalies,
                dataPoints: entityRows.length
            })
        } catch (error) {
            console.error('Error loading entity:', error)
        } finally {
            setLoading(false)
        }
    }

    return (
        <div style={{ display: 'grid', gridTemplateColumns: '280px 1fr', gap: 'var(--spacing-lg)' }}>
            {/* Entity selector */}
            <div className="card" style={{ height: 'fit-content' }}>
                <div className="card-title mb-md">Stores</div>
                <ul style={{ listStyle: 'none' }}>
                    {stores.map(s => (
                        <li
                            key={s.store_id}
                            className={`nav-item ${selected?.type === 'store' && selected?.id === String(s.store_id) ? 'active' : ''}`}
                            onClick={() => selectEntity('store', String(s.store_id))}
                            style={{ cursor: 'pointer' }}
                        >
                            🏪 Store {s.store_id}
                        </li>
                    ))}
                </ul>

                <div style={{ borderTop: '1px solid var(--border)', margin: '1rem 0' }}></div>

                <div className="card-title mb-md">Categories</div>
                <ul style={{ listStyle: 'none' }}>
                    {categories.map(c => (
                        <li
                            key={c}
                            className={`nav-item ${selected?.type === 'category' && selected?.id === c ? 'active' : ''}`}
                            onClick={() => selectEntity('category', c)}
                            style={{ cursor: 'pointer' }}
                        >
                            📦 {c}
                        </li>
                    ))}
                </ul>
            </div>

            {/* Entity profile */}
            <div className="card">
                {!selected ? (
                    <div className="empty-state">
                        <div className="empty-state-icon">🏪</div>
                        <div className="empty-state-title">Select an Entity</div>
                        <div className="empty-state-description">Choose a store or category to view details</div>
                    </div>
                ) : loading ? (
                    <div className="loading-container">
                        <div className="spinner"></div>
                    </div>
                ) : entityData ? (
                    <div>
                        <h2 style={{ fontSize: '1.5rem', fontWeight: 700, marginBottom: '0.5rem' }}>
                            {entityData.metadata.name}
                        </h2>
                        <div className="text-sm text-muted mb-md">
                            {entityData.metadata.region && `Region: ${entityData.metadata.region}`}
                            {entityData.metadata.store_type && ` • Type: ${entityData.metadata.store_type}`}
                            {` • ${entityData.dataPoints} data points`}
                        </div>

                        {/* Health metrics */}
                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem', marginBottom: '2rem' }}>
                            <HealthMetric label="Revenue Health" value={entityData.revenueHealth} />
                            <HealthMetric label="Margin Health" value={entityData.marginHealth} />
                            <HealthMetric label="Stock Health" value={entityData.stockoutHealth} />
                        </div>

                        {/* Active anomalies */}
                        <div>
                            <h3 className="card-title mb-md">Active Anomalies ({entityData.anomalies.length})</h3>
                            {entityData.anomalies.length === 0 ? (
                                <div className="text-muted">No active anomalies 🎉</div>
                            ) : (
                                <ul className="issues-list">
                                    {entityData.anomalies.slice(0, 5).map((a, i) => (
                                        <li key={i} className="issue-item">
                                            <span className={`severity-dot ${a.severity}`}></span>
                                            <div style={{ flex: 1 }}>
                                                <div style={{ fontWeight: 500 }}>{formatMetric(a.metric)}</div>
                                                <div className="text-sm text-muted">
                                                    {a.duration_days} days • {formatCurrency(a.max_impact)}
                                                </div>
                                            </div>
                                            <span className={`badge badge-${a.severity}`}>{a.severity}</span>
                                        </li>
                                    ))}
                                </ul>
                            )}
                        </div>
                    </div>
                ) : null}
            </div>
        </div>
    )
}

function HealthMetric({ label, value }) {
    const getClass = () => {
        if (value >= 80) return 'success'
        if (value >= 60) return 'warning'
        return 'danger'
    }

    return (
        <div style={{ textAlign: 'center' }}>
            <div className="text-sm text-muted" style={{ marginBottom: '0.5rem' }}>{label}</div>
            <div className="progress-bar" style={{ marginBottom: '0.5rem' }}>
                <div className={`progress-fill ${getClass()}`} style={{ width: `${value}%` }}></div>
            </div>
            <div style={{ fontSize: '1.25rem', fontWeight: 700 }}>{value}%</div>
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

export default Explorer
