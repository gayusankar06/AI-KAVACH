import { Outlet } from 'react-router-dom'
import Sidebar from './Sidebar.jsx'

export default function Layout({ user, onLogout }) {
  return (
    <div className="app-shell">
      <Sidebar user={user} onLogout={onLogout} />
      <main className="main-content">
        <Outlet />
      </main>
    </div>
  )
}