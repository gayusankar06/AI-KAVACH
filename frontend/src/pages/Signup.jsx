import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { apiSignup } from '../api.js'

export default function Signup() {
  const [form, setForm] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
  })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  function handleChange(e) {
    setForm({ ...form, [e.target.name]: e.target.value })
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')

    if (form.password !== form.confirmPassword) {
      setError('Passwords do not match')
      return
    }

    setLoading(true)
    try {
      await apiSignup(form)
      navigate('/login', { state: { message: 'Account created! Please log in.' } })
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-page">
      <form className="auth-card" onSubmit={handleSubmit}>
        <h1>CyberLens</h1>
        <h2>Create account</h2>
        {error && <div className="error">{error}</div>}
        <label>
          Username
          <input
            name="username"
            value={form.username}
            onChange={handleChange}
            placeholder="Choose a username (min 3 chars)"
            minLength={3}
            required
          />
        </label>
        <label>
          Email
          <input
            name="email"
            type="email"
            value={form.email}
            onChange={handleChange}
            placeholder="you@example.com"
            required
          />
        </label>
        <label>
          Password
          <input
            name="password"
            type="password"
            value={form.password}
            onChange={handleChange}
            placeholder="Min 6 characters"
            minLength={6}
            required
          />
        </label>
        <label>
          Confirm Password
          <input
            name="confirmPassword"
            type="password"
            value={form.confirmPassword}
            onChange={handleChange}
            placeholder="Repeat password"
            minLength={6}
            required
          />
        </label>
        <button type="submit" disabled={loading}>
          {loading ? 'Creating account...' : 'Sign up'}
        </button>
        <p className="switch-link">
          Already have an account? <Link to="/login">Log in</Link>
        </p>
      </form>
    </div>
  )
}