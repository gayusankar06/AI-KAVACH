import json
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel, EmailStr, Field

from database import (
    init_db,
    create_user,
    get_user_by_username,
    get_user_by_id,
    create_project,
    get_projects_by_user,
    get_project,
    create_scan,
    update_scan_status,
    get_scans_by_project,
    get_capture_session,
    get_capture_sessions_by_user,
    get_packets_by_session,
    add_chat_message,
    get_chat_history,
    add_pentest_result,
    get_pentest_results,
    get_code_findings,
    get_netrix_graph_data,
    get_chat_usage_graph_data,
)
from security import hash_password, verify_password
from project_service import (
    clone_github,
    save_uploaded_files,
    list_files,
    read_file,
    scaffold_pentest,
    project_dir,
)
from capture_service import (
    start_capture,
    stop_capture,
    generate_pdf,
    active_capture_count,
)
from ai_service import TOOLS, mcp_status, mcp_connect, run_tool, run_tool_url
from hexstrike_manager import ensure_hexstrike_server, stop_hexstrike_server
from metasploit_manager import ensure_metasploit_server, stop_metasploit_server
from suricata_manager import ensure_suricata_server, stop_suricata_server
from zeek_manager import ensure_zeek_server, stop_zeek_server
from report_service import collect_report_data, generate_report_pdf
from code_security_service import scan_project, _ollama_available


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    ensure_hexstrike_server()
    ensure_metasploit_server()
    ensure_suricata_server()
    ensure_zeek_server()
    yield
    stop_hexstrike_server()
    stop_metasploit_server()
    stop_suricata_server()
    stop_zeek_server()


app = FastAPI(title="CyberLens Auth API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SignupRequest(BaseModel):
    username: str = Field(min_length=3, max_length=30)
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)


class LoginRequest(BaseModel):
    username: str
    password: str


@app.get("/")
def root():
    return {"message": "CyberLens Auth API is running"}


@app.post("/api/signup")
def signup(data: SignupRequest):
    user = get_user_by_username(data.username)
    if user is not None and user["username"] == data.username:
        raise HTTPException(status_code=400, detail="Username already exists")

    user_by_email = get_user_by_username(data.email)
    if user_by_email is not None and user_by_email["email"] == data.email:
        raise HTTPException(status_code=400, detail="Email already registered")

    password_hash = hash_password(data.password)
    user_id = create_user(data.username, data.email, password_hash)
    if user_id is None:
        raise HTTPException(status_code=400, detail="Could not create user")

    return {"message": "Account created successfully", "user_id": user_id}


@app.post("/api/login")
def login(data: LoginRequest):
    user = get_user_by_username(data.username)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    if not verify_password(data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    return {
        "message": "Login successful",
        "user": {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
        },
    }


def _require_user(user_id: int):
    user = get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


class CreateProjectRequest(BaseModel):
    user_id: int
    name: str = Field(min_length=1, max_length=100)
    source_type: str
    source_url: str = ""


@app.post("/api/projects")
def create_project_endpoint(data: CreateProjectRequest):
    _require_user(data.user_id)
    if data.source_type not in ("github", "folder"):
        raise HTTPException(status_code=400, detail="Invalid source type")
    try:
        if data.source_type == "github":
            if not data.source_url:
                raise HTTPException(status_code=400, detail="GitHub URL is required")
            storage_path = clone_github(data.user_id, data.name, data.source_url)
        else:
            storage_path = str(project_dir(data.user_id, data.name))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    project_id = create_project(
        data.user_id, data.name, data.source_type, data.source_url, storage_path
    )
    return {"message": "Project created", "project_id": project_id}


@app.get("/api/projects")
def list_projects(user_id: int):
    _require_user(user_id)
    projects = get_projects_by_user(user_id)
    result = []
    for p in projects:
        item = dict(p)
        try:
            item["file_count"] = len(list_files(p["storage_path"]))
        except Exception:
            item["file_count"] = 0
        result.append(item)
    return {"projects": result}


class UploadFilesRequest(BaseModel):
    files: list = []


@app.post("/api/projects/{project_id}/files")
def upload_files(project_id: int, data: UploadFilesRequest):
    project = get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    try:
        save_uploaded_files(project["storage_path"], data.files)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {"message": "Files uploaded", "count": len(data.files)}


@app.get("/api/projects/{project_id}/files")
def get_project_files(project_id: int):
    project = get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"files": list_files(project["storage_path"])}


@app.get("/api/projects/{project_id}/file")
def get_project_file(project_id: int, path: str):
    project = get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    try:
        target = read_file(project["storage_path"], path)
        return {
            "path": path,
            "content": target.read_text(encoding="utf-8", errors="replace"),
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


class ScaffoldRequest(BaseModel):
    user_id: int


@app.post("/api/projects/{project_id}/scaffold")
def scaffold_project(project_id: int, data: ScaffoldRequest):
    _require_user(data.user_id)
    project = get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    try:
        result_path = scaffold_pentest(project)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    scan_id = create_scan(project_id, data.user_id, result_path)
    return {"message": "Scaffold created", "scan_id": scan_id, "path": result_path}


@app.get("/api/projects/{project_id}/scans")
def get_scans(project_id: int):
    project = get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"scans": [dict(s) for s in get_scans_by_project(project_id)]}


class StartCaptureRequest(BaseModel):
    user_id: int
    interface: str = "all"


@app.post("/api/network/start")
def start_capture_endpoint(data: StartCaptureRequest):
    _require_user(data.user_id)
    if active_capture_count() > 0:
        raise HTTPException(status_code=400, detail="A capture is already running")
    try:
        session_id = start_capture(data.user_id, data.interface)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    return {"message": "Capture started", "session_id": session_id}


@app.post("/api/network/stop")
def stop_capture_endpoint(session_id: int):
    try:
        session = stop_capture(session_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return {
        "message": "Capture stopped",
        "session": dict(session),
        "packet_count": session["packet_count"],
    }


@app.get("/api/network/sessions")
def list_capture_sessions(user_id: int):
    _require_user(user_id)
    sessions = get_capture_sessions_by_user(user_id)
    return {"sessions": [dict(s) for s in sessions], "active": active_capture_count()}


@app.get("/api/network/sessions/{session_id}/packets")
def get_capture_packets(session_id: int, limit: int = 200):
    session = get_capture_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    packets = get_packets_by_session(session_id, limit=limit)
    return {"packets": [dict(p) for p in packets], "session": dict(session)}


@app.get("/api/network/sessions/{session_id}/report")
def capture_report(session_id: int):
    session = get_capture_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    try:
        pdf_bytes = generate_pdf(session)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    filename = f"capture_{session_id}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


class ChatRequest(BaseModel):
    user_id: int
    message: str = Field(min_length=1, max_length=4000)


@app.post("/api/chat")
def chat_endpoint(data: ChatRequest):
    _require_user(data.user_id)
    add_chat_message(data.user_id, "user", data.message)
    history = get_chat_history(data.user_id, limit=20)
    messages = [
        {"role": m["role"], "content": m["content"]} for m in history
    ]
    try:
        import httpx

        with httpx.Client(timeout=180) as client:
            resp = client.post(
                "http://localhost:11434/api/chat",
                json={
                    "model": "llama3.2:3b",
                    "messages": messages,
                    "stream": False,
                },
            )
            resp.raise_for_status()
            reply = resp.json().get("message", {}).get("content", "").strip()
    except Exception as exc:
        add_chat_message(data.user_id, "assistant", f"Ollama error: {exc}")
        raise HTTPException(
            status_code=502,
            detail="Could not reach Ollama. Make sure it is running with `ollama serve`.",
        )
    add_chat_message(data.user_id, "assistant", reply)
    return {"reply": reply}


@app.get("/api/chat/history")
def chat_history(user_id: int):
    _require_user(user_id)
    history = get_chat_history(user_id, limit=100)
    return {"messages": [dict(m) for m in history]}


@app.get("/api/pentest/tools")
def pentest_tools():
    return {"tools": TOOLS}


@app.get("/api/pentest/mcp/status")
def pentest_mcp_status(tool: str):
    try:
        return {"status": mcp_status(tool)}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/api/pentest/mcp/connect")
def pentest_mcp_connect(tool: str):
    try:
        return mcp_connect(tool)
    except ConnectionError as exc:
        raise HTTPException(status_code=502, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


class RunToolRequest(BaseModel):
    user_id: int
    tool: str


@app.post("/api/projects/{project_id}/pentest/run")
def pentest_run_tool(project_id: int, data: RunToolRequest):
    _require_user(data.user_id)
    project = get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    try:
        summary, tool_name = run_tool(project, data.tool)
    except ConnectionError as exc:
        raise HTTPException(status_code=502, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    result_id = add_pentest_result(project_id, data.user_id, data.tool, summary)
    return {"result_id": result_id, "tool": tool_name, "summary": summary}


@app.get("/api/projects/{project_id}/pentest/results")
def pentest_results(project_id: int):
    project = get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"results": [dict(r) for r in get_pentest_results(project_id)]}


class RunUrlRequest(BaseModel):
    user_id: int
    tool: str
    url: str = Field(min_length=1, max_length=2000)


@app.post("/api/pentest/run-url")
def pentest_run_url(data: RunUrlRequest):
    _require_user(data.user_id)
    url = data.url.strip()
    if not url.startswith(("http://", "https://")):
        raise HTTPException(
            status_code=400, detail="Enter a valid URL starting with http:// or https://"
        )
    from urllib.parse import urlparse

    name = urlparse(url).netloc or "url-target"
    try:
        summary, tool_name = run_tool_url(None, data.tool, url)
    except ConnectionError as exc:
        raise HTTPException(status_code=502, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    project_id = create_project(
        data.user_id, name, "url", url, ""
    )
    result_id = add_pentest_result(project_id, data.user_id, data.tool, summary)
    return {
        "result_id": result_id,
        "project_id": project_id,
        "tool": tool_name,
        "summary": summary,
    }


@app.get("/api/report/data")
def report_data(user_id: int):
    _require_user(user_id)
    return {"report": collect_report_data(user_id)}


@app.get("/api/report/pdf")
@app.get("/api/dashboard/graphs")
def dashboard_graphs(user_id: int):
    _require_user(user_id)
    return {
        "netrix": get_netrix_graph_data(user_id),
        "chat_usage": get_chat_usage_graph_data(user_id),
    }


@app.get("/api/report/pdf")
def report_pdf(user_id: int):
    user = _require_user(user_id)
    try:
        pdf_bytes = generate_report_pdf(user_id, user["username"])
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    filename = "cyberlens_report.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


class CodeScanRequest(BaseModel):
    user_id: int


@app.post("/api/projects/{project_id}/code-security/scan")
def code_security_scan(project_id: int, data: CodeScanRequest):
    _require_user(data.user_id)
    project = get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    if not _ollama_available():
        raise HTTPException(
            status_code=502,
            detail="Ollama is not running. Start it with `ollama serve`.",
        )
    try:
        result = scan_project(project, data.user_id)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    return {"message": "Code security scan complete", "result": result}


@app.get("/api/projects/{project_id}/code-security/findings")
def code_security_findings(project_id: int):
    project = get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"findings": [dict(f) for f in get_code_findings(project_id)]}


# ==========================================
# LAYER 3, 4, 5, 6: CYBER REASONING SYSTEM (CRS) ENDPOINTS
# ==========================================
from agent_mesh_service import list_available_agents, dispatch_agent
from knowledge_graph_service import build_security_knowledge_graph
from crs_service import execute_crs_pipeline
from fuzzing_service import run_fuzzing_simulation
from database import (
    get_crs_runs_by_project,
    get_crs_run,
    get_crs_patches,
    get_crs_certificates_by_project,
    get_crs_certificate_by_id,
    add_agent_mesh_task,
    get_agent_mesh_tasks,
)


@app.get("/api/crs/agents")
def get_agents():
    return {"agents": list_available_agents()}


class AgentMeshRequest(BaseModel):
    user_id: int
    agent_id: str
    query: Optional[str] = ""


@app.post("/api/projects/{project_id}/crs/agent-mesh/run")
def run_agent_mesh(project_id: int, data: AgentMeshRequest):
    _require_user(data.user_id)
    project = get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    try:
        res = dispatch_agent(project["storage_path"], data.agent_id, data.query)
        add_agent_mesh_task(
            project_id=project_id,
            user_id=data.user_id,
            agent_id=res["agent_id"],
            agent_name=res["agent_name"],
            query=data.query or "General Specialty Analysis",
            output=res["output"],
            status=res["status"],
        )
        return {"result": res}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/api/projects/{project_id}/crs/agent-mesh/tasks")
def get_agent_tasks(project_id: int):
    project = get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"tasks": [dict(t) for t in get_agent_mesh_tasks(project_id)]}


@app.get("/api/projects/{project_id}/crs/knowledge-graph")
def get_knowledge_graph(project_id: int):
    project = get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    try:
        graph = build_security_knowledge_graph(project["storage_path"], project["name"])
        return {"graph": graph}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


class CRSPipelineRequest(BaseModel):
    user_id: int
    finding_id: Optional[int] = None
    target_file: Optional[str] = None


@app.post("/api/projects/{project_id}/crs/pipeline/run")
def run_crs_pipeline(project_id: int, data: CRSPipelineRequest):
    _require_user(data.user_id)
    project = get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    try:
        result = execute_crs_pipeline(
            project=project,
            user_id=data.user_id,
            finding_id=data.finding_id,
            target_file=data.target_file,
        )
        return {"message": "CRS closed-loop run complete", "result": result}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


class FuzzRequest(BaseModel):
    file_path: str
    cwe_id: Optional[str] = "CWE-120"
    iterations: Optional[int] = 2500


@app.post("/api/projects/{project_id}/crs/fuzzing/trigger")
def trigger_fuzzing(project_id: int, data: FuzzRequest):
    project = get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    try:
        result = run_fuzzing_simulation(data.file_path, data.cwe_id, data.iterations)
        return {"fuzz_result": result}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/api/projects/{project_id}/crs/runs")
def get_crs_runs(project_id: int):
    project = get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    runs = get_crs_runs_by_project(project_id)
    return {"runs": [dict(r) for r in runs]}


@app.get("/api/crs/runs/{run_id}/patches")
def get_run_patches(run_id: int):
    patches = get_crs_patches(run_id)
    return {"patches": [dict(p) for p in patches]}


@app.get("/api/projects/{project_id}/crs/certificates")
def get_certificates(project_id: int):
    project = get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    certs = get_crs_certificates_by_project(project_id)
    return {"certificates": [dict(c) for c in certs]}


@app.get("/api/crs/certificates/{certificate_id}")
def get_single_certificate(certificate_id: str):
    cert = get_crs_certificate_by_id(certificate_id)
    if cert is None:
        raise HTTPException(status_code=404, detail="Certificate not found")
    return {"certificate": dict(cert)}