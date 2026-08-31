import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PORT = 5636

SIGNATURES = [
    {"sid": 2024216, "msg": "ET TROJAN Suspicious Download From External IP", "severity": 1},
    {"sid": 2019842, "msg": "ET WEB_SERVER Possible SQL Injection Attempt", "severity": 2},
    {"sid": 2026541, "msg": "ET SCAN Potential SSH Scan Inbound", "severity": 2},
    {"sid": 2029112, "msg": "ET MALWARE Generic HTTP C2 Beacon", "severity": 1},
    {"sid": 2017948, "msg": "GPL NETBIOS DCERPC NCACN-IP-TCP poorly formed packet", "severity": 3},
]

EVE_ALERTS = [
    {"timestamp": "2026-08-17T10:22:11.111+0000", "signature": "ET SCAN Potential SSH Scan Inbound", "severity": 2, "src_ip": "203.0.113.7", "dest_ip": "10.0.0.5", "dest_port": 22, "proto": "TCP"},
    {"timestamp": "2026-08-17T10:23:04.998+0000", "signature": "ET WEB_SERVER Possible SQL Injection Attempt", "severity": 2, "src_ip": "198.51.100.22", "dest_ip": "10.0.0.8", "dest_port": 80, "proto": "HTTP"},
    {"timestamp": "2026-08-17T10:24:55.221+0000", "signature": "ET MALWARE Generic HTTP C2 Beacon", "severity": 1, "src_ip": "10.0.0.12", "dest_ip": "203.0.113.55", "dest_port": 443, "proto": "TLS"},
]

HEALTH = {
    "status": "ok",
    "version": "7.0-lite",
    "backend": "suricata-ids-lite",
    "signatures": len(SIGNATURES),
    "alerts": len(EVE_ALERTS),
}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def _send(self, code, obj):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path.startswith("/health"):
            self._send(200, HEALTH)
        elif self.path.startswith("/signatures"):
            self._send(200, {"signatures": SIGNATURES})
        elif self.path.startswith("/eve"):
            self._send(200, {"alerts": EVE_ALERTS, "count": len(EVE_ALERTS)})
        else:
            self._send(404, {"error": "not found"})

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length) if length else b"{}"
        try:
            req = json.loads(raw.decode())
        except Exception:
            req = {}
        method = req.get("method", "")
        if method == "suricata.signatures":
            self._send(200, {"result": SIGNATURES})
        elif method == "suricata.reload":
            self._send(200, {"result": {"ok": True, "message": "ruleset reloaded"}})
        else:
            self._send(200, {"result": {"ok": True, "method": method}})


def main():
    server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    server.serve_forever()


if __name__ == "__main__":
    main()