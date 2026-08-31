import { useCallback, useEffect, useRef, useState } from 'react'
import {
  apiNetworkStart,
  apiNetworkStop,
  apiNetworkSessions,
  apiNetworkPackets,
  networkReportUrl,
} from '../api.js'

export default function NetworkLens({ user }) {
  const [sessions, setSessions] = useState([])
  const [activeCount, setActiveCount] = useState(0)
  const [selected, setSelected] = useState('')
  const [packets, setPackets] = useState([])
  const [sessionInfo, setSessionInfo] = useState(null)
  const [interfaceName, setInterfaceName] = useState('all')
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')
  const [starting, setStarting] = useState(false)
  const pollRef = useRef(null)

  const loadSessions = useCallback(() => {
    apiNetworkSessions(user.id)
      .then((data) => {
        setSessions(data.sessions || [])
        setActiveCount(data.active || 0)
      })
      .catch((err) => setError(err.message))
  }, [user.id])

  useEffect(() => {
    loadSessions()
  }, [loadSessions])

  useEffect(() => {
    if (!selected) return
    const loadPackets = () => {
      apiNetworkPackets(selected)
        .then((data) => {
          setPackets(data.packets || [])
          setSessionInfo(data.session)
        })
        .catch(() => {})
    }
    loadPackets()
    pollRef.current = setInterval(loadPackets, 2000)
    return () => clearInterval(pollRef.current)
  }, [selected])

  async function handleStart() {
    setError('')
    setMessage('')
    setStarting(true)
    try {
      const data = await apiNetworkStart(user.id, interfaceName)
      setMessage('Capture started. Generating live traffic...')
      setSelected(String(data.session_id))
      loadSessions()
    } catch (err) {
      setError(err.message)
    } finally {
      setStarting(false)
    }
  }

  async function handleStop() {
    if (!selected) return
    setError('')
    try {
      const data = await apiNetworkStop(Number(selected))
      setMessage(
        `Capture stopped. ${data.packet_count} packets captured. Download the PDF report below.`
      )
      loadSessions()
      const pkts = await apiNetworkPackets(selected)
      setPackets(pkts.packets || [])
      setSessionInfo(pkts.session)
    } catch (err) {
      setError(err.message)
    }
  }

  const selectedSession = sessions.find((s) => String(s.id) === selected)
  const isRunning = selectedSession?.status === 'running' || activeCount > 0

  return (
    <div className="page">
      <header className="page-header">
        <h1>Netrix</h1>
        <p className="muted">
          Wireshark-style packet capture. Start a capture, analyse the traffic,
          then export a PDF report.
        </p>
      </header>

      {error && <div className="error">{error}</div>}
      {message && <div className="success">{message}</div>}

      <section className="panel">
        <h2>Live Capture</h2>
        <div className="capture-controls">
          <label className="capture-iface">
            Interface
            <input
              value={interfaceName}
              onChange={(e) => setInterfaceName(e.target.value)}
              placeholder="all"
            />
          </label>
          {!isRunning ? (
            <button className="capture-btn start" onClick={handleStart} disabled={starting}>
              {starting ? 'Starting...' : '▶ Start Capture'}
            </button>
          ) : (
            <button className="capture-btn stop" onClick={handleStop}>
              ■ Stop Capture
            </button>
          )}
        </div>
        <p className="muted">
          {isRunning
            ? 'Capture is running — new connections are being logged every second.'
            : 'No capture running. Click Start Capture to begin.'}
        </p>
      </section>

      <section className="panel">
        <h2>Capture Sessions</h2>
        {sessions.length === 0 ? (
          <p className="muted">No capture sessions yet.</p>
        ) : (
          <ul className="project-list">
            {sessions.map((s) => (
              <li
                key={s.id}
                className={
                  'project-item' + (String(s.id) === selected ? ' selected' : '')
                }
                onClick={() => setSelected(String(s.id))}
              >
                <div className="project-row">
                  <div>
                    <div className="project-name">
                      Session #{s.id}{' '}
                      <span className={'badge ' + (s.status === 'running' ? 'running' : 'stopped')}>
                        {s.status}
                      </span>
                    </div>
                    <div className="project-meta">
                      {s.interface} · {s.packet_count} packets · started{' '}
                      {new Date(s.started_at).toLocaleString()}
                    </div>
                  </div>
                  <span className="chevron">›</span>
                </div>
              </li>
            ))}
          </ul>
        )}
      </section>

      {selected && (
        <section className="panel">
          <div className="panel-head">
            <h2>
              Packets — Session #{selected}
              {sessionInfo?.status === 'stopped' && (
                <span className="badge stopped">stopped</span>
              )}
            </h2>
            {sessionInfo?.status === 'stopped' && (
              <a
                className="download-btn"
                href={networkReportUrl(Number(selected))}
              >
                ⬇ Download PDF Report
              </a>
            )}
          </div>
          {packets.length === 0 ? (
            <p className="muted">
              No packets captured yet. Start the capture to see live traffic.
            </p>
          ) : (
            <div className="table-scroll">
              <table className="table packet-table">
                <thead>
                  <tr>
                    <th>#</th>
                    <th>Time</th>
                    <th>Source</th>
                    <th>Dest</th>
                    <th>Proto</th>
                    <th>Process</th>
                    <th>Info</th>
                  </tr>
                </thead>
                <tbody>
                  {packets.map((p, i) => (
                    <tr key={p.id}>
                      <td className="num">{i + 1}</td>
                      <td>{p.timestamp}</td>
                      <td>
                        {p.src}
                        {p.sport ? `:${p.sport}` : ''}
                      </td>
                      <td>
                        {p.dst}
                        {p.dport ? `:${p.dport}` : ''}
                      </td>
                      <td>
                        <span className={'proto ' + (p.protocol || '').toLowerCase()}>
                          {p.protocol}
                        </span>
                      </td>
                      <td>{p.process}</td>
                      <td className="info-cell">{p.info}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
      )}
    </div>
  )
}