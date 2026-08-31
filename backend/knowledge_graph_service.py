"""
Layer 4: Shared Security Knowledge Graph Core (CPG / Reachability Graph).
Builds a unified, queryable property graph linking Source Code, AST Sinks, Input Surfaces,
Network Telemetry, Vulnerabilities (CVE/CWE), and Synthesized Patches.
"""

from typing import Dict, Any, List
from ast_service import extract_ast_features
from project_service import list_files, read_file


def build_security_knowledge_graph(storage_path: str, project_name: str = "Defense Project") -> Dict[str, Any]:
    """
    Ingests all files in the project and constructs a multi-layer Knowledge Graph.
    Returns nodes and links formatted for interactive visualization.
    """
    files = list_files(storage_path)
    nodes: List[Dict[str, Any]] = []
    links: List[Dict[str, Any]] = []

    # Root Project Node
    root_node_id = "node_proj_root"
    nodes.append({
        "id": root_node_id,
        "label": project_name,
        "type": "project",
        "group": "core",
        "severity": "info",
        "details": f"Air-Gapped Sovereign Repository: {project_name}"
    })

    text_exts = {"py", "c", "cpp", "h", "js", "ts", "go", "rs", "java", "sh"}
    valid_files = [f for f in files if f["size"] < 150 * 1024 and f["extension"] in text_exts][:20]

    vulnerability_counter = 0

    for f in valid_files:
        file_node_id = f"file_{f['path']}"
        nodes.append({
            "id": file_node_id,
            "label": f["path"],
            "type": "file",
            "group": "source_code",
            "extension": f["extension"],
            "severity": "low"
        })
        links.append({
            "source": root_node_id,
            "target": file_node_id,
            "relation": "contains"
        })

        try:
            target_path = read_file(storage_path, f["path"])
            content = target_path.read_text(encoding="utf-8", errors="replace")
            ast_data = extract_ast_features(f["path"], content)

            # Add Function Nodes
            for fn in ast_data["functions"][:4]:
                fn_node_id = f"fn_{f['path']}_{fn['name']}"
                nodes.append({
                    "id": fn_node_id,
                    "label": f"{fn['name']}()",
                    "type": "function",
                    "group": "ast_symbol",
                    "line": fn["line"],
                    "severity": "info"
                })
                links.append({
                    "source": file_node_id,
                    "target": fn_node_id,
                    "relation": "declares"
                })

            # Add Sinks & Vulnerability Nodes
            for sink in ast_data["sinks"]:
                vulnerability_counter += 1
                vuln_node_id = f"vuln_{vulnerability_counter}"
                nodes.append({
                    "id": vuln_node_id,
                    "label": f"{sink['cwe']}: {sink['title']}",
                    "type": "vulnerability",
                    "group": "threat",
                    "cwe": sink["cwe"],
                    "severity": sink["severity"],
                    "line": sink["line"],
                    "code": sink["code"]
                })
                links.append({
                    "source": file_node_id,
                    "target": vuln_node_id,
                    "relation": "exposes_sink"
                })

            # Add Input Sources & Taint Flows
            for src in ast_data["sources"][:3]:
                src_node_id = f"src_{f['path']}_{src['line']}"
                nodes.append({
                    "id": src_node_id,
                    "label": f"Input: Line {src['line']}",
                    "type": "input_surface",
                    "group": "attack_surface",
                    "code": src["code"],
                    "severity": "medium"
                })
                links.append({
                    "source": file_node_id,
                    "target": src_node_id,
                    "relation": "ingests_input"
                })

            # Connect Reachable Taint Paths
            for path in ast_data["reachability_paths"]:
                src_id = f"src_{f['path']}_{path['source_line']}"
                # Link source to vulnerability
                matching_vulns = [n["id"] for n in nodes if n.get("type") == "vulnerability" and n.get("line") == path["sink_line"]]
                for v_id in matching_vulns:
                    links.append({
                        "source": src_id,
                        "target": v_id,
                        "relation": "taint_reaches_sink"
                    })

        except Exception:
            continue

    # Add Defense Threat Model Indicators
    network_node_id = "node_suricata_zeek"
    nodes.append({
        "id": network_node_id,
        "label": "Suricata/Zeek Telemetry Bus",
        "type": "telemetry",
        "group": "network",
        "severity": "info",
        "details": "Active EVE JSON + NSM Network Packet Monitors"
    })
    links.append({
        "source": root_node_id,
        "target": network_node_id,
        "relation": "monitored_by"
    })

    return {
        "project_name": project_name,
        "total_nodes": len(nodes),
        "total_links": len(links),
        "vulnerabilities_mapped": vulnerability_counter,
        "nodes": nodes,
        "links": links
    }
