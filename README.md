# 🛡️ AI-KAVACH (CyberLens): Sovereign Cyber Reasoning & Self-Healing Defense System

> **Defensive by Design | Indian Armed Forces & National Security Cyber Challenge**

AI-KAVACH is an autonomous, air-gapped **Cyber Reasoning System (CRS)** built to discover, analyze, and repair zero-day vulnerabilities in critical defense software (e.g., Software-Defined Radios, UAV drone telemetry links, radar tracking modules) and mathematically prove that the fix holds with **0% functional regression**.

---

## 🏛️ 8-Layer System Architecture

1. **Layer 1: Enterprise & Tactical Sources**: Ingestion of multi-language air-gapped repositories (C/C++, Python, Rust, Go) and SDR tactical telemetry streams.
2. **Layer 2: Unified Ingestion & Fuzzing**: Static AST taint analysis (`Tree-sitter`, `Semgrep`) combined with coverage-guided fuzzing (`AFL++`, `Atheris`) capturing reproducible AddressSanitizer (ASAN) crash dumps.
3. **Layer 3: Collaborative Agent Mesh**: 36+ non-sequential defense agents (Root Cause Analysis, Reverse Engineering, Threat Modeling, SBOM, IAM).
4. **Layer 4: Security Knowledge Graph**: Code Property Graph (CPG) mapping source-to-sink dataflow paths and eliminating unreachable dead-code alerts.
5. **Layer 5: Security Reasoning Engine**: Quantized local Small Language Models (`Llama-3.2:3b` / `Qwen2.5-Coder-7b` via Ollama) performing AST context slicing and minimal Git unified diff (`.patch`) synthesis.
6. **Layer 6: Verification Layer (Dual-Gate Sandbox)**:
   - **Gate 1 (Exploit Immunity)**: Re-runs the PoC exploit payload; requires **Exit Code 0** (clean memory state).
   - **Gate 2 (Zero Regression)**: Executes full functional test suites; requires **100% invariant preservation**.
   - **Automated Self-Correction**: Sandbox test and compiler errors loop back into the SLM for up to 3 iterative repair turns.
   - **Cryptographic Audit**: Issues tamper-evident **SHA-256 Proof-of-Fix Certificates**.
7. **Layer 7: Delivery Layer**: Real-time Tactical Web Console and automated PR hot-patching.
8. **Layer 8: Sovereign Cross-Cutting Services**: Zero-telemetry enforcer, local model registry, and defense role-based access control.

---

## ⚡ Quick Start & Local Setup

### 1. Prerequisites
- Python 3.10+
- Node.js 18+
- [Ollama](https://ollama.com) (Optional for local SLM inference: `ollama pull llama3.2:3b` / `ollama pull qwen2.5-coder:7b`)

### 2. Backend Installation & Startup
```bash
cd backend
python -m pip install -r requirements.txt
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

### 3. Frontend Installation & Startup
```bash
cd frontend
npm install
npm run dev -- --host 127.0.0.1 --port 5173
```

### 4. Setup Army Tactical Demo Data (Optional)
```bash
python setup_army_demo_data.py
```
- **Tactical Officer Login**: `major_kavach` / `KavachSecure@2026`
- **Tactical Project**: `INDIAN-ARMY-TACTICAL-COMM-SUITE`

---

## 📂 Repository Structure

```
├── backend/
│   ├── ast_service.py              # Tree-sitter AST parsing & taint analysis
│   ├── fuzzing_service.py          # AFL++ / Atheris coverage fuzzing simulator
│   ├── knowledge_graph_service.py  # Code Property Graph (CPG) generator
│   ├── agent_mesh_service.py       # 10+ Collaborative defense agents
│   ├── harness_service.py          # Dual-Gate sandbox verification & SHA-256 signer
│   ├── crs_service.py              # Master Closed-Loop CRS orchestrator
│   ├── database.py                 # SQLite database & CRS tables
│   ├── main.py                     # FastAPI REST API endpoints
│   └── requirements.txt            # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── KavachCRS.jsx       # Flagship 5-Tab Cyber Reasoning Console
│   │   │   ├── CodeSecurity.jsx    # Inline Auto-Repair (CRS) findings
│   │   │   ├── Dashboard.jsx       # Tactical metrics & sovereign status
│   │   │   └── ...
│   │   ├── components/
│   │   │   └── Sidebar.jsx         # Navigation & Light/Dark theme toggle
│   │   ├── api.js                  # Frontend API client
│   │   └── index.css               # Clean responsive design system
│   ├── package.json
│   └── vite.config.js
├── setup_army_demo_data.py         # Populates tactical military datasets
└── README.md
```

---

## 🔒 Defense Sovereignty & Air-Gap Compliance
- **Zero External Telemetry**: 100% offline execution with zero outbound bytes.
- **Edge-Hardware Optimized**: Runs on standard 16GB RAM tactical laptops and 1U servers.
- **Auditability**: Cryptographically verified SHA-256 certificate ledger.
