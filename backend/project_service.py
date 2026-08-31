import base64
import os
import re
import shutil
import subprocess
from pathlib import Path

STORAGE_ROOT = Path(__file__).resolve().parent / "project_storage"


def _safe_name(name):
    name = re.sub(r"[^A-Za-z0-9_.-]", "_", name.strip())
    return name or "project"


def user_dir(user_id):
    d = STORAGE_ROOT / str(user_id)
    d.mkdir(parents=True, exist_ok=True)
    return d


def project_dir(user_id, name):
    return user_dir(user_id) / _safe_name(name)


def clone_github(user_id, name, url):
    dest = project_dir(user_id, name)
    if dest.exists():
        shutil.rmtree(dest, ignore_errors=True)
    dest.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        ["git", "clone", "--depth", "1", url, str(dest)],
        capture_output=True,
        text=True,
        timeout=180,
    )
    if result.returncode != 0:
        shutil.rmtree(dest, ignore_errors=True)
        raise ValueError(result.stderr.strip() or "Git clone failed")
    git_dir = dest / ".git"
    if git_dir.exists():
        shutil.rmtree(git_dir, ignore_errors=True)
    return str(dest)


def save_uploaded_files(storage_path, files):
    root = Path(storage_path)
    root.mkdir(parents=True, exist_ok=True)
    for item in files:
        rel = item.get("path", "")
        content = item.get("content", "")
        if not rel or rel == ".":
            continue
        target = root / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(base64.b64decode(content))
    return str(root)


def list_files(storage_path, prefix=""):
    if not storage_path:
        return []
    root = Path(storage_path)
    if not root.exists():
        return []
    results = []
    for path in sorted(root.rglob("*")):
        if path.is_file():
            rel = path.relative_to(root).as_posix()
            if ".git/" in rel or rel.startswith(".git"):
                continue
            if prefix and not rel.startswith(prefix):
                continue
            results.append(
                {
                    "path": rel,
                    "size": path.stat().st_size,
                    "extension": path.suffix.lstrip("."),
                }
            )
    return results


def read_file(storage_path, rel_path):
    root = Path(storage_path)
    target = (root / rel_path).resolve()
    root_resolved = root.resolve()
    if not str(target).startswith(str(root_resolved)):
        raise ValueError("Invalid path")
    if not target.is_file():
        raise ValueError("File not found")
    return target


def scaffold_pentest(project):
    out_root = Path(project["storage_path"]) / "pentest_app"
    if out_root.exists():
        shutil.rmtree(out_root, ignore_errors=True)

    backend = out_root / "backend"
    frontend = out_root / "frontend"
    backend.mkdir(parents=True, exist_ok=True)
    frontend.mkdir(parents=True, exist_ok=True)

    proj_name = _safe_name(project["name"])
    file_list = list_files(project["storage_path"])
    file_paths = [f["path"] for f in file_list if f["size"] < 500 * 1024]

    (backend / "requirements.txt").write_text(
        "fastapi\nuvicorn\n", encoding="utf-8"
    )
    (backend / "database.py").write_text(
        f'''import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "{proj_name}.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS scan_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_path TEXT NOT NULL,
            severity TEXT NOT NULL,
            finding TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()
    conn.close()


def add_result(file_path, severity, finding):
    conn = get_connection()
    conn.execute(
        "INSERT INTO scan_results (file_path, severity, finding) VALUES (?, ?, ?)",
        (file_path, severity, finding),
    )
    conn.commit()
    conn.close()


def get_results():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM scan_results ORDER BY id DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]
''',
        encoding="utf-8",
    )
    (backend / "main.py").write_text(
        f'''from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import init_db, add_result, get_results

FILES = {file_paths!r}


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="{proj_name} Pentest API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5174", "http://127.0.0.1:5174"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {{"message": "{proj_name} pentest API is running"}}


@app.get("/api/files")
def files():
    return {{"total": len(FILES), "files": FILES}}


@app.post("/api/scan")
def scan():
    findings = 0
    for fp in FILES:
        add_result(fp, "low", "File inspected: " + fp)
        findings += 1
    return {{"scanned": findings}}


@app.get("/api/results")
def results():
    return {{"results": get_results()}}
''',
        encoding="utf-8",
    )

    (frontend / "package.json").write_text(
        f"""{{
  "name": "{proj_name}-pentest-frontend",
  "private": true,
  "version": "1.0.0",
  "type": "module",
  "scripts": {{
    "dev": "vite --port 5174",
    "build": "vite build",
    "preview": "vite preview"
  }},
  "dependencies": {{
    "react": "^18.3.1",
    "react-dom": "^18.3.1"
  }},
  "devDependencies": {{
    "@vitejs/plugin-react": "^4.3.4",
    "vite": "^5.4.11"
  }}
}}
""",
        encoding="utf-8",
    )
    (frontend / "vite.config.js").write_text(
        """import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: { port: 5174 },
})
""",
        encoding="utf-8",
    )
    (frontend / "index.html").write_text(
        f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{proj_name} Pentest</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>
""",
        encoding="utf-8",
    )
    (frontend / "src").mkdir(exist_ok=True)
    (frontend / "src" / "main.jsx").write_text(
        """import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
)
""",
        encoding="utf-8",
    )
    (frontend / "src" / "App.jsx").write_text(
        f"""import {{ useEffect, useState }} from 'react'

const API = 'http://localhost:8001'

export default function App() {{
  const [files, setFiles] = useState([])
  const [results, setResults] = useState([])
  const [scanning, setScanning] = useState(false)
  const [message, setMessage] = useState('')

  async function loadFiles() {{
    const res = await fetch(API + '/api/files')
    const data = await res.json()
    setFiles(data.files || [])
  }}

  async function loadResults() {{
    const res = await fetch(API + '/api/results')
    const data = await res.json()
    setResults(data.results || [])
  }}

  useEffect(() => {{
    loadFiles()
    loadResults()
  }}, [])

  async function runScan() {{
    setScanning(true)
    setMessage('')
    try {{
      const res = await fetch(API + '/api/scan', {{ method: 'POST' }})
      const data = await res.json()
      setMessage(`Scan complete: ${{data.scanned}} files inspected`)
      loadResults()
    }} catch (err) {{
      setMessage('Scan failed: ' + err.message)
    }} finally {{
      setScanning(false)
    }}
  }}

  return (
    <div className="container">
      <h1>{proj_name} Pentest</h1>
      <p className="muted">Generated frontend + backend with SQLite database.</p>
      <button onClick={{runScan}} disabled={{scanning}}>
        {{scanning ? 'Scanning...' : 'Run Scan'}}
      </button>
      {{message && <div className="message">{{message}}</div>}}
      <section>
        <h2>Project Files ({{files.length}})</h2>
        <ul>
          {{files.map((f, i) => <li key={{i}}>{{f}}</li>)}}
        </ul>
      </section>
      <section>
        <h2>Scan Results ({{results.length}})</h2>
        <ul>
          {{results.map((r, i) => <li key={{i}}>[{{r.severity}}] {{r.file_path}} — {{r.finding}}</li>)}}
        </ul>
      </section>
    </div>
  )
}}
""",
        encoding="utf-8",
    )
    (frontend / "src" / "index.css").write_text(
        """* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: 'Segoe UI', system-ui, sans-serif; background: #0f172a; color: #e2e8f0; min-height: 100vh; }
.container { max-width: 860px; margin: 0 auto; padding: 2rem; }
h1 { background: linear-gradient(90deg, #60a5fa, #818cf8); -webkit-background-clip: text; background-clip: text; color: transparent; margin-bottom: 0.5rem; }
.muted { color: #94a3b8; margin-bottom: 1.5rem; }
button { padding: 0.7rem 1.4rem; border: none; border-radius: 8px; background: linear-gradient(90deg, #3b82f6, #6366f1); color: #fff; font-weight: 600; cursor: pointer; margin-bottom: 1rem; }
button:disabled { opacity: 0.6; cursor: not-allowed; }
.message { background: rgba(34, 197, 94, 0.15); border: 1px solid #22c55e; color: #86efac; border-radius: 8px; padding: 0.6rem 0.9rem; margin-bottom: 1rem; }
section { background: #1e293b; border: 1px solid #334155; border-radius: 10px; padding: 1.2rem; margin-bottom: 1.2rem; }
section h2 { font-size: 1rem; color: #93c5fd; margin-bottom: 0.75rem; }
ul { list-style: none; }
li { padding: 0.35rem 0; border-bottom: 1px solid #334155; font-size: 0.9rem; word-break: break-all; }
""",
        encoding="utf-8",
    )

    return str(out_root)