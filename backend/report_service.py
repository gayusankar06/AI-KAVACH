from datetime import datetime

from fpdf import FPDF

from database import (
    get_projects_by_user,
    get_pentest_results,
    get_capture_sessions_by_user,
)


def _escape(text):
    if text is None:
        return ""
    return "".join(ch for ch in str(text) if ord(ch) >= 32 or ch in "\n\t")


def collect_report_data(user_id):
    projects = get_projects_by_user(user_id)
    capture_sessions = get_capture_sessions_by_user(user_id)

    project_list = []
    for p in projects:
        results = get_pentest_results(p["id"])
        project_list.append(
            {
                "id": p["id"],
                "name": p["name"],
                "source_type": p["source_type"],
                "source_url": p["source_url"],
                "created_at": p["created_at"],
                "results": [dict(r) for r in results],
            }
        )

    session_list = [
        {
            "id": s["id"],
            "interface": s["interface"],
            "status": s["status"],
            "packet_count": s["packet_count"],
            "started_at": s["started_at"],
            "stopped_at": s["stopped_at"],
        }
        for s in capture_sessions
    ]

    return {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "projects": project_list,
        "capture_sessions": session_list,
        "totals": {
            "projects": len(project_list),
            "findings": sum(len(p["results"]) for p in project_list),
            "captures": len(session_list),
            "packets": sum(s["packet_count"] for s in session_list),
        },
    }


class ReportPDF(FPDF):
    LEFT = 15
    RIGHT = 15
    CONTENT_W = 210 - 15 - 15  # 180 mm usable width

    def __init__(self):
        super().__init__()
        self.set_margins(self.LEFT, 15, self.RIGHT)
        self.set_auto_page_break(auto=True, margin=15)

    def section_bar(self, text):
        self.set_fill_color(30, 41, 59)
        self.set_text_color(147, 197, 253)
        self.set_font("Helvetica", "B", 13)
        self.cell(0, 9, text, fill=True, new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(0, 0, 0)
        self.ln(2)

    def info_line(self, label, value):
        self.set_font("Helvetica", "", 10)
        self.cell(45, 6, _escape(label), new_x="RIGHT", new_y="TOP")
        self.set_font("Helvetica", "B", 10)
        self.cell(0, 6, _escape(value), new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

    def table_header(self, widths, labels):
        self.set_font("Helvetica", "B", 9)
        self.set_fill_color(226, 232, 240)
        self.set_text_color(51, 65, 85)
        for w, label in zip(widths, labels):
            self.cell(w, 7, label, border=1, fill=True, new_x="RIGHT", new_y="TOP")
        self.ln()
        self.set_text_color(0, 0, 0)

    def table_row(self, widths, values, height=6.5):
        self.set_font("Helvetica", "", 9)
        for w, value in zip(widths, values):
            self.cell(w, height, _escape(value), border=1, new_x="RIGHT", new_y="TOP")
        self.ln()

    def finding_row(self, widths, date, tool, summary):
        date_w, tool_w, summary_w = widths
        self.set_font("Helvetica", "", 8)
        self.cell(date_w, 7, _escape(date), border=1, new_x="RIGHT", new_y="TOP")
        self.cell(tool_w, 7, _escape(tool), border=1, new_x="RIGHT", new_y="TOP")
        self.multi_cell(
            summary_w,
            5.5,
            _escape(summary),
            border=1,
            new_x="LMARGIN",
            new_y="NEXT",
        )
        self.ln(1)


def generate_report_pdf(user_id, username):
    data = collect_report_data(user_id)
    totals = data["totals"]
    pdf = ReportPDF()
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 20)
    pdf.cell(0, 12, "CyberLens Security Report", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)
    pdf.info_line("Generated for", username)
    pdf.info_line("Generated at", data["generated_at"])
    pdf.ln(4)

    pdf.section_bar("Executive Summary")
    rows = [
        ("Projects analyzed", str(totals["projects"])),
        ("Total AI findings stored", str(totals["findings"])),
        ("Network capture sessions", str(totals["captures"])),
        ("Total packets captured", str(totals["packets"])),
    ]
    pdf.table_header([135, 45], ["Item", "Count"])
    for label, value in rows:
        pdf.table_row([135, 45], [label, value])
    pdf.ln(6)

    tool_counts = {}
    for p in data["projects"]:
        for r in p["results"]:
            tool_counts[r["tool"]] = tool_counts.get(r["tool"], 0) + 1
    if tool_counts:
        pdf.section_bar("Findings by Tool")
        pdf.table_header([135, 45], ["Tool", "Findings"])
        for tool, count in sorted(tool_counts.items(), key=lambda x: -x[1]):
            pdf.table_row([135, 45], [tool, str(count)])
        pdf.ln(6)

    widths_findings = [28, 38, ReportPDF.CONTENT_W - 66]

    for project in data["projects"]:
        pdf.section_bar(f"Project: {project['name']}")
        pdf.info_line("Source", project["source_type"])
        if project["source_url"]:
            pdf.info_line("Target", project["source_url"])
        pdf.info_line("Added", project["created_at"])
        pdf.ln(2)

        if not project["results"]:
            pdf.set_font("Helvetica", "I", 9)
            pdf.cell(0, 6, "No AI findings recorded for this project.", new_x="LMARGIN", new_y="NEXT")
            pdf.ln(6)
            continue

        pdf.table_header(widths_findings, ["Date", "Tool", "Finding"])
        for r in project["results"]:
            pdf.finding_row(
                widths_findings,
                r["created_at"][:16],
                r["tool"],
                r["summary"] or "No summary",
            )
        pdf.ln(4)

    if data["capture_sessions"]:
        pdf.section_bar("Network Capture Sessions")
        widths_sessions = [22, 52, 40, 33, 33]
        pdf.table_header(
            widths_sessions, ["ID", "Started", "Interface", "Packets", "Status"]
        )
        for s in data["capture_sessions"]:
            pdf.table_row(
                widths_sessions,
                [str(s["id"]), s["started_at"], s["interface"], str(s["packet_count"]), s["status"]],
            )
        pdf.ln(4)

    pdf.section_bar("How to Read This Report")
    pdf.set_font("Helvetica", "", 9)
    for line in [
        "1. Executive Summary gives the overall counts for this report.",
        "2. Findings by Tool shows how many results each AI tool produced.",
        "3. Each project section lists every stored finding with date, tool and full analysis.",
        "4. Network Capture Sessions summarises packet captures stored in the database.",
    ]:
        pdf.cell(0, 6, line, new_x="LMARGIN", new_y="NEXT")

    return bytes(pdf.output(dest="S"))