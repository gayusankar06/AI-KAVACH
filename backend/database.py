import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "users.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            source_type TEXT NOT NULL,
            source_url TEXT,
            storage_path TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS pentest_scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            status TEXT DEFAULT 'created',
            result_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id)
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS capture_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            interface TEXT,
            status TEXT DEFAULT 'running',
            packet_count INTEGER DEFAULT 0,
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            stopped_at TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS packets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL,
            timestamp TEXT NOT NULL,
            src TEXT,
            dst TEXT,
            sport INTEGER,
            dport INTEGER,
            protocol TEXT,
            size INTEGER,
            state TEXT,
            process TEXT,
            info TEXT,
            FOREIGN KEY (session_id) REFERENCES capture_sessions(id)
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS pentest_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            tool TEXT NOT NULL,
            summary TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id)
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS code_security_findings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            file_path TEXT NOT NULL,
            severity TEXT,
            title TEXT,
            description TEXT,
            code_snippet TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id)
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS crs_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            status TEXT DEFAULT 'pending',
            target_file TEXT,
            vulnerability_type TEXT,
            cwe_id TEXT,
            stage TEXT DEFAULT 'initiated',
            fuzz_crash_trace TEXT,
            reachability_path TEXT,
            remediation_plan TEXT,
            iterations INTEGER DEFAULT 0,
            proof_status TEXT DEFAULT 'unverified',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id)
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS crs_patches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id INTEGER NOT NULL,
            project_id INTEGER NOT NULL,
            file_path TEXT NOT NULL,
            original_code TEXT,
            patched_code TEXT,
            diff_content TEXT,
            rationale TEXT,
            iteration INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (run_id) REFERENCES crs_runs(id)
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS crs_proof_certificates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            certificate_id TEXT NOT NULL UNIQUE,
            run_id INTEGER NOT NULL,
            project_id INTEGER NOT NULL,
            patch_id INTEGER,
            status TEXT NOT NULL,
            gate1_mitigation_verified INTEGER DEFAULT 0,
            gate2_regression_verified INTEGER DEFAULT 0,
            sha256_signature TEXT NOT NULL,
            telemetry_json TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (run_id) REFERENCES crs_runs(id)
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS agent_mesh_tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            agent_id TEXT NOT NULL,
            agent_name TEXT NOT NULL,
            status TEXT DEFAULT 'completed',
            query TEXT,
            output TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id)
        )
        """
    )
    conn.commit()
    conn.close()


def create_user(username, email, password_hash):
    conn = get_connection()
    try:
        cursor = conn.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
            (username, email, password_hash),
        )
        conn.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()


def get_user_by_username(username):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM users WHERE username = ? OR email = ?", (username, username)
    ).fetchone()
    conn.close()
    return row


def get_user_by_id(user_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return row


def create_project(user_id, name, source_type, source_url, storage_path):
    conn = get_connection()
    cursor = conn.execute(
        "INSERT INTO projects (user_id, name, source_type, source_url, storage_path) VALUES (?, ?, ?, ?, ?)",
        (user_id, name, source_type, source_url, storage_path),
    )
    conn.commit()
    project_id = cursor.lastrowid
    conn.close()
    return project_id


def get_projects_by_user(user_id):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM projects WHERE user_id = ? ORDER BY created_at DESC",
        (user_id,),
    ).fetchall()
    conn.close()
    return rows


def get_project(project_id):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM projects WHERE id = ?", (project_id,)
    ).fetchone()
    conn.close()
    return row


def create_scan(project_id, user_id, result_path):
    conn = get_connection()
    cursor = conn.execute(
        "INSERT INTO pentest_scans (project_id, user_id, result_path) VALUES (?, ?, ?)",
        (project_id, user_id, result_path),
    )
    conn.commit()
    scan_id = cursor.lastrowid
    conn.close()
    return scan_id


def update_scan_status(scan_id, status):
    conn = get_connection()
    conn.execute(
        "UPDATE pentest_scans SET status = ? WHERE id = ?", (status, scan_id)
    )
    conn.commit()
    conn.close()


def get_scans_by_project(project_id):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM pentest_scans WHERE project_id = ? ORDER BY created_at DESC",
        (project_id,),
    ).fetchall()
    conn.close()
    return rows


def create_capture_session(user_id, interface):
    conn = get_connection()
    cursor = conn.execute(
        "INSERT INTO capture_sessions (user_id, interface) VALUES (?, ?)",
        (user_id, interface),
    )
    conn.commit()
    session_id = cursor.lastrowid
    conn.close()
    return session_id


def get_capture_session(session_id):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM capture_sessions WHERE id = ?", (session_id,)
    ).fetchone()
    conn.close()
    return row


def get_capture_sessions_by_user(user_id):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM capture_sessions WHERE user_id = ? ORDER BY started_at DESC",
        (user_id,),
    ).fetchall()
    conn.close()
    return rows


def update_capture_session(session_id, status, packet_count, stopped_at):
    conn = get_connection()
    conn.execute(
        "UPDATE capture_sessions SET status = ?, packet_count = ?, stopped_at = ? WHERE id = ?",
        (status, packet_count, stopped_at, session_id),
    )
    conn.commit()
    conn.close()


def add_packet(session_id, ts, src, dst, sport, dport, protocol, size, state, process, info):
    conn = get_connection()
    conn.execute(
        "INSERT INTO packets (session_id, timestamp, src, dst, sport, dport, protocol, size, state, process, info) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (session_id, ts, src, dst, sport, dport, protocol, size, state, process, info),
    )
    conn.commit()
    conn.close()


def get_packets_by_session(session_id, limit=500):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM packets WHERE session_id = ? ORDER BY id DESC LIMIT ?",
        (session_id, limit),
    ).fetchall()
    conn.close()
    return rows


def get_packets_all(session_id):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM packets WHERE session_id = ? ORDER BY id", (session_id,)
    ).fetchall()
    conn.close()
    return rows


def count_packets_by_session(session_id):
    conn = get_connection()
    row = conn.execute(
        "SELECT COUNT(*) AS c FROM packets WHERE session_id = ?", (session_id,)
    ).fetchone()
    conn.close()
    return row["c"]


def add_chat_message(user_id, role, content):
    conn = get_connection()
    conn.execute(
        "INSERT INTO chat_messages (user_id, role, content) VALUES (?, ?, ?)",
        (user_id, role, content),
    )
    conn.commit()
    conn.close()


def get_chat_history(user_id, limit=100):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM chat_messages WHERE user_id = ? ORDER BY id DESC LIMIT ?",
        (user_id, limit),
    ).fetchall()
    conn.close()
    return rows


def get_netrix_graph_data(user_id):
    conn = get_connection()
    sessions = conn.execute(
        "SELECT id, interface, status, packet_count, started_at, stopped_at "
        "FROM capture_sessions WHERE user_id = ? ORDER BY started_at ASC",
        (user_id,),
    ).fetchall()
    session_ids = [s["id"] for s in sessions]
    protocol_rows = []
    if session_ids:
        placeholders = ",".join("?" * len(session_ids))
        protocol_rows = conn.execute(
            f"SELECT session_id, protocol, COUNT(*) AS count FROM packets "
            f"WHERE session_id IN ({placeholders}) GROUP BY session_id, protocol",
            session_ids,
        ).fetchall()
    conn.close()
    by_session = {}
    for pr in protocol_rows:
        by_session.setdefault(pr["session_id"], {})[pr["protocol"] or "unknown"] = pr["count"]
    return [
        {
            "id": s["id"],
            "interface": s["interface"] or "unknown",
            "status": s["status"],
            "packet_count": s["packet_count"],
            "started_at": s["started_at"],
            "stopped_at": s["stopped_at"],
            "protocols": by_session.get(s["id"], {}),
        }
        for s in sessions
    ]


def get_chat_usage_graph_data(user_id):
    conn = get_connection()
    rows = conn.execute(
        "SELECT DATE(created_at) AS day, role, COUNT(*) AS count "
        "FROM chat_messages WHERE user_id = ? GROUP BY day, role ORDER BY day",
        (user_id,),
    ).fetchall()
    conn.close()
    daily = {}
    for r in rows:
        daily.setdefault(r["day"], {"user": 0, "assistant": 0})[r["role"]] = r["count"]
    return [
        {"day": day, "user": v["user"], "assistant": v["assistant"]}
        for day, v in sorted(daily.items())
    ]

def add_pentest_result(project_id, user_id, tool, summary):
    conn = get_connection()
    cursor = conn.execute(
        "INSERT INTO pentest_results (project_id, user_id, tool, summary) VALUES (?, ?, ?, ?)",
        (project_id, user_id, tool, summary),
    )
    conn.commit()
    result_id = cursor.lastrowid
    conn.close()
    return result_id


def get_pentest_results(project_id):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM pentest_results WHERE project_id = ? ORDER BY id DESC",
        (project_id,),
    ).fetchall()
    conn.close()
    return rows


def clear_code_findings(project_id):
    conn = get_connection()
    conn.execute("DELETE FROM code_security_findings WHERE project_id = ?", (project_id,))
    conn.commit()
    conn.close()


def add_code_finding(project_id, user_id, file_path, severity, title, description, code_snippet):
    conn = get_connection()
    conn.execute(
        "INSERT INTO code_security_findings (project_id, user_id, file_path, severity, title, description, code_snippet) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (project_id, user_id, file_path, severity, title, description, code_snippet),
    )
    conn.commit()
    conn.close()


def get_code_findings(project_id):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM code_security_findings WHERE project_id = ? ORDER BY created_at DESC, id DESC",
        (project_id,),
    ).fetchall()
    conn.close()
    return rows


def get_code_finding_by_id(finding_id):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM code_security_findings WHERE id = ?", (finding_id,)
    ).fetchone()
    conn.close()
    return row


def create_crs_run(project_id, user_id, target_file, vulnerability_type, cwe_id="CWE-Unknown"):
    conn = get_connection()
    cursor = conn.execute(
        """
        INSERT INTO crs_runs (project_id, user_id, status, target_file, vulnerability_type, cwe_id, stage)
        VALUES (?, ?, 'running', ?, ?, ?, 'discovery')
        """,
        (project_id, user_id, target_file, vulnerability_type, cwe_id),
    )
    conn.commit()
    run_id = cursor.lastrowid
    conn.close()
    return run_id


def update_crs_run(run_id, **kwargs):
    conn = get_connection()
    fields = []
    values = []
    for k, v in kwargs.items():
        fields.append(f"{k} = ?")
        values.append(v)
    fields.append("updated_at = CURRENT_TIMESTAMP")
    values.append(run_id)
    query = f"UPDATE crs_runs SET {', '.join(fields)} WHERE id = ?"
    conn.execute(query, tuple(values))
    conn.commit()
    conn.close()


def get_crs_run(run_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM crs_runs WHERE id = ?", (run_id,)).fetchone()
    conn.close()
    return row


def get_crs_runs_by_project(project_id):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM crs_runs WHERE project_id = ? ORDER BY id DESC",
        (project_id,),
    ).fetchall()
    conn.close()
    return rows


def add_crs_patch(run_id, project_id, file_path, original_code, patched_code, diff_content, rationale, iteration=1):
    conn = get_connection()
    cursor = conn.execute(
        """
        INSERT INTO crs_patches (run_id, project_id, file_path, original_code, patched_code, diff_content, rationale, iteration)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (run_id, project_id, file_path, original_code, patched_code, diff_content, rationale, iteration),
    )
    conn.commit()
    patch_id = cursor.lastrowid
    conn.close()
    return patch_id


def get_crs_patches(run_id):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM crs_patches WHERE run_id = ? ORDER BY iteration ASC",
        (run_id,),
    ).fetchall()
    conn.close()
    return rows


def add_crs_proof_certificate(certificate_id, run_id, project_id, patch_id, status, gate1, gate2, sha256_sig, telemetry_json):
    conn = get_connection()
    cursor = conn.execute(
        """
        INSERT INTO crs_proof_certificates (
            certificate_id, run_id, project_id, patch_id, status,
            gate1_mitigation_verified, gate2_regression_verified,
            sha256_signature, telemetry_json
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (certificate_id, run_id, project_id, patch_id, status, gate1, gate2, sha256_sig, telemetry_json),
    )
    conn.commit()
    cert_pk = cursor.lastrowid
    conn.close()
    return cert_pk


def get_crs_certificates_by_project(project_id):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM crs_proof_certificates WHERE project_id = ? ORDER BY id DESC",
        (project_id,),
    ).fetchall()
    conn.close()
    return rows


def get_crs_certificate_by_id(certificate_id):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM crs_proof_certificates WHERE certificate_id = ?",
        (certificate_id,),
    ).fetchone()
    conn.close()
    return row


def add_agent_mesh_task(project_id, user_id, agent_id, agent_name, query, output, status="completed"):
    conn = get_connection()
    cursor = conn.execute(
        """
        INSERT INTO agent_mesh_tasks (project_id, user_id, agent_id, agent_name, query, output, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (project_id, user_id, agent_id, agent_name, query, output, status),
    )
    conn.commit()
    task_id = cursor.lastrowid
    conn.close()
    return task_id


def get_agent_mesh_tasks(project_id):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM agent_mesh_tasks WHERE project_id = ? ORDER BY id DESC LIMIT 50",
        (project_id,),
    ).fetchall()
    conn.close()
    return rows