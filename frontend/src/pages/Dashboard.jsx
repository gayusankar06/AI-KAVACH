import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { apiListProjects, apiDashboardGraphs } from '../api.js'

function BarChart({ data, color, valueKey, formatLabel }) {
  const max = Math.max(...data.map((d) => d[valueKey] || 0), 1)
  if (data.length === 0) return <p className="muted">No data yet.</p>
  return (
    <div className="bar-chart">
      {data.map((d, i) => (
        <div className="bar-col" key={i}>
          <div className="bar-track">
            <div
              className="bar-fill"
              style={{
                height: `${((d[valueKey] || 0) / max) * 100}%`,
                background: color,
              }}
              title={`${d.label}: ${d[valueKey] || 0}`}
            />
          </div>
          <div className="bar-label">{formatLabel ? formatLabel(d.label) : d.label}</div>
          <div className="bar-value">{d[valueKey] || 0}</div>
        </div>
      ))}
    </div>
  )
}

function StackedBarChart({ data, formatLabel }) {
  const max = Math.max(
    ...data.map((d) => (d.user || 0) + (d.assistant || 0)),
    1
  )
  if (data.length === 0) return <p className="muted">No chat data yet.</p>
  return (
    <div className="bar-chart">
      {data.map((d, i) => (
        <div className="bar-col" key={i}>
          <div className="bar-track">
            <div
              className="bar-fill stacked-a"
              style={{
                height: `${((d.assistant || 0) / max) * 100}%`,
              }}
              title={`assistant: ${d.assistant || 0}`}
            />
            <div
              className="bar-fill stacked-u"
              style={{
                height: `${((d.user || 0) / max) * 100}%`,
              }}
              title={`user: ${d.user || 0}`}
            />
          </div>
          <div className="bar-label">{formatLabel ? formatLabel(d.label) : d.label}</div>
          <div className="bar-value">{(d.user || 0) + (d.assistant || 0)}</div>
        </div>
      ))}
    </div>
  )
}

export default function Dashboard({ user }) {
  const [projects, setProjects] = useState([])
  const [loading, setLoading] = useState(true)
  const [netrix, setNetrix] = useState([])
  const [chatUsage, setChatUsage] = useState([])
  const [graphError, setGraphError] = useState('')

  useEffect(() => {
    apiListProjects(user.id)
      .then((data) => setProjects(data.projects || []))
      .catch(() => setProjects([]))
      .finally(() => setLoading(false))
  }, [user.id])

  useEffect(() => {
    apiDashboardGraphs(user.id)
      .then((data) => {
        setNetrix(data.netrix || [])
        setChatUsage(data.chat_usage || [])
      })
      .catch((err) => setGraphError(err.message))
  }, [user.id])

  const totalPackets = netrix.reduce((s, n) => s + (n.packet_count || 0), 0)
  const totalChat = chatUsage.reduce(
    (s, d) => s + (d.user || 0) + (d.assistant || 0),
    0
  )

  const netrixBars = netrix.map((n, i) => ({
    label: n.interface || `S${i + 1}`,
    value: n.packet_count || 0,
  }))

  const protocolCounts = {}
  for (const n of netrix) {
    for (const [proto, count] of Object.entries(n.protocols || {})) {
      protocolCounts[proto] = (protocolCounts[proto] || 0) + count
    }
  }

  return (
    <div className="page">
      <header className="page-header">
        <h1>Dashboard</h1>
        <p className="muted">Welcome back, {user.username}</p>
      </header>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-value">{projects.length}</div>
          <div className="stat-label">Projects</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">
            {projects.reduce((sum, p) => sum + (p.file_count || 0), 0)}
          </div>
          <div className="stat-label">Total Files</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{netrix.length}</div>
          <div className="stat-label">Capture Sessions</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{totalPackets}</div>
          <div className="stat-label">Packets Captured</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{totalChat}</div>
          <div className="stat-label">Chat Messages</div>
        </div>
      </div>

      <div className="split">
        <div className="col">
          <section className="panel">
            <div className="panel-head">
              <h2>Netrix Analysis Report</h2>
              <span className="muted">Packets per capture session</span>
            </div>
            {graphError && <div className="error">{graphError}</div>}
            <BarChart
              data={netrixBars}
              color="linear-gradient(180deg, #e5e5e5, #666666)"
              valueKey="value"
              formatLabel={(l) => (l.length > 12 ? l.slice(0, 11) + '…' : l)}
            />
            {netrix.length === 0 && (
              <p className="muted">
                No network captures yet. Run a capture in Netrix to populate
                this graph.
              </p>
            )}
            {Object.keys(protocolCounts).length > 0 && (
              <div className="legend">
                {Object.entries(protocolCounts).map(([proto, count]) => (
                  <span className="legend-item" key={proto}>
                    <span className="legend-dot proto-dot" /> {proto} — {count}
                  </span>
                ))}
              </div>
            )}
          </section>
        </div>

        <div className="col">
          <section className="panel">
            <div className="panel-head">
              <h2>Chat Usage</h2>
              <span className="muted">Messages per day (user + assistant)</span>
            </div>
            <div className="legend">
              <span className="legend-item">
                <span className="legend-dot stacked-u" /> User
              </span>
              <span className="legend-item">
                <span className="legend-dot stacked-a" /> Assistant
              </span>
            </div>
            <StackedBarChart
              data={chatUsage.map((d) => ({
                label: d.day,
                user: d.user,
                assistant: d.assistant,
              }))}
              formatLabel={(l) => (l ? l.slice(5) : l)}
            />
            {chatUsage.length === 0 && (
              <p className="muted">
                No chat activity yet. Ask the AI in the Chatbox to see usage
                here.
              </p>
            )}
          </section>
        </div>
      </div>

      <section className="panel">
        <div className="panel-head">
          <h2>Recent Projects</h2>
          <Link className="link-btn" to="/projects">
            Open Projects
          </Link>
        </div>
        {loading ? (
          <p className="muted">Loading...</p>
        ) : projects.length === 0 ? (
          <p className="muted">
            No projects yet. Go to <Link to="/projects">Projects</Link> to add
            a GitHub repository or upload a folder.
          </p>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Source</th>
                <th>Files</th>
                <th>Created</th>
              </tr>
            </thead>
            <tbody>
              {projects.slice(0, 5).map((p) => (
                <tr key={p.id}>
                  <td>{p.name}</td>
                  <td>{p.source_type}</td>
                  <td>{p.file_count}</td>
                  <td>{new Date(p.created_at).toLocaleDateString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>
    </div>
  )
}