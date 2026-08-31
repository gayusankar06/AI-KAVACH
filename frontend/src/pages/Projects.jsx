import { useCallback, useEffect, useRef, useState } from 'react'
import {
  apiCreateProject,
  apiListProjects,
  apiUploadFiles,
  apiGetFiles,
  apiGetFile,
} from '../api.js'

function readFileAsBase64(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => resolve(reader.result.split(',')[1])
    reader.onerror = reject
    reader.readAsDataURL(file)
  })
}

export default function Projects({ user }) {
  const [projects, setProjects] = useState([])
  const [selected, setSelected] = useState(null)
  const [files, setFiles] = useState([])
  const [viewing, setViewing] = useState(null)
  const [name, setName] = useState('')
  const [githubUrl, setGithubUrl] = useState('')
  const [tab, setTab] = useState('github')
  const [uploadFiles, setUploadFiles] = useState(null)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [fileLoading, setFileLoading] = useState(false)
  const fileInputRef = useRef(null)

  const loadProjects = useCallback(() => {
    apiListProjects(user.id)
      .then((data) => {
        setProjects(data.projects || [])
        setSelected((cur) => {
          if (!cur) return null
          const updated = (data.projects || []).find((p) => p.id === cur.id)
          return updated || null
        })
      })
      .catch((err) => setError(err.message))
  }, [user.id])

  useEffect(() => {
    loadProjects()
  }, [loadProjects])

  useEffect(() => {
    if (!selected) {
      setFiles([])
      return
    }
    setFileLoading(true)
    setFiles([])
    apiGetFiles(selected.id)
      .then((data) => setFiles(data.files || []))
      .catch((err) => setError(err.message))
      .finally(() => setFileLoading(false))
  }, [selected])

  async function handleCreateGithub(e) {
    e.preventDefault()
    setError('')
    setMessage('')
    setLoading(true)
    try {
      await apiCreateProject({
        user_id: user.id,
        name: name || githubUrl.split('/').filter(Boolean).pop() || 'github-project',
        source_type: 'github',
        source_url: githubUrl,
      })
      setMessage('Repository cloned successfully')
      setName('')
      setGithubUrl('')
      loadProjects()
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  async function handleCreateFolder() {
    if (!name.trim()) {
      setError('Enter a project name')
      return
    }
    if (!uploadFiles || uploadFiles.length === 0) {
      setError('Select a folder to upload')
      return
    }
    setError('')
    setMessage('')
    setLoading(true)
    try {
      const data = await apiCreateProject({
        user_id: user.id,
        name: name,
        source_type: 'folder',
        source_url: '',
      })
      const items = []
      for (const file of uploadFiles) {
        const relPath = file.webkitRelativePath || file.name
        const content = await readFileAsBase64(file)
        items.push({ path: relPath, content })
      }
      await apiUploadFiles(data.project_id, items)
      setMessage(`Uploaded ${items.length} files from folder`)
      setName('')
      setUploadFiles(null)
      if (fileInputRef.current) fileInputRef.current.value = ''
      loadProjects()
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  async function handleViewFile(path) {
    if (!selected) return
    try {
      const data = await apiGetFile(selected.id, path)
      setViewing(data)
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <div className="page">
      <header className="page-header">
        <h1>Projects</h1>
        <p className="muted">
          Add a GitHub repository or upload a folder to store all files locally.
        </p>
      </header>

      {error && <div className="error">{error}</div>}
      {message && <div className="success">{message}</div>}

      <div className="split">
        <div className="col">
          <section className="panel">
            <div className="tabs">
              <button
                className={'tab' + (tab === 'github' ? ' active' : '')}
                onClick={() => setTab('github')}
              >
                GitHub URL
              </button>
              <button
                className={'tab' + (tab === 'folder' ? ' active' : '')}
                onClick={() => setTab('folder')}
              >
                Upload Folder
              </button>
            </div>

            {tab === 'github' ? (
              <form onSubmit={handleCreateGithub}>
                <label>
                  Project name
                  <input
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="my-project"
                  />
                </label>
                <label>
                  GitHub repository URL
                  <input
                    value={githubUrl}
                    onChange={(e) => setGithubUrl(e.target.value)}
                    placeholder="https://github.com/user/repo"
                    required
                  />
                </label>
                <button type="submit" disabled={loading}>
                  {loading ? 'Cloning...' : 'Clone & Store Locally'}
                </button>
              </form>
            ) : (
              <div>
                <label>
                  Project name
                  <input
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="my-project"
                  />
                </label>
                <label>
                  Select folder
                  <input
                    ref={fileInputRef}
                    type="file"
                    webkitdirectory=""
                    directory=""
                    onChange={(e) => setUploadFiles(e.target.files)}
                  />
                </label>
                {uploadFiles && (
                  <p className="muted">{uploadFiles.length} files selected</p>
                )}
                <button onClick={handleCreateFolder} disabled={loading}>
                  {loading ? 'Uploading...' : 'Upload & Store Locally'}
                </button>
              </div>
            )}
          </section>

          <section className="panel">
            <h2>Your Projects ({projects.length})</h2>
            {projects.length === 0 ? (
              <p className="muted">No projects added yet.</p>
            ) : (
              <ul className="project-list">
                {projects.map((p) => (
                  <li
                    key={p.id}
                    className={'project-item' + (selected?.id === p.id ? ' selected' : '')}
                    onClick={() => setSelected(p)}
                  >
                    <div className="project-row">
                      <div>
                        <div className="project-name">{p.name}</div>
                        <div className="project-meta">
                          {p.source_type} · {p.file_count} files
                        </div>
                      </div>
                      <span className="chevron">›</span>
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </section>
        </div>

        <div className="col">
          <section className="panel">
            <h2>{selected ? `${selected.name} — Files` : 'Files'}</h2>
            {!selected ? (
              <p className="muted">Select a project to see its stored files.</p>
            ) : fileLoading ? (
              <p className="muted">Loading files...</p>
            ) : files.length === 0 ? (
              <p className="muted">No files stored in this project.</p>
            ) : (
              <ul className="file-list">
                {files.map((f) => (
                  <li key={f.path}>
                    <button
                      className="file-item"
                      onClick={() => handleViewFile(f.path)}
                    >
                      <span className="file-icon">📄</span>
                      <span>{f.path}</span>
                      <span className="file-size">{(f.size / 1024).toFixed(1)} KB</span>
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </section>

          {viewing && (
            <section className="panel">
              <div className="panel-head">
                <h2>{viewing.path}</h2>
                <button className="small-btn" onClick={() => setViewing(null)}>
                  Close
                </button>
              </div>
              <pre className="code-view">{viewing.content}</pre>
            </section>
          )}
        </div>
      </div>
    </div>
  )
}