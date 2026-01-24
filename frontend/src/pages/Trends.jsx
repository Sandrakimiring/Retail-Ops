import { useState, useEffect } from 'react'
import api, { formatCurrency, formatPercent } from '../utils/api'

function Trends() {
    const [trendsData, setTrendsData] = useState([])
    const [stores, setStores] = useState([])
    const [categories, setCategories] = useState([])
    const [filters, setFilters] = useState({
        store: 'all',
        category: 'all',
        metric: 'total_revenue'
    })
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        async function loadFilters() {
            const [storesData, categoriesData] = await Promise.all([
                api.getStores(),
                api.getCategories()
            ])
            setStores(storesData)
            setCategories(categoriesData)
        }
        loadFilters()
    }, [])

    useEffect(() => {
        async function loadTrends() {
            setLoading(true)
            try {
                const data = await api.getTrends(filters)
                setTrendsData(data)
            } catch (error) {
                console.error('Error loading trends:', error)
            } finally {
                setLoading(false)
            }
        }
        loadTrends()
    }, [filters])

    const handleFilterChange = (key, value) => {
        setFilters(prev => ({ ...prev, [key]: value }))
    }

    const metricLabels = {
        'total_revenue': 'Revenue',
        'gross_margin': 'Gross Margin',
        'stockout_rate': 'Stockout Rate'
    }

    // Calculate stats
    const stats = trendsData.length > 0 ? {
        avg: trendsData.reduce((sum, d) => sum + d.actual, 0) / trendsData.length,
        min: Math.min(...trendsData.map(d => d.actual)),
        max: Math.max(...trendsData.map(d => d.actual))
    } : null

    const formatValue = (value) => {
        if (filters.metric === 'total_revenue') return formatCurrency(value)
        return formatPercent(value)
    }

    return (
        <div>
            {/* Filters */}
            <div className="filters">
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

                <div className="filter-group">
                    <label>Category</label>
                    <select
                        className="form-select"
                        value={filters.category}
                        onChange={(e) => handleFilterChange('category', e.target.value)}
                    >
                        <option value="all">All Categories</option>
                        {categories.map(c => (
                            <option key={c} value={c}>{c}</option>
                        ))}
                    </select>
                </div>

                <div className="filter-group">
                    <label>Metric</label>
                    <select
                        className="form-select"
                        value={filters.metric}
                        onChange={(e) => handleFilterChange('metric', e.target.value)}
                    >
                        <option value="total_revenue">Revenue</option>
                        <option value="gross_margin">Margin</option>
                        <option value="stockout_rate">Stockout Rate</option>
                    </select>
                </div>
            </div>

            {loading ? (
                <div className="loading-container">
                    <div className="spinner"></div>
                </div>
            ) : (
                <div className="grid grid-cols-2">
                    {/* Chart area */}
                    <div className="card">
                        <div className="card-header">
                            <h3 className="card-title">{metricLabels[filters.metric]} Trend</h3>
                        </div>
                        <div style={{ height: 300, padding: '1rem' }}>
                            <TrendChart data={trendsData} metric={filters.metric} />
                        </div>
                    </div>

                    {/* Stats */}
                    <div className="card">
                        <div className="card-header">
                            <h3 className="card-title">Summary Statistics</h3>
                        </div>
                        {stats && (
                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                                <div>
                                    <div className="text-sm text-muted">Average</div>
                                    <div style={{ fontSize: '1.5rem', fontWeight: 700 }}>{formatValue(stats.avg)}</div>
                                </div>
                                <div>
                                    <div className="text-sm text-muted">Data Points</div>
                                    <div style={{ fontSize: '1.5rem', fontWeight: 700 }}>{trendsData.length}</div>
                                </div>
                                <div>
                                    <div className="text-sm text-muted">Min</div>
                                    <div style={{ fontSize: '1rem' }}>{formatValue(stats.min)}</div>
                                </div>
                                <div>
                                    <div className="text-sm text-muted">Max</div>
                                    <div style={{ fontSize: '1rem' }}>{formatValue(stats.max)}</div>
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            )}
        </div>
    )
}

function TrendChart({ data, metric }) {
    if (!data || data.length === 0) {
        return <div className="empty-state">No data available</div>
    }

    const maxActual = Math.max(...data.map(d => d.actual))
    const maxExpected = Math.max(...data.filter(d => d.expected).map(d => d.expected))
    const maxValue = Math.max(maxActual, maxExpected || 0)

    // Simple SVG line chart
    const width = 600
    const height = 250
    const padding = 40

    const getX = (i) => padding + (i / (data.length - 1)) * (width - 2 * padding)
    const getY = (val) => height - padding - (val / maxValue) * (height - 2 * padding)

    const actualPath = data.map((d, i) => `${i === 0 ? 'M' : 'L'} ${getX(i)} ${getY(d.actual)}`).join(' ')
    const expectedPath = data
        .filter(d => d.expected !== null)
        .map((d, i) => `${i === 0 ? 'M' : 'L'} ${getX(data.indexOf(d))} ${getY(d.expected)}`)
        .join(' ')

    return (
        <svg width="100%" height="100%" viewBox={`0 0 ${width} ${height}`} style={{ overflow: 'visible' }}>
            {/* Grid lines */}
            {[0, 0.25, 0.5, 0.75, 1].map(pct => (
                <line
                    key={pct}
                    x1={padding}
                    y1={getY(maxValue * pct)}
                    x2={width - padding}
                    y2={getY(maxValue * pct)}
                    stroke="var(--border)"
                    strokeDasharray="4"
                />
            ))}

            {/* Expected line */}
            {expectedPath && (
                <path
                    d={expectedPath}
                    fill="none"
                    stroke="var(--secondary)"
                    strokeWidth="2"
                    strokeDasharray="5,5"
                />
            )}

            {/* Actual line */}
            <path
                d={actualPath}
                fill="none"
                stroke="var(--primary)"
                strokeWidth="2"
            />

            {/* Legend */}
            <g transform={`translate(${padding}, ${height - 10})`}>
                <line x1="0" y1="0" x2="20" y2="0" stroke="var(--primary)" strokeWidth="2" />
                <text x="25" y="4" fontSize="12" fill="var(--text-muted)">Actual</text>
                <line x1="80" y1="0" x2="100" y2="0" stroke="var(--secondary)" strokeWidth="2" strokeDasharray="5,5" />
                <text x="105" y="4" fontSize="12" fill="var(--text-muted)">Expected</text>
            </g>
        </svg>
    )
}

export default Trends
