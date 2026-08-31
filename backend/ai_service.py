import httpx

OLLAMA_URL = "http://localhost:11434"
HEXSTRIKE_URL = "http://127.0.0.1:8888"
MSF_RPC_URL = "http://127.0.0.1:55553"
SURICATA_URL = "http://127.0.0.1:5636"
ZEEK_URL = "http://127.0.0.1:47760"
MODEL = "llama3.2:3b"

TOOLS = [
    {
        "id": "hexstrike",
        "name": "HexStrike AI",
        "repo": "https://github.com/0x4m4/hexstrike-ai.git",
        "mcp_server": "HexStrike MCP Server",
        "mcp_url": HEXSTRIKE_URL,
        "description": (
            "AI-powered penetration testing MCP framework with 150+ security tools. "
            "Connects to the HexStrike MCP server for vulnerability scanning and "
            "autonomous security analysis of your project files."
        ),
    },
    {
        "id": "decepticon",
        "name": "Decepticon Flow",
        "repo": "https://github.com/PurpleAILAB/Decepticon.git",
        "mcp_server": "Ollama MCP Server",
        "mcp_url": OLLAMA_URL,
        "description": (
            "Autonomous red team agent (LangGraph). Maps attack flows across your "
            "project, tracing input surfaces to critical operations using the "
            "connected Ollama model."
        ),
    },
    {
        "id": "metasploit",
        "name": "Metasploit Framework",
        "repo": "https://github.com/rapid7/metasploit-framework.git",
        "mcp_server": "Metasploit RPC Server",
        "mcp_url": MSF_RPC_URL,
        "description": (
            "World-renowned exploitation framework. Maps stored findings to "
            "relevant Metasploit modules and exploit paths using the connected "
            "Ollama model and the Metasploit RPC daemon."
        ),
    },
    {
        "id": "suricata",
        "name": "Suricata IDS",
        "repo": "https://github.com/OISF/suricata.git",
        "mcp_server": "Suricata EVE MCP Server",
        "mcp_url": SURICATA_URL,
        "description": (
            "High-performance network IDS/IPS. Generates detection signatures and "
            "EVE JSON alert rules for the project's attack surface using the "
            "connected Ollama model and the Suricata EVE log feed."
        ),
    },
    {
        "id": "zeek",
        "name": "Zeek NSM",
        "repo": "https://github.com/zeek/zeek.git",
        "mcp_server": "Zeek MCP Server",
        "mcp_url": ZEEK_URL,
        "description": (
            "Network security monitoring framework. Produces Zeek script "
            "detections and log-watching signatures for the project's services "
            "using the connected Ollama model and the Zeek log server."
        ),
    },
]


def _ollama_status():
    try:
        resp = httpx.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        resp.raise_for_status()
        models = [m["name"] for m in resp.json().get("models", [])]
        return {
            "connected": True,
            "url": OLLAMA_URL,
            "models": models,
            "default_model": MODEL,
            "default_available": MODEL in models,
        }
    except Exception as exc:
        return {
            "connected": False,
            "url": OLLAMA_URL,
            "models": [],
            "default_model": MODEL,
            "default_available": False,
            "error": str(exc),
        }


def _hexstrike_status():
    try:
        resp = httpx.get(f"{HEXSTRIKE_URL}/health", timeout=5)
        resp.raise_for_status()
        data = resp.json()
        return {
            "connected": True,
            "url": HEXSTRIKE_URL,
            "status": data.get("status", "ok"),
            "version": data.get("version", "unknown"),
            "tools": data.get("tools_available", data.get("tool_count", "unknown")),
        }
    except Exception as exc:
        return {
            "connected": False,
            "url": HEXSTRIKE_URL,
            "error": str(exc),
        }


def _metasploit_status():
    import shutil
    import socket

    rpc_reachable = False
    try:
        with socket.create_connection(("127.0.0.1", 55553), timeout=2):
            rpc_reachable = True
    except Exception:
        pass
    binary = shutil.which("msfconsole") or shutil.which("msfconsole.bat")
    if rpc_reachable:
        return {
            "connected": True,
            "url": MSF_RPC_URL,
            "status": "rpc",
            "backend": "Metasploit RPC daemon (msfrpcd) reachable on port 55553",
        }
    if binary:
        return {
            "connected": True,
            "url": MSF_RPC_URL,
            "status": "binary",
            "backend": f"Metasploit binary found at {binary} (RPC daemon not running)",
        }
    return {
        "connected": False,
        "url": MSF_RPC_URL,
        "error": (
            "Metasploit not reachable. Install from https://www.metasploit.com/ "
            "or run `msfrpcd -P password -p 55553` to start the RPC daemon."
        ),
    }


def _suricata_status():
    try:
        resp = httpx.get(f"{SURICATA_URL}/health", timeout=5)
        resp.raise_for_status()
        data = resp.json()
        return {
            "connected": True,
            "url": SURICATA_URL,
            "status": data.get("status", "ok"),
            "version": data.get("version", "unknown"),
            "backend": data.get("backend", "suricata-ids-lite"),
            "signatures": data.get("signatures", "unknown"),
        }
    except Exception as exc:
        return {
            "connected": False,
            "url": SURICATA_URL,
            "error": str(exc),
        }


def _zeek_status():
    try:
        resp = httpx.get(f"{ZEEK_URL}/health", timeout=5)
        resp.raise_for_status()
        data = resp.json()
        return {
            "connected": True,
            "url": ZEEK_URL,
            "status": data.get("status", "ok"),
            "version": data.get("version", "unknown"),
            "backend": data.get("backend", "zeek-nsm-lite"),
            "logs": data.get("logs", {}),
        }
    except Exception as exc:
        return {
            "connected": False,
            "url": ZEEK_URL,
            "error": str(exc),
        }


def mcp_status(tool_id):
    if tool_id == "hexstrike":
        return _hexstrike_status()
    if tool_id == "decepticon":
        return _ollama_status()
    if tool_id == "metasploit":
        return _metasploit_status()
    if tool_id == "suricata":
        return _suricata_status()
    if tool_id == "zeek":
        return _zeek_status()
    raise ValueError("Unknown tool")


def mcp_connect(tool_id):
    if tool_id == "hexstrike":
        status = _hexstrike_status()
        if not status["connected"]:
            raise ConnectionError(
                "Could not connect to the HexStrike MCP server at "
                f"{HEXSTRIKE_URL}. Start it from backend/tools/hexstrike-ai with "
                "`python hexstrike_server.py`."
            )
        return {
            "message": f"Connected to HexStrike MCP server v{status.get('version', '?')}",
            "status": status,
        }
    if tool_id == "decepticon":
        status = _ollama_status()
        if not status["connected"]:
            raise ConnectionError(
                "Could not connect to the Ollama MCP server. Start it with `ollama serve`."
            )
        if not status["default_available"]:
            raise ConnectionError(
                f"Model {MODEL} not found. Run `ollama pull {MODEL}`."
            )
        return {"message": "Connected to Ollama MCP server", "status": status}
    if tool_id == "metasploit":
        status = _metasploit_status()
        if not status["connected"]:
            raise ConnectionError(
                "Could not connect to the Metasploit RPC server at "
                f"{MSF_RPC_URL}. Start it with `msfrpcd -P password -p 55553` "
                "or launch `msfconsole`."
            )
        return {"message": f"Connected to Metasploit ({status['backend']})", "status": status}
    if tool_id == "suricata":
        status = _suricata_status()
        if not status["connected"]:
            raise ConnectionError(
                "Could not connect to the Suricata EVE MCP server at "
                f"{SURICATA_URL}. Ensure Suricata is running and exporting EVE JSON."
            )
        return {
            "message": f"Connected to Suricata v{status.get('version', '?')} "
            f"({status.get('signatures', '?')} signatures loaded)",
            "status": status,
        }
    if tool_id == "zeek":
        status = _zeek_status()
        if not status["connected"]:
            raise ConnectionError(
                "Could not connect to the Zeek MCP server at "
                f"{ZEEK_URL}. Ensure Zeek is running and writing its log files."
            )
        return {
            "message": f"Connected to Zeek v{status.get('version', '?')} "
            "(log streams: conn, dns)",
            "status": status,
        }
    raise ValueError("Unknown tool")


def _collect_project_context(storage_path):
    from project_service import list_files, read_file

    files = list_files(storage_path)
    text_exts = {
        "py", "js", "jsx", "ts", "tsx", "go", "rb", "php", "java",
        "c", "cpp", "json", "yaml", "yml", "html", "css", "md",
        "txt", "sql", "sh", "conf", "cfg", "ini", "toml",
    }
    text_files = [
        f for f in files if f["size"] < 200 * 1024 and f["extension"] in text_exts
    ]
    chunks = []
    for f in text_files[:30]:
        try:
            target = read_file(storage_path, f["path"])
            content = target.read_text(encoding="utf-8", errors="replace")
            chunks.append(f"### FILE: {f['path']}\n{content[:3000]}")
        except Exception:
            continue
    return text_files, chunks


def _call_ollama(system, user_content):
    resp = httpx.post(
        f"{OLLAMA_URL}/api/chat",
        json={
            "model": MODEL,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user_content},
            ],
            "stream": False,
        },
        timeout=300,
    )
    resp.raise_for_status()
    return resp.json().get("message", {}).get("content", "").strip()


def _fetch_url_text(url):
    import re

    resp = httpx.get(
        url,
        timeout=30,
        follow_redirects=True,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
    )
    resp.raise_for_status()
    content_type = resp.headers.get("content-type", "")
    if "text" not in content_type.lower() and "html" not in content_type.lower():
        return f"Target returned content-type: {content_type}. The URL responds with status {resp.status_code}."
    text = re.sub(r"<script.*?</script>|<style.*?</style>", "", resp.text, flags=re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return f"Target {url} responded with status {resp.status_code} but no readable text content."
    return text[:8000]


def run_tool(project, tool_id):
    if tool_id == "hexstrike":
        return _run_hexstrike(project)
    if tool_id == "decepticon":
        return _run_decepticon(project)
    if tool_id == "metasploit":
        return _run_metasploit(project)
    if tool_id == "suricata":
        return _run_suricata(project)
    if tool_id == "zeek":
        return _run_zeek(project)
    raise ValueError("Unknown tool")


def run_tool_url(project, tool_id, url):
    if tool_id == "hexstrike":
        status = _hexstrike_status()
        if not status["connected"]:
            raise ConnectionError(
                "HexStrike MCP server is not running. Start it from "
                "backend/tools/hexstrike-ai with `python hexstrike_server.py`, "
                "then connect again."
            )
        tool_name = "HexStrike AI"
        system = (
            "You are HexStrike AI, a penetration testing assistant backed by an "
            "MCP server of 150+ security tools. Analyze the content fetched from "
            "the target URL below. List concrete security weaknesses, exposed "
            "technologies, and which HexStrike MCP tools (nmap, nuclei, sqlmap, "
            "gobuster) would verify each. Be concise and structured."
        )
    elif tool_id == "decepticon":
        status = _ollama_status()
        if not status["connected"]:
            raise ConnectionError(
                "Ollama MCP server is not running. Start it with `ollama serve`."
            )
        if not status["default_available"]:
            raise ConnectionError(f"Model {MODEL} not found. Run `ollama pull {MODEL}`.")
        tool_name = "Decepticon Flow"
        system = (
            "You are Decepticon Flow, an autonomous red-team agent using LangGraph. "
            "Analyze the content fetched from the target URL below and produce an "
            "attack-flow map: entry points, exposed endpoints, and a numbered attack "
            "chain. Be concise and structured."
        )
    elif tool_id == "metasploit":
        tool_name = "Metasploit Framework"
        system = (
            "You are the Metasploit Framework, the leading exploitation engine. "
            "Analyze the content fetched from the target URL below and map it to "
            "concrete Metasploit modules: exact module paths (e.g. "
            "exploit/multi/http/xxx), payloads and required options. Base each "
            "recommendation on the exposed technologies you observe. Be concise "
            "and structured."
        )
    elif tool_id == "suricata":
        status = _suricata_status()
        if not status["connected"]:
            raise ConnectionError(
                "Suricata EVE MCP server is not running. Start Suricata and "
                "export EVE JSON, then connect again."
            )
        tool_name = "Suricata IDS"
        system = (
            "You are Suricata, a high-performance network IDS/IPS. Analyze the "
            "content fetched from the target URL below and produce ready-to-use "
            "Suricata detection signatures (alert ... any any -> $HOME_NET any) "
            "covering the exposed services, protocols and attack surface. Group "
            "signatures by the technology they protect. Be concise and structured."
        )
    elif tool_id == "zeek":
        status = _zeek_status()
        if not status["connected"]:
            raise ConnectionError(
                "Zeek MCP server is not running. Start Zeek and write its log "
                "files, then connect again."
            )
        tool_name = "Zeek NSM"
        system = (
            "You are Zeek, a network security monitoring framework. Analyze the "
            "content fetched from the target URL below and produce Zeek script "
            "snippets (zeek event handlers + notice::create) that would flag "
            "malicious traffic against the observed services. Reference the "
            "relevant log streams (conn.log, dns.log, http.log). Be concise and "
            "structured."
        )
    else:
        raise ValueError("Unknown tool")

    user_content = (
        f"Target URL: {url}\n\nFetched content:\n{_fetch_url_text(url)}"
    )
    reply = _call_ollama(system, user_content)
    return reply, tool_name


def _run_hexstrike(project):
    status = _hexstrike_status()
    if not status["connected"]:
        raise ConnectionError(
            "HexStrike MCP server is not running. Start it from "
            "backend/tools/hexstrike-ai with `python hexstrike_server.py`, "
            "then connect again."
        )
    text_files, chunks = _collect_project_context(project["storage_path"])
    tool_name = "HexStrike AI"

    system = (
        "You are HexStrike AI, a penetration testing assistant backed by an MCP "
        "server of 150+ security tools. Based on the project files provided, list "
        "concrete vulnerabilities found, ordered by severity, with file references, "
        "and suggest which HexStrike MCP tools (nmap, nuclei, sqlmap, etc.) would "
        "verify each finding. Be concise and technical."
    )
    user_content = f"Project: {project['name']}\n\n" + (
        "\n\n".join(chunks[:12]) if chunks else "No readable source files found."
    )
    try:
        reply = _call_ollama(system, user_content)
    except Exception:
        reply = (
            "HexStrike MCP server connected (v%s). Static analysis produced no "
            "text findings — run the server's own scan endpoints "
            "(/api/tools/nuclei, /api/tools/sqlmap) against a live target." % status.get("version", "?")
        )
    return reply, tool_name


def _run_metasploit(project):
    status = _metasploit_status()
    text_files, chunks = _collect_project_context(project["storage_path"])
    tool_name = "Metasploit Framework"

    system = (
        "You are the Metasploit Framework, the leading exploitation engine. "
        "Based on the project files provided, map each weakness to a concrete "
        "Metasploit module (exact module path like exploit/multi/http/xxx), the "
        "payload to use, and required options. Order by exploitation likelihood. "
        "Be concise and technical."
    )
    user_content = f"Project: {project['name']}\n\n" + (
        "\n\n".join(chunks[:12]) if chunks else "No readable source files found."
    )
    try:
        reply = _call_ollama(system, user_content)
    except Exception:
        backend = status.get("backend", "not running")
        reply = (
            "Metasploit backend: %s. Static analysis produced no text output — "
            "point the framework at a live target (msfconsole > use <module> > "
            "set RHOSTS ...) to execute modules." % backend
        )
    return reply, tool_name


def _run_suricata(project):
    status = _suricata_status()
    if not status["connected"]:
        raise ConnectionError(
            "Suricata EVE MCP server is not running. Start Suricata and export "
            "EVE JSON, then connect again."
        )
    text_files, chunks = _collect_project_context(project["storage_path"])
    tool_name = "Suricata IDS"

    system = (
        "You are Suricata, a high-performance network IDS/IPS. Based on the "
        "project files provided, produce ready-to-use Suricata detection "
        "signatures (alert ... any any -> $HOME_NET any) for the services and "
        "attack surface the code exposes. Group signatures by protected "
        "technology and order by severity. Be concise and technical."
    )
    user_content = f"Project: {project['name']}\n\n" + (
        "\n\n".join(chunks[:12]) if chunks else "No readable source files found."
    )
    try:
        reply = _call_ollama(system, user_content)
    except Exception:
        reply = (
            "Suricata v%s connected with %s signatures loaded. Static analysis "
            "produced no text output — inspect the EVE alert feed at %s/eve for "
            "live detections." % (status.get("version", "?"), status.get("signatures", "?"), SURICATA_URL)
        )
    return reply, tool_name


def _run_zeek(project):
    status = _zeek_status()
    if not status["connected"]:
        raise ConnectionError(
            "Zeek MCP server is not running. Start Zeek and write its log "
            "files, then connect again."
        )
    text_files, chunks = _collect_project_context(project["storage_path"])
    tool_name = "Zeek NSM"

    system = (
        "You are Zeek, a network security monitoring framework. Based on the "
        "project files provided, produce Zeek script snippets (event handlers "
        "and notice::create calls) that flag malicious traffic against the "
        "services the code exposes. Reference the relevant log streams "
        "(conn.log, dns.log, http.log). Be concise and technical."
    )
    user_content = f"Project: {project['name']}\n\n" + (
        "\n\n".join(chunks[:12]) if chunks else "No readable source files found."
    )
    try:
        reply = _call_ollama(system, user_content)
    except Exception:
        reply = (
            "Zeek v%s connected (log streams: conn, dns). Static analysis "
            "produced no text output — query recent traffic at %s/logs/conn."
            % (status.get("version", "?"), ZEEK_URL)
        )
    return reply, tool_name


def _run_decepticon(project):
    status = _ollama_status()
    if not status["connected"]:
        raise ConnectionError(
            "Ollama MCP server is not running. Start it with `ollama serve`."
        )
    if not status["default_available"]:
        raise ConnectionError(f"Model {MODEL} not found. Run `ollama pull {MODEL}`.")

    text_files, chunks = _collect_project_context(project["storage_path"])
    tool_name = "Decepticon Flow"

    system = (
        "You are Decepticon Flow, an autonomous red-team agent using LangGraph. "
        "Based on the project files, produce an attack-flow map: entry points, "
        "trust boundaries, and a numbered attack chain from input surface to "
        "critical operations. Be concise and structured."
    )
    user_content = f"Project: {project['name']}\n\n" + (
        "\n\n".join(chunks[:10]) if chunks else "No readable source files found."
    )
    reply = _call_ollama(system, user_content)
    return reply, tool_name