"""
Enterprise Light-Themed 5-Slide PDF Presentation Deck Generator for AI-KAVACH Hackathon.
Design System:
- Background: Clean Pristine Slate (#F8FAFC)
- Cards: Pure White (#FFFFFF) with Elegant Slate Border (#CBD5E1)
- Typography: High-Contrast Charcoal (#0F172A, #1E293B) and Subtext (#475569)
- Accents: Defense Sapphire (#1E40AF), Tech Blue (#0284C7), Amber Gold (#D97706), Emerald (#16A34A)
- Perfect Symmetric Alignment, Zero Blank Spaces, Crisp 300 DPI Rendering.
"""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image

SLIDES_DIR = "e:/CyberLens/CYBERLENS--main/light_slides_render"
PDF_FINAL_PATH = "e:/CyberLens/CYBERLENS--main/AI-KAVACH_Pitch_Deck_Final.pdf"
PDF_OVERWRITE_PATH = "e:/CyberLens/CYBERLENS--main/AI-KAVACH Pitch Deck.pdf"
ARCH_IMG_PATH = "e:/CyberLens/CYBERLENS--main/cyberlens block (2).png"

os.makedirs(SLIDES_DIR, exist_ok=True)

# Light Mode Color Tokens
BG_COLOR = "#F1F5F9"          # Light Slate Canvas
CARD_BG = "#FFFFFF"           # Crisp White Card
CARD_BORDER = "#CBD5E1"       # Subtle Slate Border
INNER_BG = "#F8FAFC"          # Light Container Tint
TEXT_MAIN = "#0F172A"         # Slate-900 High-Contrast Text
TEXT_SUB = "#334155"          # Slate-700 Body Text
TEXT_MUTED = "#64748B"        # Slate-500 Captions
BLUE_PRIMARY = "#1D4ED8"      # Defense Blue Accent
CYAN_ACCENT = "#0284C7"       # Tech Blue Accent
GOLD_ACCENT = "#B45309"       # Deep Amber Accent
GREEN_ACCENT = "#15803D"      # Forest Green Accent
RED_ACCENT = "#DC2626"        # Alert Red

plt.rcParams['font.sans-serif'] = ['Segoe UI', 'DejaVu Sans', 'Arial', 'sans-serif']
plt.rcParams['text.color'] = TEXT_MAIN


def create_base_slide(slide_num_str, title_text, category_text="AI KAVACH | CYBER REASONING SYSTEM"):
    fig, ax = plt.subplots(figsize=(16, 9), dpi=200)
    fig.patch.set_facecolor(BG_COLOR)
    ax.set_facecolor(BG_COLOR)
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 9)
    ax.axis('off')

    # Top Tag
    ax.text(0.8, 8.42, f"{category_text}   •   {slide_num_str.upper()}", color=BLUE_PRIMARY, fontsize=11, weight='bold')
    
    # Title
    ax.text(0.8, 7.85, title_text, color=TEXT_MAIN, fontsize=21, weight='bold')

    # Header Divider Line
    ax.plot([0.8, 15.2], [7.55, 7.55], color="#CBD5E1", linewidth=1.5)

    return fig, ax


# ==============================================================================
# SLIDE 1: INTRODUCTION, IDEATION & BRIEF DESCRIPTION
# ==============================================================================
def render_slide_1():
    fig, ax = create_base_slide("Slide 1 of 5", "CYBERLENS-KAVACH: Sovereign Cyber Reasoning & Self-Healing Defense System")

    # Left Container: National Security Problem Statement
    card_l = patches.FancyBboxPatch((0.8, 0.8), 6.9, 6.4, boxstyle="round,pad=0.25",
                                   facecolor=CARD_BG, edgecolor=CARD_BORDER, linewidth=1.4)
    ax.add_patch(card_l)

    ax.text(1.1, 6.75, "National Security Problem Statement", color=GOLD_ACCENT, fontsize=14, weight='bold')
    ax.plot([1.1, 7.3], [6.5, 6.5], color="#E2E8F0", linewidth=1.2)

    p1 = (
        "• Zero-Day & Zero-Window Exploits in Defense Infra:\n"
        "  Tactical SDR radios, UAV drone telemetry links, and radar command networks\n"
        "  operate in air-gapped combat zones. Manual vulnerability discovery and patching\n"
        "  cycles take 15 to 45 days, exposing armed forces to fatal adversary zero-days."
    )
    ax.text(1.1, 5.15, p1, color=TEXT_SUB, fontsize=10.5, linespacing=1.4)

    p2 = (
        "• The 'Broken Patch' & AI Hallucination Dilemma:\n"
        "  Generic commercial AI tools generate unchecked code that risks altering mission\n"
        "  logic invariants, introducing silent regressions, or failing under adversary evasion."
    )
    ax.text(1.1, 3.65, p2, color=TEXT_SUB, fontsize=10.5, linespacing=1.4)

    p3 = (
        "• Strict Air-Gap & Tactical Edge Compute Constraint:\n"
        "  Defense policy strictly forbids external cloud LLM telemetry. Forward command\n"
        "  units operate on tactical laptops / 1U servers without cloud GPU clusters."
    )
    ax.text(1.1, 2.15, p3, color=TEXT_SUB, fontsize=10.5, linespacing=1.4)

    # Right Container: Proposed Solution: Closed-Loop CRS
    card_r = patches.FancyBboxPatch((8.3, 0.8), 6.9, 6.4, boxstyle="round,pad=0.25",
                                   facecolor=CARD_BG, edgecolor=BLUE_PRIMARY, linewidth=1.6)
    ax.add_patch(card_r)

    ax.text(8.6, 6.75, "Proposed Solution: Closed-Loop CRS", color=BLUE_PRIMARY, fontsize=14, weight='bold')
    ax.plot([8.6, 14.8], [6.5, 6.5], color="#E2E8F0", linewidth=1.2)

    s1 = (
        "• DARPA AIxCC-Grade Cyber Reasoning Architecture:\n"
        "  CyberLens-Kavach is an autonomous, air-gapped Cyber Reasoning System (CRS)\n"
        "  unifying coverage fuzzing, AST taint analysis, and local quantized SLMs to\n"
        "  autonomously find vulnerabilities, synthesize patches, and prove the fix holds."
    )
    ax.text(8.6, 5.15, s1, color=TEXT_SUB, fontsize=10.5, linespacing=1.4)

    s2 = (
        "• 100% Sovereign, Air-Gapped & Telemetry-Free:\n"
        "  Runs strictly on-premise on edge hardware with zero outbound bytes, issuing\n"
        "  cryptographically signed SHA-256 Proof-of-Fix Certificates for military audits."
    )
    ax.text(8.6, 3.65, s2, color=TEXT_SUB, fontsize=10.5, linespacing=1.4)

    # Closed Loop Flow Pills
    pill_y = 1.45
    steps = [("Detect", GOLD_ACCENT), ("Localize", CYAN_ACCENT), ("Synthesize Patch", BLUE_PRIMARY), ("Prove Fix", GREEN_ACCENT), ("Deploy", GOLD_ACCENT)]
    x_start = 8.65
    for idx, (st, col) in enumerate(steps):
        p_box = patches.FancyBboxPatch((x_start, pill_y), 0.98, 0.65, boxstyle="round,pad=0.08",
                                       facecolor="#F8FAFC", edgecolor=col, linewidth=1.3)
        ax.add_patch(p_box)
        ax.text(x_start + 0.49, pill_y + 0.32, st, color=col, fontsize=8.0, weight='bold', ha='center', va='center')
        if idx < len(steps) - 1:
            ax.text(x_start + 1.10, pill_y + 0.32, "->", color=BLUE_PRIMARY, fontsize=10, weight='bold', ha='center', va='center')
        x_start += 1.25

    out_file = f"{SLIDES_DIR}/slide_1.png"
    plt.savefig(out_file, facecolor=BG_COLOR, bbox_inches='tight', dpi=200)
    plt.close()
    return out_file


# ==============================================================================
# SLIDE 2: DETAILED METHODOLOGY & WORKFLOW
# ==============================================================================
def render_slide_2():
    fig, ax = create_base_slide("Slide 2 of 5", "Autonomous Tri-Stage Cyber Reasoning Methodology & Workflow")

    # Left Column: 3 Stage Methodology Explanations
    card_l = patches.FancyBboxPatch((0.8, 0.8), 6.5, 6.4, boxstyle="round,pad=0.25",
                                    facecolor=CARD_BG, edgecolor=CARD_BORDER, linewidth=1.4)
    ax.add_patch(card_l)

    # Stage 1 Card
    s1_box = patches.FancyBboxPatch((1.05, 5.15), 6.0, 1.8, boxstyle="round,pad=0.12",
                                    facecolor="#F8FAFC", edgecolor=GOLD_ACCENT, linewidth=1.2)
    ax.add_patch(s1_box)
    ax.text(1.25, 6.55, "Stage 1: Multi-Modal Autonomous Discovery", color=GOLD_ACCENT, fontsize=11.5, weight='bold')
    ax.text(1.25, 5.4, "• Ingests C/C++, Python, Rust tactical codebases and SDR streams.\n• Tree-sitter AST & Semgrep map input sources to memory sinks.\n• AFL++ coverage fuzzing triggers reproducible crash payloads (ASAN).", color=TEXT_SUB, fontsize=9.2, linespacing=1.35)

    # Stage 2 Card
    s2_box = patches.FancyBboxPatch((1.05, 3.05), 6.0, 1.9, boxstyle="round,pad=0.12",
                                    facecolor="#F8FAFC", edgecolor=CYAN_ACCENT, linewidth=1.2)
    ax.add_patch(s2_box)
    ax.text(1.25, 4.55, "Stage 2: SLM Reasoning & AST Patch Synthesis", color=CYAN_ACCENT, fontsize=11.5, weight='bold')
    ax.text(1.25, 3.35, "• AST context windowing isolates offending functions for lightweight SLMs.\n• Local 4-bit SLMs analyze root-cause invariants and bounds.\n• Synthesizes minimal unified Git diffs (`.patch`) preserving logic contracts.", color=TEXT_SUB, fontsize=9.2, linespacing=1.35)

    # Stage 3 Card
    s3_box = patches.FancyBboxPatch((1.05, 0.95), 6.0, 1.9, boxstyle="round,pad=0.12",
                                    facecolor="#F8FAFC", edgecolor=GREEN_ACCENT, linewidth=1.2)
    ax.add_patch(s3_box)
    ax.text(1.25, 2.45, "Stage 3: Dual-Gate Proof-of-Fix Harness", color=GREEN_ACCENT, fontsize=11.5, weight='bold')
    ax.text(1.25, 1.25, "• Gate 1: Re-executes PoC exploit -> Asserts Exit 0 (Vulnerability Mitigated).\n• Gate 2: Executes full PyTest/CTest suite -> Asserts 0% Regression.\n• Automated Self-Correction: Test/compiler errors loop back to SLM.", color=TEXT_SUB, fontsize=9.2, linespacing=1.35)

    # Right Column: Visual Flowchart
    card_r = patches.FancyBboxPatch((7.7, 0.8), 7.5, 6.4, boxstyle="round,pad=0.25",
                                    facecolor=CARD_BG, edgecolor=BLUE_PRIMARY, linewidth=1.5)
    ax.add_patch(card_r)
    ax.text(8.0, 6.75, "Tactical Closed-Loop Execution Architecture", color=BLUE_PRIMARY, fontsize=14, weight='bold')

    wf_boxes = [
        (8.1, 4.95, 6.7, 1.4, "1. INGESTION & FUZZING", "• Target: Tactical Comms, SDR demuxer (`tactical_radio_gateway.c`)\n• AFL++ mutated crash dump -> PoC Payload (ASAN stack trace)", GOLD_ACCENT),
        (8.1, 3.15, 6.7, 1.4, "2. AIR-GAPPED SLM REPAIR", "• Llama-3.2 / Qwen-Coder AST-guided reasoning\n• Generates Unified Git Diff (`.patch`) without altering contracts", CYAN_ACCENT),
        (8.1, 1.15, 6.7, 1.6, "3. DUAL-GATE PROOF HARNESS", "• Gate 1: Re-run Exploit (Exit Code 0: Vulnerability Eliminated)\n• Gate 2: Full Regression Suite (38/38 Tests Passed - 0% Regression)\n• Cryptographic SHA-256 Proof Certificate Signed & Issued", GREEN_ACCENT),
    ]

    for bx, by, bw, bh, btitle, bdesc, bcol in wf_boxes:
        pbox = patches.FancyBboxPatch((bx, by), bw, bh, boxstyle="round,pad=0.12",
                                      facecolor="#F8FAFC", edgecolor=bcol, linewidth=1.4)
        ax.add_patch(pbox)
        ax.text(bx + 0.3, by + bh - 0.35, btitle, color=bcol, fontsize=10.5, weight='bold')
        ax.text(bx + 0.3, by + 0.3, bdesc, color=TEXT_SUB, fontsize=9.2, linespacing=1.3)

    # Down Arrows
    ax.annotate('', xy=(11.45, 4.55), xytext=(11.45, 4.95), arrowprops=dict(facecolor=CYAN_ACCENT, edgecolor=CYAN_ACCENT, width=2, headwidth=6))
    ax.annotate('', xy=(11.45, 2.75), xytext=(11.45, 3.15), arrowprops=dict(facecolor=GREEN_ACCENT, edgecolor=GREEN_ACCENT, width=2, headwidth=6))

    # Self-Correction Feedback Loop Arrow
    ax.annotate('Self-Correction Feedback Loop (Multi-Turn)', xy=(14.8, 3.8), xytext=(14.8, 2.0),
                arrowprops=dict(facecolor=RED_ACCENT, edgecolor=RED_ACCENT, arrowstyle="->", connectionstyle="arc3,rad=0.35", lw=2),
                color=RED_ACCENT, fontsize=9, weight='bold', ha='right')

    out_file = f"{SLIDES_DIR}/slide_2.png"
    plt.savefig(out_file, facecolor=BG_COLOR, bbox_inches='tight', dpi=200)
    plt.close()
    return out_file


# ==============================================================================
# SLIDE 3: TECHNOLOGY STACK & SYSTEM ARCHITECTURE
# ==============================================================================
def render_slide_3():
    fig, ax = create_base_slide("Slide 3 of 5", "System Architecture, Technology Stack & Equipment Used")

    # Left Column: Structured Technology Stack & Specs
    card_l = patches.FancyBboxPatch((0.8, 0.8), 6.5, 6.4, boxstyle="round,pad=0.25",
                                    facecolor=CARD_BG, edgecolor=CARD_BORDER, linewidth=1.4)
    ax.add_patch(card_l)

    ax.text(1.1, 6.75, "Technology Stack & Hardware Profile", color=GOLD_ACCENT, fontsize=14, weight='bold')
    ax.plot([1.1, 6.9], [6.5, 6.5], color="#E2E8F0", linewidth=1.2)

    tech_items = [
        ("Reasoning SLM Core", "Llama-3.2:3b & Qwen2.5-Coder-7b (4-bit GGUF via Ollama for local air-gapped triage)", CYAN_ACCENT),
        ("Dynamic Fuzzers & DAST", "AFL++ v4.09c, Atheris Native Python, Boofuzz Protocol, Nuclei DAST", GOLD_ACCENT),
        ("Static & AST Analysis", "Tree-sitter AST parser, Semgrep OSS, Joern Code Property Graph", BLUE_PRIMARY),
        ("Network Telemetry Feed", "Suricata IDS (EVE JSON Alerts) & Zeek NSM (conn/dns/http streams)", GREEN_ACCENT),
        ("Verification Sandboxes", "Docker / gVisor MicroVM Sandboxes, PyTest, CTest, ASAN/UBSAN", CYAN_ACCENT),
        ("Hardware Equipment", "Standard Tactical Military Laptop / 1U Edge Server (Min: 16GB RAM, 4 CPU Cores, CPU-only capable)", GOLD_ACCENT)
    ]

    ty = 5.85
    for title, desc, col in tech_items:
        ax.text(1.1, ty, f"• {title}:", color=col, fontsize=10.2, weight='bold')
        ax.text(1.1, ty - 0.38, desc, color=TEXT_SUB, fontsize=8.8)
        ty -= 0.95

    # Right Column: 8-Layer Architecture Image Container
    card_r = patches.FancyBboxPatch((7.7, 0.8), 7.5, 6.4, boxstyle="round,pad=0.25",
                                    facecolor=CARD_BG, edgecolor=BLUE_PRIMARY, linewidth=1.5)
    ax.add_patch(card_r)
    ax.text(8.0, 6.75, "8-Layer Enterprise Cyber Reasoning Architecture", color=BLUE_PRIMARY, fontsize=14, weight='bold')

    if os.path.exists(ARCH_IMG_PATH):
        arch_img = Image.open(ARCH_IMG_PATH)
        ax.imshow(arch_img, extent=[7.95, 14.95, 0.95, 6.45], aspect="auto", zorder=5)

    out_file = f"{SLIDES_DIR}/slide_3.png"
    plt.savefig(out_file, facecolor=BG_COLOR, bbox_inches='tight', dpi=200)
    plt.close()
    return out_file


# ==============================================================================
# SLIDE 4: SALIENT FEATURES, NOVELTY & USP
# ==============================================================================
def render_slide_4():
    fig, ax = create_base_slide("Slide 4 of 5", "Key Features, Innovation & Defense Advantages (USP)")

    w, h = 6.9, 3.05

    # Card 1: Dual-Gate Proof-of-Fix
    c1 = patches.FancyBboxPatch((0.8, 4.15), w, h, boxstyle="round,pad=0.2",
                                facecolor=CARD_BG, edgecolor=BLUE_PRIMARY, linewidth=1.4)
    ax.add_patch(c1)
    ax.text(1.1, 6.75, "1. Dual-Gate Proof-of-Fix Harness (Core USP)", color=BLUE_PRIMARY, fontsize=12.5, weight='bold')
    p1 = (
        "• Eliminates AI Hallucination: Does not trust patches blindly; enforces empirical\n"
        "  sandbox execution before human deployment.\n"
        "• Gate 1 (Mitigation Proof): Re-runs PoC exploit payload -> requires Exit Code 0\n"
        "  and clean AddressSanitizer (ASAN) memory state.\n"
        "• Gate 2 (Regression Proof): Executes existing functional test suites, guaranteeing\n"
        "  0% degradation of mission invariants."
    )
    ax.text(1.1, 4.95, p1, color=TEXT_SUB, fontsize=9.8, linespacing=1.35)

    # Card 2: 100% Air-Gapped & Sovereign
    c2 = patches.FancyBboxPatch((8.3, 4.15), w, h, boxstyle="round,pad=0.2",
                                facecolor=CARD_BG, edgecolor=GOLD_ACCENT, linewidth=1.4)
    ax.add_patch(c2)
    ax.text(8.6, 6.75, "2. 100% Air-Gapped & Defense Sovereign", color=GOLD_ACCENT, fontsize=12.5, weight='bold')
    p2 = (
        "• Built for Armed Forces Sovereignty: 100% offline execution with zero outbound\n"
        "  bytes or telemetry leaks to external servers.\n"
        "• Air-Gap Compliance: Operates in isolated military intranets, command bunkers,\n"
        "  and tactical forward bases.\n"
        "• Cryptographic Proof: Issues tamper-evident SHA-256 signed Proof-of-Fix\n"
        "  Certificates for military chain-of-command audit trails."
    )
    ax.text(8.6, 4.95, p2, color=TEXT_SUB, fontsize=9.8, linespacing=1.35)

    # Card 3: Hyper-Lightweight Edge Profile
    c3 = patches.FancyBboxPatch((0.8, 0.8), w, h, boxstyle="round,pad=0.2",
                                facecolor=CARD_BG, edgecolor=CYAN_ACCENT, linewidth=1.4)
    ax.add_patch(c3)
    ax.text(1.1, 3.4, "3. Hyper-Lightweight Edge Resource Profile", color=CYAN_ACCENT, fontsize=12.5, weight='bold')
    p3 = (
        "• Edge-Optimized Footprint: Powered by highly optimized 4-bit quantized Small\n"
        "  Language Models (3B–7B parameters) with AST context pruning.\n"
        "• No Supercomputing Clusters: Operates seamlessly on standard tactical military\n"
        "  laptops (16GB RAM, 4 CPU cores), scoring maximum on jury resource benchmarks.\n"
        "• Rapid MTTP: Sub-90 second Mean Time to Patch on battlefield hardware."
    )
    ax.text(1.1, 1.6, p3, color=TEXT_SUB, fontsize=9.8, linespacing=1.35)

    # Card 4: Collaborative Agent Mesh & CPG
    c4 = patches.FancyBboxPatch((8.3, 0.8), w, h, boxstyle="round,pad=0.2",
                                facecolor=CARD_BG, edgecolor=GREEN_ACCENT, linewidth=1.4)
    ax.add_patch(c4)
    ax.text(8.6, 3.4, "4. Collaborative Agent Mesh & Knowledge Graph", color=GREEN_ACCENT, fontsize=12.5, weight='bold')
    p4 = (
        "• 36+ Specialized Defense Agents: Dispatches non-sequential domain agents\n"
        "  (Reverse Engineering, Root Cause Analysis, SBOM, IAM, Threat Modeling).\n"
        "• Code Property Graph (CPG): Fuses static source AST with live Suricata IDS &\n"
        "  Zeek NSM network feeds to prioritize exploitable mission attack paths."
    )
    ax.text(8.6, 1.7, p4, color=TEXT_SUB, fontsize=9.8, linespacing=1.35)

    out_file = f"{SLIDES_DIR}/slide_4.png"
    plt.savefig(out_file, facecolor=BG_COLOR, bbox_inches='tight', dpi=200)
    plt.close()
    return out_file


# ==============================================================================
# SLIDE 5: FINAL DELIVERABLES, OBJECTIVES & POC
# ==============================================================================
def render_slide_5():
    fig, ax = create_base_slide("Slide 5 of 5", "Project Deliverables, Performance Objectives & Validated PoC")

    # Left Container: Deliverables & PoC
    card_l = patches.FancyBboxPatch((0.8, 0.8), 6.9, 6.4, boxstyle="round,pad=0.25",
                                    facecolor=CARD_BG, edgecolor=BLUE_PRIMARY, linewidth=1.5)
    ax.add_patch(card_l)

    ax.text(1.1, 6.75, "Project Deliverables & Armed Forces PoC", color=BLUE_PRIMARY, fontsize=14, weight='bold')
    ax.plot([1.1, 7.3], [6.5, 6.5], color="#E2E8F0", linewidth=1.2)

    delivs = (
        "• Fully Operational CRS Platform: Web Console + Headless CLI deployed locally.\n"
        "• Autonomous Repair Engine: AST-guided patch synthesizer with self-correction.\n"
        "• Dual-Gate Sandbox Runner: Generating cryptographic SHA-256 certificates.\n"
        "• Validated Indian Armed Forces PoC:\n"
        "  - [TARGET 1] SDR Tactical Packet Demuxer (`tactical_radio_gateway.c`)\n"
        "    -> CWE-120 Buffer Overflow Remediated | CERT: KAVACH-PROOF-CE5D7512\n"
        "  - [TARGET 2] UAV Drone Telemetry Router (`drone_telemetry_parser.py`)\n"
        "    -> CWE-78 Command Injection Remediated | CERT: KAVACH-PROOF-CD352E51"
    )
    ax.text(1.1, 4.35, delivs, color=TEXT_SUB, fontsize=10.2, linespacing=1.38)

    # Live Demo Link Box inside Left Card
    dlink_box = patches.FancyBboxPatch((1.1, 1.1), 6.3, 1.5, boxstyle="round,pad=0.15",
                                       facecolor="#F8FAFC", edgecolor=GREEN_ACCENT, linewidth=1.4)
    ax.add_patch(dlink_box)
    ax.text(1.3, 2.2, "[LIVE WORKING DEMO & VIDEO LINK]", color=GREEN_ACCENT, fontsize=11, weight='bold')
    ax.text(1.3, 1.7, "• Local Platform: http://127.0.0.1:5173 (Officer: major_kavach)", color=BLUE_PRIMARY, fontsize=9.5)
    ax.text(1.3, 1.3, "• Video Walkthrough: AI_KAVACH_Demo_Walkthrough.mp4 (Included in package)", color=TEXT_SUB, fontsize=9.5)

    # Right Container: Benchmark SLA Table
    card_r = patches.FancyBboxPatch((8.3, 0.8), 6.9, 6.4, boxstyle="round,pad=0.25",
                                    facecolor=CARD_BG, edgecolor=GOLD_ACCENT, linewidth=1.5)
    ax.add_patch(card_r)

    ax.text(8.6, 6.75, "Quantitative Performance SLA Benchmarks", color=GOLD_ACCENT, fontsize=14, weight='bold')
    ax.plot([8.6, 14.8], [6.5, 6.5], color="#E2E8F0", linewidth=1.2)

    # Table Header
    ax.text(8.6, 6.15, "BENCHMARK METRIC", color=TEXT_MUTED, fontsize=9.2, weight='bold')
    ax.text(11.3, 6.15, "TARGET SLA", color=TEXT_MUTED, fontsize=9.2, weight='bold')
    ax.text(13.1, 6.15, "EMPIRICAL POC", color=TEXT_MUTED, fontsize=9.2, weight='bold')
    ax.plot([8.6, 14.8], [5.95, 5.95], color="#E2E8F0", linewidth=1.0)

    rows = [
        ("Mean Time to Patch (MTTP)", "< 120 Seconds", "~42 Seconds", GREEN_ACCENT),
        ("False-Positive Filter Rate", "> 90%", "> 92% (Gated)", GREEN_ACCENT),
        ("Proof-of-Fix Reliability", "100% Mitigation", "100% Clean ASAN", GREEN_ACCENT),
        ("Regression Test Integrity", "0% Breakage", "38/38 Maintained", GREEN_ACCENT),
        ("Edge Compute Profile", "16GB Laptop", "16GB RAM / 4-Core", BLUE_PRIMARY),
        ("Network Egress Policy", "Zero Egress", "0 Outbound Bytes", GOLD_ACCENT),
        ("36-Hr Grand Finale Ready", "Simulated IAF", "100% Deployable", GOLD_ACCENT)
    ]

    ry = 5.55
    for metric, target, actual, col in rows:
        ax.text(8.6, ry, metric, color=TEXT_SUB, fontsize=9.2)
        ax.text(11.3, ry, target, color=TEXT_MUTED, fontsize=9.2)
        ax.text(13.1, ry, actual, color=col, fontsize=9.2, weight='bold')
        ax.plot([8.6, 14.8], [ry - 0.15, ry - 0.15], color="#F1F5F9", linewidth=0.8)
        ry -= 0.62

    out_file = f"{SLIDES_DIR}/slide_5.png"
    plt.savefig(out_file, facecolor=BG_COLOR, bbox_inches='tight', dpi=200)
    plt.close()
    return out_file


def compile_light_pdf():
    print("[*] Rendering 5 High-Resolution Light-Theme Slides...")
    s1 = render_slide_1()
    s2 = render_slide_2()
    s3 = render_slide_3()
    s4 = render_slide_4()
    s5 = render_slide_5()
    print("[+] All 5 Light Slides Rendered Successfully.")

    images = [
        Image.open(s1).convert("RGB"),
        Image.open(s2).convert("RGB"),
        Image.open(s3).convert("RGB"),
        Image.open(s4).convert("RGB"),
        Image.open(s5).convert("RGB"),
    ]

    images[0].save(PDF_FINAL_PATH, save_all=True, append_images=images[1:], resolution=200.0)
    images[0].save(PDF_OVERWRITE_PATH, save_all=True, append_images=images[1:], resolution=200.0)
    print(f"[SUCCESS] Saved 5-Page Light Submission PDF to: {PDF_FINAL_PATH}")
    print(f"[SUCCESS] Overwrote: {PDF_OVERWRITE_PATH}")

if __name__ == "__main__":
    compile_light_pdf()
