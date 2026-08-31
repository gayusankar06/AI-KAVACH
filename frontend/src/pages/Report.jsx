import { useEffect, useState } from 'react'
import { apiReportData, reportPdfUrl } from '../api.js'

export default function Report({ user }) {
  const [report, setReport] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    apiReportData(user.id)
      .then((data) => setReport(data.report))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [user.id])

  if (loading) return <p className="muted">Loading report...</p>

  const totals = report?.totals || {}
  const projects = report?.projects || []
  const sessions = report?.capture_sessions || []
  const hasData = totals.findings > 0 || totals.captures > 0

  return (
    <div className="page">
      <header className="page-header">
        <h1>Report</h1>
        <p className="muted">
          Vulnerability findings and network captures stored in the database,
          compiled into an easy-to-understand report.
        </p>
      </header>

      {error && <div className="error">{error}</div>}

      <section className="panel">
        <div className="panel-head">
          <h2>Download Report</h2>
          <a className="download-btn" href={reportPdfUrl(user.id)}>
            ⬇ Download PDF Report
          </a>
        </div>
        {!hasData && (
          <p className="muted">
            No findings yet. Run a pentest tool on a project or capture network
            traffic to populate this report.
          </p>
        )}
      </section>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-value">{totals.projects || 0}</div>
          <div className="stat-label">Projects</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{totals.findings || 0}</div>
          <div className="stat-label">AI Findings</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{totals.captures || 0}</div>
          <div className="stat-label">Captures</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{totals.packets || 0}</div>
          <div className="stat-label">Packets</div>
        </div>
      </div>

      {projects.map((p) => (
        <section className="panel" key={p.id}>
          <div className="panel-head">
            <h2>{p.name}</h2>
            <span className="project-meta">
              {p.source_type}
              {p.source_url ? ' · ' + p.source_url : ''}
            </span>
          </div>
          {p.results.length === 0 ? (
            <p className="muted">No findings for this project yet.</p>
          ) : (
            <ul className="project-list">
              {p.results.map((r) => (
                <li key={r.id} className="project-item">
                  <div className="project-row">
                    <div>
                      <div className="project-name">
                        {r.tool}{' '}
                        <span className="badge stopped">finding</span>
                      </div>
                      <div className="project-meta">
                        {new Date(r.created_at).toLocaleString()}
                      </div>
                    </div>
                  </div>
                  <pre className="code-view result-preview">{r.summary}</pre>
                </li>
              ))}
            </ul>
          )}
        </section>
      ))}

      {sessions.length > 0 && (
        <section className="panel">
          <h2>Network Capture Sessions</h2>
          <table className="table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Interface</th>
                <th>Packets</th>
                <th>Status</th>
                <th>Started</th>
              </tr>
            </thead>
            <tbody>
              {sessions.map((s) => (
                <tr key={s.id}>
                  <td>{s.id}</td>
                  <td>{s.interface}</td>
                  <td>{s.packet_count}</td>
                  <td>{s.status}</td>
                  <td>{new Date(s.started_at).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      )}
    </div>
  )
}