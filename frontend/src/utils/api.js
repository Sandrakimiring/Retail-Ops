// API utilities for fetching and processing data

const API_BASE = '/api'
const DATA_BASE = '/data/processed'
const RAW_DATA_BASE = '/data/raw'

// Parse CSV text to array of objects
function parseCSV(text) {
    const lines = text.trim().split('\n')
    const headers = lines[0].split(',').map(h => h.trim())

    return lines.slice(1).map(line => {
        const values = line.split(',')
        const obj = {}
        headers.forEach((header, i) => {
            let value = values[i]?.trim()
            if (!isNaN(value) && value !== '') {
                value = parseFloat(value)
            }
            obj[header] = value
        })
        return obj
    })
}

// Fetch CSV file
async function fetchCSV(path) {
    try {
        const response = await fetch(path)
        if (!response.ok) throw new Error(`HTTP ${response.status}`)
        const text = await response.text()
        return parseCSV(text)
    } catch (error) {
        console.error(`Error fetching ${path}:`, error)
        return []
    }
}

// Format currency
export function formatCurrency(value) {
    if (value === null || value === undefined) return '--'
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(value)
}

// Format percentage
export function formatPercent(value, decimals = 1) {
    if (value === null || value === undefined) return '--'
    return `${(value * 100).toFixed(decimals)}%`
}

// Format date
export function formatDate(dateStr) {
    if (!dateStr) return '--'
    const date = new Date(dateStr)
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

// Format date range
export function formatDateRange(start, end) {
    const s = new Date(start).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
    const e = new Date(end).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
    return `${s} - ${e}`
}

// API functions
export const api = {
    // Load all data files
    async loadData() {
        const [kpiDaily, baselines, anomalies, rootCauses, stores] = await Promise.all([
            fetchCSV(`${DATA_BASE}/kpi_daily.csv`),
            fetchCSV(`${DATA_BASE}/baselines.csv`),
            fetchCSV(`${DATA_BASE}/anomalies.csv`),
            fetchCSV(`${DATA_BASE}/root_causes.csv`),
            fetchCSV(`${RAW_DATA_BASE}/stores.csv`)
        ])
        return { kpiDaily, baselines, anomalies, rootCauses, stores }
    },

    // Get dashboard summary
    async getDashboardSummary() {
        const { kpiDaily, anomalies } = await this.loadData()

        if (!kpiDaily.length) return null

        const dates = [...new Set(kpiDaily.map(r => r.date))].sort()
        const latestDate = dates[dates.length - 1]
        const latestData = kpiDaily.filter(r => r.date === latestDate)

        const totalRevenue = latestData.reduce((sum, r) => sum + (r.total_revenue || 0), 0)
        const margins = latestData.map(r => r.gross_margin || 0)
        const avgMargin = margins.reduce((a, b) => a + b, 0) / margins.length

        const severityCounts = {
            critical: anomalies.filter(a => a.severity === 'critical').length,
            high: anomalies.filter(a => a.severity === 'high').length,
            medium: anomalies.filter(a => a.severity === 'medium').length,
            low: anomalies.filter(a => a.severity === 'low').length
        }

        const weighted = severityCounts.critical * 10 + severityCounts.high * 5 +
            severityCounts.medium * 2 + severityCounts.low
        const healthScore = Math.max(0, Math.min(100, 100 - weighted))

        return {
            latestDate,
            totalRevenue,
            avgMargin,
            totalAnomalies: anomalies.length,
            severityCounts,
            healthScore
        }
    },

    // Get anomalies with filters
    async getAnomalies(filters = {}) {
        const { anomalies, rootCauses } = await this.loadData()

        let filtered = [...anomalies]

        if (filters.severity && filters.severity !== 'all') {
            filtered = filtered.filter(a => a.severity === filters.severity)
        }
        if (filters.metric && filters.metric !== 'all') {
            filtered = filtered.filter(a => a.metric === filters.metric)
        }
        if (filters.store && filters.store !== 'all') {
            filtered = filtered.filter(a => String(a.store_id) === String(filters.store))
        }

        return filtered.map(anomaly => {
            const anomalyId = `${anomaly.store_id}_${anomaly.category}_${anomaly.start_date.replace(/-/g, '')}`
            const drivers = rootCauses
                .filter(rc => rc.anomaly_id === anomalyId)
                .sort((a, b) => b.importance_score - a.importance_score)
                .slice(0, 5)
            return { ...anomaly, anomalyId, drivers }
        })
    },

    // Get trends data
    async getTrends(filters = {}) {
        const { kpiDaily, baselines } = await this.loadData()

        let data = [...kpiDaily]
        if (filters.store && filters.store !== 'all') {
            data = data.filter(r => String(r.store_id) === String(filters.store))
        }
        if (filters.category && filters.category !== 'all') {
            data = data.filter(r => r.category === filters.category)
        }

        const metric = filters.metric || 'total_revenue'
        const byDate = {}

        data.forEach(row => {
            const date = row.date
            if (!byDate[date]) byDate[date] = []
            byDate[date].push(row[metric] || 0)
        })

        const expectedCol = `${metric}_expected`

        return Object.entries(byDate)
            .map(([date, values]) => {
                const actual = values.reduce((a, b) => a + b, 0) / values.length
                const baselineRows = baselines.filter(b => b.date === date)
                let expected = null
                if (baselineRows.length) {
                    const expectedValues = baselineRows.map(b => b[expectedCol] || 0)
                    expected = expectedValues.reduce((a, b) => a + b, 0) / expectedValues.length
                }
                return { date, actual, expected }
            })
            .sort((a, b) => new Date(a.date) - new Date(b.date))
    },

    // Get stores
    async getStores() {
        const { stores } = await this.loadData()
        return stores
    },

    // Get categories
    async getCategories() {
        const { kpiDaily } = await this.loadData()
        return [...new Set(kpiDaily.map(r => r.category))].sort()
    }
}

export default api
