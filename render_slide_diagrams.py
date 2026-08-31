"""
Renders high-resolution defense-grade diagrams for embedding into PowerPoint slides.
Creates:
1. slide2_workflow.png - 3-Stage Closed-Loop Workflow
2. slide3_architecture.png - 8-Layer Enterprise Cyber Reasoning System
3. slide4_dualgate.png - Dual-Gate Proof-of-Fix & Cryptographic Certificate
"""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Dark tactical styling
BG_COLOR = "#0A1628"
CARD_BG = "#122642"
CARD_BORDER = "#1E406A"
CYAN = "#00E5FF"
GOLD = "#FFB703"
GREEN = "#22C55E"
WHITE = "#F0F6FC"
MUTED = "#94A3B8"

plt.rcParams['font.sans-serif'] = 'Segoe UI', 'DejaVu Sans', 'Arial'
plt.rcParams['text.color'] = WHITE

def create_workflow_diagram():
    fig, ax = plt.subplots(figsize=(10, 4.2), dpi=300)
    fig.patch.set_facecolor(BG_COLOR)
    ax.set_facecolor(BG_COLOR)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 4.2)
    ax.axis('off')

    # Stage 1: Discovery Box
    box1 = patches.FancyBboxPatch((0.4, 0.6), 2.7, 3.0, boxstyle="round,pad=0.2",
                                  facecolor=CARD_BG, edgecolor=GOLD, linewidth=2)
    ax.add_patch(box1)
    ax.text(1.75, 3.2, "STAGE 1: HYBRID DISCOVERY", color=GOLD, fontsize=10, weight='bold', ha='center')
    ax.text(1.75, 2.7, "• Coverage Fuzzing (AFL++)", color=WHITE, fontsize=8.5, ha='center')
    ax.text(1.75, 2.2, "• AST Taint & Sinks (Semgrep)", color=WHITE, fontsize=8.5, ha='center')
    ax.text(1.75, 1.7, "• Network IDS (Zeek / Suricata)", color=WHITE, fontsize=8.5, ha='center')
    ax.text(1.75, 1.1, "Output: PoC Crash Payloads", color=GOLD, fontsize=8, weight='bold', ha='center')

    # Arrow 1 -> 2
    ax.annotate('', xy=(3.6, 2.1), xytext=(3.1, 2.1),
                arrowprops=dict(facecolor=CYAN, edgecolor=CYAN, width=3, headwidth=8))

    # Stage 2: Reasoning Box
    box2 = patches.FancyBboxPatch((3.7, 0.6), 2.7, 3.0, boxstyle="round,pad=0.2",
                                  facecolor=CARD_BG, edgecolor=CYAN, linewidth=2)
    ax.add_patch(box2)
    ax.text(5.05, 3.2, "STAGE 2: SLM REASONING", color=CYAN, fontsize=10, weight='bold', ha='center')
    ax.text(5.05, 2.7, "• Air-Gapped SLM (Llama 3.2)", color=WHITE, fontsize=8.5, ha='center')
    ax.text(5.05, 2.2, "• AST Context Windowing", color=WHITE, fontsize=8.5, ha='center')
    ax.text(5.05, 1.7, "• Unified Diff (.patch) Gen", color=WHITE, fontsize=8.5, ha='center')
    ax.text(5.05, 1.1, "Output: Surgical AST Patch", color=CYAN, fontsize=8, weight='bold', ha='center')

    # Arrow 2 -> 3
    ax.annotate('', xy=(6.9, 2.1), xytext=(6.4, 2.1),
                arrowprops=dict(facecolor=GREEN, edgecolor=GREEN, width=3, headwidth=8))

    # Stage 3: Verification Box
    box3 = patches.FancyBboxPatch((7.0, 0.6), 2.6, 3.0, boxstyle="round,pad=0.2",
                                  facecolor=CARD_BG, edgecolor=GREEN, linewidth=2)
    ax.add_patch(box3)
    ax.text(8.3, 3.2, "STAGE 3: PROOF-OF-FIX", color=GREEN, fontsize=10, weight='bold', ha='center')
    ax.text(8.3, 2.7, "• Gate 1: Exploit Re-run (0 Crash)", color=WHITE, fontsize=8.5, ha='center')
    ax.text(8.3, 2.2, "• Gate 2: Full Regression Suite", color=WHITE, fontsize=8.5, ha='center')
    ax.text(8.3, 1.7, "• SHA-256 Signed Proof Cert", color=WHITE, fontsize=8.5, ha='center')
    ax.text(8.3, 1.1, "Output: Verified Hot-Patch", color=GREEN, fontsize=8, weight='bold', ha='center')

    # Feedback Loop Curved Arrow (Stage 3 -> Stage 2)
    ax.annotate('Self-Correction Feedback Loop (if test fails)',
                xy=(5.05, 0.6), xytext=(8.3, 0.2),
                arrowprops=dict(facecolor='#EF4444', edgecolor='#EF4444', arrowstyle="->",
                                connectionstyle="arc3,rad=0.3", lw=1.8),
                color='#FCA5A5', fontsize=8, weight='bold', ha='right')

    plt.tight_layout()
    out_file = "e:/CyberLens/CYBERLENS--main/slide2_workflow.png"
    plt.savefig(out_file, facecolor=BG_COLOR, bbox_inches='tight')
    plt.close()
    print(f"[+] Rendered: {out_file}")

def create_architecture_diagram():
    fig, ax = plt.subplots(figsize=(10, 5.0), dpi=300)
    fig.patch.set_facecolor(BG_COLOR)
    ax.set_facecolor(BG_COLOR)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5.2)
    ax.axis('off')

    layers = [
        ("Layer 1: Enterprise & Tactical Sources", "Air-Gapped Repos • C/C++ Tactical Binaries • CI/CD • SDR Streams", GOLD),
        ("Layer 2: Unified Ingestion & Coverage Fuzzing", "AST Taint Parser • AFL++ Engine • ASAN Crash Dump Collector", CYAN),
        ("Layer 3: Collaborative AI Agent Mesh", "36+ Specialized Defense Agents (Reverse Eng, Root Cause, Patch Synthesis)", WHITE),
        ("Layer 4: Shared Security Knowledge Graph (CPG)", "Unified Code Property Graph • Symbol Reachability • CVE/CWE Store", CYAN),
        ("Layer 5: Security Reasoning Engine (SLM Core)", "Air-Gapped Quantized Model • AST Root Cause Triage • Unified Diff Synthesizer", GOLD),
        ("Layer 6: Verification Layer & Proof-of-Fix Harness", "Ephemeral Sandbox • Gate 1 Exploit Mitigation • Gate 2 Zero Regression • SHA-256 Sign", GREEN),
        ("Layer 7: Delivery & Defense Command Layer", "Executive Dashboards • Military PR Hot-Patch • Defense Compliance PDF Export", WHITE),
        ("Layer 8: Cross-Cutting Sovereign Platform Services", "Zero-Telemetry Policy • Air-Gapped Model Registry • Military Clearance RBAC", CYAN)
    ]

    y_start = 4.6
    for idx, (title, desc, col) in enumerate(layers):
        y = y_start - (idx * 0.58)
        box = patches.FancyBboxPatch((0.5, y - 0.22), 9.0, 0.48, boxstyle="round,pad=0.1",
                                      facecolor=CARD_BG, edgecolor=col, linewidth=1.2)
        ax.add_patch(box)
        ax.text(0.8, y, title, color=col, fontsize=9.5, weight='bold', va='center')
        ax.text(5.2, y, desc, color=MUTED, fontsize=8.0, va='center')

    plt.tight_layout()
    out_file = "e:/CyberLens/CYBERLENS--main/slide3_architecture.png"
    plt.savefig(out_file, facecolor=BG_COLOR, bbox_inches='tight')
    plt.close()
    print(f"[+] Rendered: {out_file}")

if __name__ == "__main__":
    create_workflow_diagram()
    create_architecture_diagram()
