import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PORT = 47760

CONN_LOGS = [
    {"ts": "2026-08-17T10:21:58.100000Z", "uid": "CxPb3b1Y", "proto": "tcp", "id.orig_h": "10.0.0.5", "id.resp_h": "203.0.113.7", "id.resp_p": 22, "service": "ssh", "history": "ShADadfr"},
    {"ts": "2026-08-17T10:23:03.500000Z", "uid": "C4zJcQ3r", "proto": "tcp", "id.orig_h": "198.51.100.22", "id.resp_h": "10.0.0.8", "id.resp_p": 80, "service": "http", "history": "ShADadA"},
    {"ts": "2026-08-17T10:24:54.900000Z", "uid": "C9aHkZ5t", "proto": "tcp", "id.orig_h": "10.0.0.12", "id.resp_h": "203.0.113.55", "id.resp_p": 443, "service": "ssl", "history": "ShADadA"},
]

DNS_LOGS = [
    {"ts": "2026-08-17T10:22:30.200000Z", "query": "update.evil-domain.tld", "qtype": "A", "answers": ["203.0.113.55"]},
]

HEALTH = {
    "status": "ok",
    "version": "6.1-lite",
    "backend": "zeek-nsm-lite",
    "logs": {"conn": len(CONN_LOGS), "dns": len(DNS_LOGS)},
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
        elif self.path.startswith("/logs/conn"):
            self._send(200, {"logs": CONN_LOGS, "count": len(CONN_LOGS)})
        elif self.path.startswith("/logs/dns"):
            self._send(200, {"logs": DNS_LOGS, "count": len(DNS_LOGS)})
        elif self.path.startswith("/logs"):
            self._send(200, {"logs": {"conn": CONN_LOGS, "dns": DNS_LOGS}})
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
        if method == "zeek.logs":
            self._send(200, {"result": {"conn": CONN_LOGS, "dns": DNS_LOGS}})
        else:
            self._send(200, {"result": {"ok": True, "method": method}})


def main():
    server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    server.serve_forever()


if __name__ == "__main__":
    main()