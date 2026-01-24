import { useState } from 'react'

function Settings() {
    const [settings, setSettings] = useState({
        minDays: 2,
        minImpact: 100,
        baselineWindow: 30,
        boundsMultiplier: 2.0
    })

    const [saved, setSaved] = useState(false)

    const handleChange = (key, value) => {
        setSettings(prev => ({ ...prev, [key]: value }))
        setSaved(false)
    }

    const handleSave = () => {
        // In production, this would save to backend
        console.log('Settings saved:', settings)
        setSaved(true)
        setTimeout(() => setSaved(false), 3000)
    }

    const handleReset = () => {
        setSettings({
            minDays: 2,
            minImpact: 100,
            baselineWindow: 30,
            boundsMultiplier: 2.0
        })
    }

    return (
        <div>
            {/* Detection Thresholds */}
            <div className="card mb-md">
                <h2 style={{ fontSize: '1.125rem', fontWeight: 600, marginBottom: '1.5rem', paddingBottom: '1rem', borderBottom: '1px solid var(--border)' }}>
                    Detection Thresholds
                </h2>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '1.5rem' }}>
                    <div className="form-group">
                        <label className="form-label">Min Consecutive Days</label>
                        <input
                            type="number"
                            className="form-input"
                            value={settings.minDays}
                            onChange={(e) => handleChange('minDays', parseInt(e.target.value))}
                            min="1"
                            max="30"
                        />
                    </div>
                    <div className="form-group">
                        <label className="form-label">Min Financial Impact ($)</label>
                        <input
                            type="number"
                            className="form-input"
                            value={settings.minImpact}
                            onChange={(e) => handleChange('minImpact', parseInt(e.target.value))}
                            min="0"
                        />
                    </div>
                    <div className="form-group">
                        <label className="form-label">Baseline Window (Days)</label>
                        <input
                            type="number"
                            className="form-input"
                            value={settings.baselineWindow}
                            onChange={(e) => handleChange('baselineWindow', parseInt(e.target.value))}
                            min="7"
                            max="90"
                        />
                    </div>
                    <div className="form-group">
                        <label className="form-label">Bounds Multiplier (σ)</label>
                        <input
                            type="number"
                            className="form-input"
                            value={settings.boundsMultiplier}
                            onChange={(e) => handleChange('boundsMultiplier', parseFloat(e.target.value))}
                            min="1"
                            max="5"
                            step="0.1"
                        />
                    </div>
                </div>
            </div>

            {/* Severity Thresholds */}
            <div className="card mb-md">
                <h2 style={{ fontSize: '1.125rem', fontWeight: 600, marginBottom: '1.5rem', paddingBottom: '1rem', borderBottom: '1px solid var(--border)' }}>
                    Severity Thresholds
                </h2>
                <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                    <thead>
                        <tr>
                            <th style={{ textAlign: 'left', padding: '0.5rem', borderBottom: '1px solid var(--border)', color: 'var(--text-muted)', fontSize: '0.875rem' }}>Level</th>
                            <th style={{ textAlign: 'left', padding: '0.5rem', borderBottom: '1px solid var(--border)', color: 'var(--text-muted)', fontSize: '0.875rem' }}>Min Days</th>
                            <th style={{ textAlign: 'left', padding: '0.5rem', borderBottom: '1px solid var(--border)', color: 'var(--text-muted)', fontSize: '0.875rem' }}>Min Impact</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td style={{ padding: '0.5rem' }}><span className="badge badge-low">Low</span></td>
                            <td style={{ padding: '0.5rem' }}><input type="number" className="form-input" defaultValue="2" style={{ width: 80 }} /></td>
                            <td style={{ padding: '0.5rem' }}><input type="number" className="form-input" defaultValue="100" style={{ width: 100 }} /></td>
                        </tr>
                        <tr>
                            <td style={{ padding: '0.5rem' }}><span className="badge badge-medium">Medium</span></td>
                            <td style={{ padding: '0.5rem' }}><input type="number" className="form-input" defaultValue="3" style={{ width: 80 }} /></td>
                            <td style={{ padding: '0.5rem' }}><input type="number" className="form-input" defaultValue="500" style={{ width: 100 }} /></td>
                        </tr>
                        <tr>
                            <td style={{ padding: '0.5rem' }}><span className="badge badge-high">High</span></td>
                            <td style={{ padding: '0.5rem' }}><input type="number" className="form-input" defaultValue="5" style={{ width: 80 }} /></td>
                            <td style={{ padding: '0.5rem' }}><input type="number" className="form-input" defaultValue="1000" style={{ width: 100 }} /></td>
                        </tr>
                        <tr>
                            <td style={{ padding: '0.5rem' }}><span className="badge badge-critical">Critical</span></td>
                            <td style={{ padding: '0.5rem' }}><input type="number" className="form-input" defaultValue="7" style={{ width: 80 }} /></td>
                            <td style={{ padding: '0.5rem' }}><input type="number" className="form-input" defaultValue="5000" style={{ width: 100 }} /></td>
                        </tr>
                    </tbody>
                </table>
            </div>

            {/* Appearance */}
            <div className="card mb-md">
                <h2 style={{ fontSize: '1.125rem', fontWeight: 600, marginBottom: '1.5rem', paddingBottom: '1rem', borderBottom: '1px solid var(--border)' }}>
                    Appearance
                </h2>
                <div className="form-group">
                    <label className="form-label">Theme</label>
                    <div style={{ display: 'flex', gap: '1rem' }}>
                        <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer' }}>
                            <input
                                type="radio"
                                name="theme"
                                value="light"
                                onChange={() => document.documentElement.setAttribute('data-theme', 'light')}
                                defaultChecked
                            /> Light
                        </label>
                        <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer' }}>
                            <input
                                type="radio"
                                name="theme"
                                value="dark"
                                onChange={() => document.documentElement.setAttribute('data-theme', 'dark')}
                            /> Dark
                        </label>
                    </div>
                </div>
            </div>

            {/* Actions */}
            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '1rem' }}>
                {saved && (
                    <span style={{ color: 'var(--success)', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        ✓ Settings saved
                    </span>
                )}
                <button className="btn btn-secondary" onClick={handleReset}>
                    Reset to Defaults
                </button>
                <button className="btn btn-primary" onClick={handleSave}>
                    Save Settings
                </button>
            </div>
        </div>
    )
}

export default Settings
