import { useState, useEffect } from 'react'
import api, { formatCurrency, formatDateRange } from '../utils/api'

function Anomalies() {
    const [anomalies, setAnomalies] = useState([])
    const [stores, setStores] = useState([])
    const [filters, setFilters] = useState({
        severity: 'all',
        metric: 'all',
        store: 'all'
    })
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        async function loadStores() {
            const storesData = await api.getStores()
            setStores(storesData)
        }
        loadStores()
    }, [])

    useEffect(() => {
        async function loadAnomalies() {
            setLoading(true)
            try {
                const data = await api.getAnomalies(filters)
                setAnomalies(data)
            } catch (error) {
                console.error('Error loading anomalies:', error)
            } finally {
                setLoading(false)
            }
        }
        loadAnomalies()
    }, [filters])

    const handleFilterChange = (key, value) => {
        setFilters(prev => ({ ...prev, [key]: value }))
    }

    return (
        <div>
            {/* Filters */}
            <div className="filters">
                <div className="filter-group">
                    <label>Severity</label>
                    <select
                        className="form-select"
                        value={filters.severity}
                        onChange={(e) => handleFilterChange('severity', e.target.value)}
                    >
                        <option value="all">All Severities</option>
                        <option value="critical">Critical</option>
                        <option value="high">High</option>
                        <option value="medium">Medium</option>
                        <option value="low">Low</option>
                    </select>
                </div>

                <div className="filter-group">
                    <label>Metric</label>
                    <select
                        className="form-select"
                        value={filters.metric}
                        onChange={(e) => handleFilterChange('metric', e.target.value)}
                    >
                        <option value="all">All Metrics</option>
                        <option value="total_revenue">Revenue</option>
                        <option value="gross_margin">Margin</option>
                        <option value="stockout_rate">Stockout</option>
                    </select>
                </div>

                <div className="filter-group">
                    <label>Store</label>
                    <select
                        className="form-select"
                        value={filters.store}
                        onChange={(e) => handleFilterChange('store', e.target.value)}
                    >
                        <option value="all">All Stores</option>
                        {stores.map(s => (
                            <option key={s.store_id} value={s.store_id}>Store {s.store_id}</option>
                        ))}
                    </select>
                </div>
            </div>

            {/* Anomaly List */}
            {loading ? (
                <div className="loading-container">
                    <div className="spinner"></div>
                </div>
            ) : anomalies.length === 0 ? (
                <div className="empty-state">
                    <div className="empty-state-icon">✅</div>
                    <div className="empty-state-title">No Anomalies Found</div>
                    <div className="empty-state-description">Try adjusting your filters</div>
                </div>
            ) : (
                <div>
                    {anomalies.map(anomaly => (
                        <AnomalyCard key={anomaly.anomalyId} anomaly={anomaly} />
                    ))}
                </div>
            )}
        </div>
    )
}

function AnomalyCard({ anomaly }) {
    const metricName = {
        'total_revenue': 'Revenue',
        'gross_margin': 'Gross Margin',
        'stockout_rate': 'Stockout Rate'
    }[anomaly.metric] || anomaly.metric

    const direction = anomaly.anomaly_direction === 'high' ? 'above' : 'below'

    return (
        <div className={`anomaly-card ${anomaly.severity}`}>
            <div className="anomaly-header">
                <span className={`badge badge-${anomaly.severity}`}>{anomaly.severity}</span>
                <div>
                    <div className="anomaly-title">
                        {anomaly.entity || `Store ${anomaly.store_id}, ${anomaly.category}`}
                    </div>
                    <div className="text-sm text-muted">{metricName}</div>
                </div>
            </div>

            <p className="text-muted mb-md">
                {metricName} is {direction} expected levels
            </p>

            <div className="anomaly-stats">
                <div className="anomaly-stat">
                    <div className="anomaly-stat-value">{anomaly.duration_days}</div>
                    <div className="anomaly-stat-label">Days</div>
                </div>
                <div className="anomaly-stat">
                    <div className="anomaly-stat-value">{formatCurrency(anomaly.max_impact)}</div>
                    <div className="anomaly-stat-label">Max Impact</div>
                </div>
                <div className="anomaly-stat">
                    <div className="anomaly-stat-value">{formatDateRange(anomaly.start_date, anomaly.end_date)}</div>
                    <div className="anomaly-stat-label">Period</div>
                </div>
            </div>

            {anomaly.drivers && anomaly.drivers.length > 0 && (
                <div>
                    <div className="text-sm font-bold text-muted mb-md">Top Drivers</div>
                    {anomaly.drivers.slice(0, 3).map((driver, i) => (
                        <div key={i} className="driver-item">
                            <span className="driver-name">{formatDriverName(driver.driver)}</span>
                            <div className="driver-bar">
                                <div
                                    className="driver-bar-fill"
                                    style={{ width: `${driver.importance_score * 100}%` }}
                                ></div>
                            </div>
                            <span className="text-sm text-muted">{(driver.importance_score * 100).toFixed(0)}%</span>
                        </div>
                    ))}
                </div>
            )}
        </div>
    )
}

function formatDriverName(driver) {
    const names = {
        'stock_on_hand': 'Stock Level',
        'discount_rate': 'Discount Rate',
        'avg_markup': 'Markup',
        'units_sold': 'Units Sold',
        'price': 'Price'
    }
    return names[driver] || driver
}

export default Anomalies
