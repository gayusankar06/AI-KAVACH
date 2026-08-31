import { useCallback, useEffect, useState } from 'react'
import {
  apiListProjects,
  apiCodeScan,
  apiCodeFindings,
  apiGetFile,
  apiRunCRSPipeline,
} from '../api.js'

const severityOrder = { critical: 0, high: 1, medium: 2, low: 3, info: 4 }

export default function CodeSecurity({ user }) {
  const [projects, setProjects] = useState([])
  const [selected, setSelected] = useState('')
  const [findings, setFindings] = useState([])
  const [loading, setLoading] = useState(false)
  const [scanning, setScanning] = useState(false)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const [openFile, setOpenFile] = useState('')
  const [fileView, setFileView] = useState(null)
  const [repairingId, setRepairingId] = useState(null)
  const [repairResults, setRepairResults] = useState({})

  const loadProjects = useCallback(() => {
    apiListProjects(user.id)
      .then((data) => setProjects(data.projects || []))
      .catch((err) => setError(err.message))
  }, [user.id])

  useEffect(() => {
    loadProjects()
  }, [loadProjects])

  useEffect(() => {
    if (!selected) {
      setFindings([])
      return
    }
    apiCodeFindings(selected)
      .then((data) => setFindings(data.findings || []))
      .catch(() => setFindings([]))
  }, [selected])

  async function handleScan() {
    if (!selected) {
      setError('Select a project first')
      return
    }
    setScanning(true)
    setError('')
    setMessage('')
    setFindings([])
    try {
      const data = await apiCodeScan(selected, user.id)
      setMessage(
        `Scan complete: ${data.result.analyzed_files} files analyzed, ${data.result.findings} vulnerabilities found.`
      )
      const res = await apiCodeFindings(selected)
      setFindings(res.findings || [])
    } catch (err) {
      setError(err.message)
    } finally {
      setScanning(false)
    }
  }

  async function handleAutoRepair(finding) {
    if (!selected || repairingId) return
    setRepairingId(finding.id)
    setError('')
    try {
      const res = await apiRunCRSPipeline(selected, user.id, finding.id)
      setRepairResults((prev) => ({
        ...prev,
        [finding.id]: res.result,
      }))
    } catch (err) {
      setError(`Auto-Repair Failed: ${err.message}`)
    } finally {
      setRepairingId(null)
    }
  }

  async function handleViewFile(path) {
    if (!selected) return
    setOpenFile(path)
    setFileView(null)
    try {
      const data = await apiGetFile(selected, path)
      setFileView(data.content)
    } catch (err) {
      setError(err.message)
    }
  }

  const sorted = [...findings].sort(
    (a, b) =>
      (severityOrder[a.severity] ?? 4) - (severityOrder[b.severity] ?? 4)
  )

  const fileGroup = {}
  for (const f of sorted) {
    if (!fileGroup[f.file_path]) fileGroup[f.file_path] = []
    fileGroup[f.file_path].push(f)
  }

  const fileFindings = openFile ? fileGroup[openFile] || [] : []

  return (
    <div className="page">
      <header className="page-header">
        <h1>Code Security</h1>
        <p className="muted">
          Select a project and scan its code for vulnerabilities using AI.
          Findings are highlighted file-by-file with autonomous CRS Proof-of-Fix repair.
        </p>
      </header>

      {error && <div className="error">{error}</div>}
      {message && <div className="success">{message}</div>}

      <section className="panel">
        <h2>Step 1 — Select a project</h2>
        {projects.length === 0 ? (
          <p className="muted">
            No projects available. Add a project first in the Projects page.
          </p>
        ) : (
          <select
            className="select"
            value={selected}
            onChange={(e) => {
              setSelected(e.target.value)
              setOpenFile('')
              setFileView(null)
            }}
          >
            <option value="">-- Choose a project --</option>
            {projects.map((p) => (
              <option key={p.id} value={p.id}>
                {p.name} ({p.file_count} files)
              </option>
            ))}
          </select>
        )}
      </section>

      <section className="panel">
        <h2>Step 2 — Analyze code</h2>
        <button onClick={handleScan} disabled={scanning || !selected}>
          {scanning ? 'Analyzing code with AI...' : 'Scan for Vulnerabilities'}
        </button>
        {scanning && <p className="muted">Ollama is reviewing each file...</p>}
      </section>

      <div className="split">
        <div className="col">
          <section className="panel">
            <h2>Vulnerabilities ({findings.length})</h2>
            {Object.keys(fileGroup).length === 0 ? (
              <p className="muted">
                No findings yet. Run a scan above to analyze the code.
              </p>
            ) : (
              Object.entries(fileGroup).map(([path, items]) => (
                <div key={path} className="file-group">
                  <button
                    className="file-group-head"
                    onClick={() => handleViewFile(path)}
                  >
                    <span className="file-icon">📄</span>
                    <span>{path}</span>
                    <span className="file-group-count">{items.length}</span>
                  </button>
                  <ul className="finding-list">
                    {items.map((f) => (
                      <li key={f.id} className="finding" style={{ position: 'relative' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                          <span className={'sev-badge ' + f.severity}>
                            {f.severity}
                          </span>
                          <button
                            onClick={() => handleAutoRepair(f)}
                            disabled={repairingId === f.id}
                            style={{
                              background: repairResults[f.id] ? 'rgba(34, 197, 94, 0.2)' : 'linear-gradient(135deg, #00E5FF, #0284C7)',
                              color: repairResults[f.id] ? '#22C55E' : '#0A1628',
                              border: repairResults[f.id] ? '1px solid #22C55E' : 'none',
                              padding: '4px 10px',
                              borderRadius: '6px',
                              fontSize: '11px',
                              fontWeight: 800,
                              cursor: repairingId === f.id ? 'not-allowed' : 'pointer'
                            }}
                          >
                            {repairingId === f.id ? '⚡ Synthesizing & Verifying...' : repairResults[f.id] ? '✓ Fix Verified' : '⚡ Auto-Repair (CRS)'}
                          </button>
                        </div>
                        <div className="finding-body" style={{ marginTop: '8px' }}>
                          <div className="finding-title">{f.title}</div>
                          <div className="finding-desc">{f.description}</div>
                          {f.code_snippet && (
                            <pre className="code-view finding-code">
                              {f.code_snippet}
                            </pre>
                          )}

                          {/* Render Synthesized Patch & Proof if generated */}
                          {repairResults[f.id] && (
                            <div style={{
                              marginTop: '12px',
                              background: '#0B192C',
                              border: '1px solid #1E3A5F',
                              borderRadius: '6px',
                              padding: '12px'
                            }}>
                              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px', fontWeight: 700, color: '#22C55E', marginBottom: '6px' }}>
                                <span>🛡️ Dual-Gate Verified Patch:</span>
                                <span>CERT: {repairResults[f.id].certificate_id}</span>
                              </div>
                              <pre style={{
                                background: '#07101E',
                                color: '#A5F3FC',
                                padding: '8px',
                                borderRadius: '4px',
                                fontSize: '10px',
                                overflowX: 'auto',
                                margin: 0
                              }}>
                                {repairResults[f.id].diff_content}
                              </pre>
                              <div style={{ fontSize: '10px', color: '#94A3B8', marginTop: '6px' }}>
                                <strong>Rationale:</strong> {repairResults[f.id].rationale}
                              </div>
                            </div>
                          )}
                        </div>
                      </li>
                    ))}
                  </ul>
                </div>
              ))
            )}
          </section>
        </div>

        <div className="col">
          <section className="panel">
            <h2>
              {openFile ? `File: ${openFile}` : 'File View'}
              {openFile && fileFindings.length > 0 && (
                <span className="muted">
                  {' '}
                  — {fileFindings.length} finding(s) in this file
                </span>
              )}
            </h2>
            {!openFile ? (
              <p className="muted">
                Click a file on the left to view its code with highlighted
                vulnerable lines.
              </p>
            ) : fileView === null ? (
              <p className="muted">Loading file...</p>
            ) : (
              <div className="file-analysis">
                {fileFindings.map((f) => (
                  <div key={f.id} className="highlight-box">
                    <span className={'sev-badge ' + f.severity}>
                      {f.severity}
                    </span>
                    <strong>{f.title}</strong>
                    <pre className="code-view highlight-line">
                      {f.code_snippet}
                    </pre>
                  </div>
                ))}
                <pre className="code-view">{fileView}</pre>
              </div>
            )}
          </section>
        </div>
      </div>
    </div>
  )
}