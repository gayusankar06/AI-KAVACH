import { useEffect, useState } from 'react'
import { NavLink } from 'react-router-dom'

const items = [
  { to: '/dashboard', label: 'Dashboard', icon: '▦' },
  { to: '/kavach-crs', label: 'Kavach CRS', icon: '🛡️' },
  { to: '/projects', label: 'Projects', icon: '▤' },
  { to: '/code-security', label: 'Code Security', icon: '⌁' },
  { to: '/network-lens', label: 'Netrix', icon: '⬡' },
  { to: '/ai-chatbox', label: 'AI Chatbox', icon: '❍' },
  { to: '/pentest', label: 'Pentest', icon: '▲' },
  { to: '/report', label: 'Report', icon: '▣' },
]

export default function Sidebar({ user, onLogout }) {
  const [theme, setTheme] = useState(
    () => localStorage.getItem('cyberlens_theme') || 'dark'
  )

  useEffect(() => {
    document.documentElement.dataset.theme = theme
    localStorage.setItem('cyberlens_theme', theme)
  }, [theme])

  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <span className="brand-icon">◉</span>
        <span>CyberLens</span>
      </div>
      <nav className="sidebar-nav">
        {items.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              'nav-item' + (isActive ? ' active' : '')
            }
          >
            <span className="nav-icon">{item.icon}</span>
            <span>{item.label}</span>
          </NavLink>
        ))}
      </nav>
      <div className="sidebar-footer">
        <div className="theme-toggle" role="group" aria-label="Theme">
          <button
            className={theme === 'dark' ? 'active' : ''}
            onClick={() => setTheme('dark')}
          >
            <span className="toggle-icon">◐</span>
            <span>Dark</span>
          </button>
          <button
            className={theme === 'light' ? 'active' : ''}
            onClick={() => setTheme('light')}
          >
            <span className="toggle-icon">◑</span>
            <span>Light</span>
          </button>
        </div>
        <div className="sidebar-user">
          <div className="avatar">{user?.username?.charAt(0)?.toUpperCase()}</div>
          <div className="user-info">
            <div className="user-name">{user?.username}</div>
            <div className="user-email">{user?.email}</div>
          </div>
        </div>
        <button className="logout-btn" onClick={onLogout}>
          Log out
        </button>
      </div>
    </aside>
  )
}