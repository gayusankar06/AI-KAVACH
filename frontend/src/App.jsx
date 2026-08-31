import { Routes, Route, Navigate } from 'react-router-dom'
import { useEffect, useState } from 'react'
import Layout from './components/Layout.jsx'
import Login from './pages/Login.jsx'
import Signup from './pages/Signup.jsx'
import Dashboard from './pages/Dashboard.jsx'
import Projects from './pages/Projects.jsx'
import CodeSecurity from './pages/CodeSecurity.jsx'
import NetworkLens from './pages/NetworkLens.jsx'
import AIChat from './pages/AIChat.jsx'
import Pentest from './pages/Pentest.jsx'
import Report from './pages/Report.jsx'
import KavachCRS from './pages/KavachCRS.jsx'

export default function App() {
  const [user, setUser] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem('cyberlens_user') || 'null')
    } catch {
      return null
    }
  })

  useEffect(() => {
    if (user) {
      localStorage.setItem('cyberlens_user', JSON.stringify(user))
    } else {
      localStorage.removeItem('cyberlens_user')
    }
  }, [user])

  return (
    <Routes>
      <Route path="/login" element={<Login onLogin={setUser} />} />
      <Route path="/signup" element={<Signup />} />
      <Route
        element={
          user ? (
            <Layout user={user} onLogout={() => setUser(null)} />
          ) : (
            <Navigate to="/login" replace />
          )
        }
      >
        <Route path="/dashboard" element={<Dashboard user={user} />} />
        <Route path="/kavach-crs" element={<KavachCRS user={user} />} />
        <Route path="/projects" element={<Projects user={user} />} />
        <Route path="/code-security" element={<CodeSecurity user={user} />} />
        <Route path="/network-lens" element={<NetworkLens user={user} />} />
        <Route path="/ai-chatbox" element={<AIChat user={user} />} />
        <Route path="/pentest" element={<Pentest user={user} />} />
        <Route path="/report" element={<Report user={user} />} />
      </Route>
      <Route path="/" element={<Navigate to="/dashboard" replace />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}