import { useLocation } from 'react-router-dom'

function Header() {
    const location = useLocation()

    const getPageTitle = () => {
        switch (location.pathname) {
            case '/': return 'Dashboard'
            case '/anomalies': return 'Anomaly Feed'
            case '/trends': return 'Historical Trends'
            case '/explorer': return 'Store & Category Explorer'
            case '/settings': return 'Settings'
            default: return 'Dashboard'
        }
    }

    const toggleTheme = () => {
        const html = document.documentElement
        const current = html.getAttribute('data-theme')
        html.setAttribute('data-theme', current === 'dark' ? 'light' : 'dark')
    }

    return (
        <header className="header">
            <div className="header-left">
                <h1 style={{ fontSize: '1.125rem', fontWeight: 700 }}>{getPageTitle()}</h1>
            </div>
            <div className="header-right">
                <button className="btn btn-ghost" onClick={toggleTheme} aria-label="Toggle theme">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
                    </svg>
                </button>
            </div>
        </header>
    )
}

export default Header
