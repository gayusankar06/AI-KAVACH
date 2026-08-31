"""
Layer 2 & 4: AST Ingestion, Taint Analysis, and Code Property Extraction.
Parses source files, detects sources and sinks, and prunes context windows for local SLM reasoning.
"""

import os
import re
from typing import List, Dict, Any

# Common dangerous sink signatures across C/C++, Python, Go, JS, Rust
DANGEROUS_SINKS = {
    "c_cpp": [
        (r"\bstrcpy\s*\(", "Buffer Overflow (strcpy unchecked copy)", "CWE-120"),
        (r"\bstrcat\s*\(", "Buffer Overflow (strcat unchecked concat)", "CWE-120"),
        (r"\bsprintf\s*\(", "Format String / Buffer Overflow", "CWE-134"),
        (r"\bgets\s*\(", "Critical Unbounded Buffer Read (gets)", "CWE-242"),
        (r"\bsystem\s*\(", "Command Injection via system()", "CWE-78"),
        (r"\bmemcpy\s*\([^,]+,[^,]+,\s*([a-zA-Z0-9_]+)\)", "Potential Buffer Overflow in memcpy", "CWE-120"),
        (r"\bfree\s*\(([a-zA-Z0-9_]+)\).*\bfree\s*\(\1\)", "Double Free Vulnerability", "CWE-415"),
    ],
    "python": [
        (r"\bos\.system\s*\(", "OS Command Execution", "CWE-78"),
        (r"\bsubprocess\.(Popen|run|call)\s*\([^,]+shell\s*=\s*True", "Shell Command Injection", "CWE-78"),
        (r"\beval\s*\(", "Arbitrary Code Execution via eval()", "CWE-95"),
        (r"\bexec\s*\(", "Arbitrary Code Execution via exec()", "CWE-95"),
        (r"\bpickle\.loads?\s*\(", "Insecure Deserialization", "CWE-502"),
        (r"cursor\.execute\s*\(\s*f?[\"'].*?%s|format\(|\+", "SQL Injection (Unparameterized query)", "CWE-89"),
    ],
    "javascript": [
        (r"\beval\s*\(", "DOM / Server Code Execution", "CWE-95"),
        (r"\bchild_process\.exec\s*\(", "Command Injection", "CWE-78"),
        (r"innerHTML\s*=", "Cross-Site Scripting (XSS)", "CWE-79"),
        (r"dangerouslySetInnerHTML", "React Raw HTML Injection", "CWE-79"),
    ],
    "go": [
        (r"\bexec\.Command\s*\(", "OS Command Execution", "CWE-78"),
        (r"\bdb\.Query\s*\(f?[\"'].*?\+", "SQL Injection in Go Query", "CWE-89"),
    ]
}

INPUT_SOURCES = [
    r"request\.(GET|POST|args|form|values|json|body)",
    r"sys\.argv",
    r"argv\[\d+\]",
    r"stdin",
    r"req\.(query|body|params|headers)",
    r"cin\s*>>",
    r"scanf\s*\(",
    r"fgets\s*\(",
]


def extract_ast_features(file_path: str, content: str) -> Dict[str, Any]:
    """Analyzes AST / Lexical patterns to find functions, sources, sinks, and taint paths."""
    ext = file_path.split(".")[-1].lower() if "." in file_path else ""
    lang_key = "c_cpp" if ext in ("c", "cpp", "h", "hpp") else \
               "python" if ext == "py" else \
               "javascript" if ext in ("js", "jsx", "ts", "tsx") else \
               "go" if ext == "go" else "python"

    lines = content.splitlines()
    functions = []
    sinks_found = []
    sources_found = []

    # Function detection regexes
    func_regex = r"def\s+([a-zA-Z0-9_]+)\s*\(" if lang_key == "python" else \
                 r"(?:void|int|char|bool|float|double|[A-Za-z0-9_]+)\s+([a-zA-Z0-9_]+)\s*\([^)]*\)\s*\{" if lang_key == "c_cpp" else \
                 r"function\s+([a-zA-Z0-9_]+)\s*\("

    for idx, line in enumerate(lines):
        line_num = idx + 1
        # Detect function declarations
        f_match = re.search(func_regex, line)
        if f_match:
            functions.append({
                "name": f_match.group(1),
                "line": line_num,
                "signature": line.strip()
            })

        # Detect input sources
        for src_pat in INPUT_SOURCES:
            if re.search(src_pat, line):
                sources_found.append({
                    "line": line_num,
                    "code": line.strip(),
                    "pattern": src_pat
                })
                break

        # Detect dangerous sinks
        for sink_pat, desc, cwe in DANGEROUS_SINKS.get(lang_key, []):
            if re.search(sink_pat, line):
                sinks_found.append({
                    "line": line_num,
                    "code": line.strip(),
                    "title": desc,
                    "cwe": cwe,
                    "severity": "critical" if "Overflow" in desc or "Command" in desc or "Execution" in desc else "high"
                })

    # Derive taint reachability paths
    reachability_paths = []
    for src in sources_found:
        for sink in sinks_found:
            if src["line"] <= sink["line"]:
                reachability_paths.append({
                    "source_line": src["line"],
                    "sink_line": sink["line"],
                    "sink_title": sink["title"],
                    "cwe": sink["cwe"],
                    "hops": sink["line"] - src["line"]
                })

    return {
        "file_path": file_path,
        "language": lang_key,
        "loc": len(lines),
        "functions": functions,
        "sources": sources_found,
        "sinks": sinks_found,
        "reachability_paths": reachability_paths,
        "is_vulnerable": len(sinks_found) > 0
    }


def slice_code_context(content: str, target_line: int, window: int = 25) -> Dict[str, Any]:
    """Extracts a focused code slice around a vulnerable line to fit within lightweight SLM context."""
    lines = content.splitlines()
    start = max(0, target_line - window - 1)
    end = min(len(lines), target_line + window)
    
    numbered_slice = [
        f"{idx + 1:4d} | {lines[idx]}" for idx in range(start, end)
    ]
    raw_slice = "\n".join(lines[start:end])
    
    return {
        "start_line": start + 1,
        "end_line": end,
        "target_line": target_line,
        "slice_text": "\n".join(numbered_slice),
        "raw_text": raw_slice
    }
