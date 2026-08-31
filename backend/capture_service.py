import datetime
import io
import threading
import time

import psutil
from fpdf import FPDF

from database import (
    create_capture_session,
    get_capture_session,
    update_capture_session,
    add_packet,
    get_packets_all,
    count_packets_by_session,
)

_captures = {}


def _proto_name(sock_type, sock_family):
    if sock_type == 1:
        return "TCP"
    if sock_type == 2:
        return "UDP"
    if sock_type == 3:
        return "ICMP"
    return str(sock_type)


def _process_name(pid):
    try:
        return psutil.Process(pid).name()
    except Exception:
        return ""


def _key(conn):
    return (conn.pid, conn.fd, conn.family, conn.type, conn.laddr, conn.raddr)


def _run_capture(session_id, stop_event):
    seen = set()
    while not stop_event.is_set():
        try:
            conns = psutil.net_connections()
        except (psutil.AccessDenied, psutil.Error):
            conns = []
        now = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
        for c in conns:
            k = _key(c)
            if k in seen:
                continue
            seen.add(k)
            if not c.laddr:
                continue
            laddr = c.laddr
            lport = laddr.port if hasattr(laddr, "port") else None
            local_ip = laddr.ip if hasattr(laddr, "ip") else ""
            remote_ip = c.raddr.ip if c.raddr else ""
            rport = c.raddr.port if c.raddr and hasattr(c.raddr, "port") else None
            proto = _proto_name(c.type, c.family)
            state = c.status or ""
            proc = _process_name(c.pid) if c.pid else ""
            if proto == "TCP" and c.raddr:
                src, sport, dst, dport = local_ip, lport, remote_ip, rport
                direction = "in" if proc else "conn"
                info = f"{src}:{sport} -> {dst}:{dport} [{state}]"
            elif proto == "TCP":
                src, sport, dst, dport = "0.0.0.0", lport, "", None
                info = f"LISTEN on {local_ip}:{lport}"
            elif proto == "UDP" and c.raddr:
                src, sport, dst, dport = local_ip, lport, remote_ip, rport
                info = f"{src}:{sport} -> {dst}:{dport} (UDP)"
            else:
                src, sport, dst, dport = local_ip, lport, remote_ip, rport
                info = f"{local_ip}:{lport} <- {remote_ip}:{rport}"
            size = 64
            try:
                add_packet(
                    session_id, now, src, sport, dst, dport, proto, size,
                    state, proc or "unknown", info,
                )
            except Exception:
                pass
        time.sleep(0.5)
    stop_event.set()


def start_capture(user_id, interface):
    session_id = create_capture_session(user_id, interface)
    stop_event = threading.Event()
    thread = threading.Thread(
        target=_run_capture, args=(session_id, stop_event), daemon=True
    )
    _captures[session_id] = {"thread": thread, "stop": stop_event}
    thread.start()
    return session_id


def stop_capture(session_id):
    cap = _captures.get(session_id)
    if cap is None:
        session = get_capture_session(session_id)
        if session is None:
            raise ValueError("Capture session not found")
        return session
    cap["stop"].set()
    cap["thread"].join(timeout=5)
    count = count_packets_by_session(session_id)
    update_capture_session(
        session_id,
        "stopped",
        count,
        datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    )
    _captures.pop(session_id, None)
    return get_capture_session(session_id)


def _escape(text):
    return "".join(ch for ch in str(text) if ord(ch) >= 32 or ch in "\n\t")


def generate_pdf(session):
    session_id = session["id"]
    packets = get_packets_all(session_id)
    total_size = sum(p["size"] or 0 for p in packets)

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 10, "CyberLens - Network Capture Report", ln=True)
    pdf.ln(3)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, f"Session ID: {session_id}", ln=True)
    pdf.cell(0, 6, f"Interface: {session['interface'] or 'all'}", ln=True)
    pdf.cell(0, 6, f"Status: {session['status']}", ln=True)
    pdf.cell(0, 6, f"Started: {session['started_at']}", ln=True)
    if session["stopped_at"]:
        pdf.cell(0, 6, f"Stopped: {session['stopped_at']}", ln=True)
    pdf.cell(0, 6, f"Packets captured: {len(packets)}", ln=True)
    pdf.cell(0, 6, f"Approx. bytes: {total_size}", ln=True)
    pdf.ln(5)

    protocols = {}
    for p in packets:
        protocols[p["protocol"]] = protocols.get(p["protocol"], 0) + 1

    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 8, "Protocol Breakdown", ln=True)
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(40, 7, "Protocol", border=1)
    pdf.cell(40, 7, "Count", border=1)
    pdf.cell(60, 7, "Percentage", border=1)
    pdf.ln()
    pdf.set_font("Helvetica", "", 9)
    for proto, count in sorted(protocols.items(), key=lambda x: -x[1]):
        pct = f"{count / len(packets) * 100:.1f}%" if packets else "0%"
        pdf.cell(40, 7, _escape(proto), border=1)
        pdf.cell(40, 7, str(count), border=1)
        pdf.cell(60, 7, pct, border=1)
        pdf.ln()
    pdf.ln(5)

    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 8, "Captured Packets", ln=True)
    cols = [
        ("Time", 18),
        ("Source", 34),
        ("Dest", 34),
        ("Proto", 18),
        ("Info", 84),
    ]
    pdf.set_font("Helvetica", "B", 8)
    for name, w in cols:
        pdf.cell(w, 6, name, border=1)
    pdf.ln()
    pdf.set_font("Helvetica", "", 8)
    for p in packets:
        row = [
            _escape(p["timestamp"]),
            _escape(p["src"] or ""),
            _escape(p["dst"] or ""),
            _escape(p["protocol"] or ""),
            _escape(p["info"] or ""),
        ]
        for value, (_, w) in zip(row, cols):
            pdf.cell(w, 6, value[: int(w / 1.4)], border=1)
        pdf.ln()

    return bytes(pdf.output(dest="S"))


def active_capture_count():
    return len(_captures)


def capture_is_running(session_id):
    return session_id in _captures