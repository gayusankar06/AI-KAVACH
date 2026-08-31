import json
import re

import httpx

from database import clear_code_findings, add_code_finding
from project_service import list_files, read_file

OLLAMA_URL = "http://localhost:11434"
MODEL = "llama3.2:3b"

TEXT_EXTS = {
    "py", "js", "jsx", "ts", "tsx", "go", "rb", "php", "java",
    "c", "cpp", "json", "yaml", "yml", "html", "css", "md",
    "txt", "sql", "sh", "conf", "cfg", "ini", "toml", "vue", "cs",
}

NO_EXT_NAMES = {
    "README", "readme", "Makefile", "makefile", "Dockerfile", "LICENSE",
    "LICENCE", "CHANGELOG", "CHANGELOG.md", "VERSION", "Procfile",
    ".env.example", ".gitignore", ".dockerignore", "Jenkinsfile",
    "Gemfile", "Rakefile", "Vagrantfile",
}

SYSTEM_PROMPT = (
    "You are a senior application security reviewer. Analyze the source file "
    "provided and identify security vulnerabilities. Return ONLY a valid JSON "
    "array of findings. Each finding must have exactly these keys: "
    "severity (one of: critical, high, medium, low), title (short string), "
    "description (2-4 sentences, technical), code_snippet (the exact "
    "vulnerable line(s) from the file). If there are no vulnerabilities, "
    "return an empty array []. Do not add explanations outside the JSON."
)


def _ollama_available():
    try:
        resp = httpx.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        resp.raise_for_status()
        return True
    except Exception:
        return False


def _extract_json(text):
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    match = re.search(r"\[.*\]", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass
    return None


def _analyze_file(path, content, chunk_limit=3000):
    findings = []
    chunks = [
        content[i : i + chunk_limit] for i in range(0, len(content), chunk_limit)
    ][:6]
    for chunk in chunks:
        user_content = f"FILE: {path}\n\n{chunk}"
        resp = httpx.post(
            f"{OLLAMA_URL}/api/chat",
            json={
                "model": MODEL,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_content},
                ],
                "stream": False,
            },
            timeout=300,
        )
        resp.raise_for_status()
        reply = resp.json().get("message", {}).get("content", "")
        parsed = _extract_json(reply)
        if isinstance(parsed, list):
            for item in parsed:
                if isinstance(item, dict):
                    findings.append(item)
    return findings


def scan_project(project, user_id):
    files = list_files(project["storage_path"])
    targets = [
        f
        for f in files
        if f["size"] < 200 * 1024
        and (f["extension"] in TEXT_EXTS or f["path"].split("/")[-1] in NO_EXT_NAMES)
    ][:20]

    clear_code_findings(project["id"])

    all_findings = []
    analyzed_files = 0
    for f in targets:
        try:
            target = read_file(project["storage_path"], f["path"])
            content = target.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        try:
            file_findings = _analyze_file(f["path"], content)
        except Exception:
            continue
        analyzed_files += 1
        for finding in file_findings:
            severity = str(finding.get("severity", "medium")).lower()
            if severity not in ("critical", "high", "medium", "low", "info"):
                severity = "medium"
            add_code_finding(
                project["id"],
                user_id,
                f["path"],
                severity,
                str(finding.get("title", "Potential issue"))[:200],
                str(finding.get("description", ""))[:2000],
                str(finding.get("code_snippet", ""))[:2000],
            )
            all_findings.append(finding)

    return {"analyzed_files": analyzed_files, "findings": len(all_findings)}