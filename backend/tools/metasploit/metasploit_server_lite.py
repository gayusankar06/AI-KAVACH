import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PORT = 55553

MODULES = [
    {"path": "exploit/multi/http/struts2_content_type_ognl", "rank": "excellent", "target": "Apache Struts 2"},
    {"path": "exploit/multi/http/tomcat_mgr_upload", "rank": "excellent", "target": "Apache Tomcat"},
    {"path": "exploit/multi/http/wp_crop_rce", "rank": "excellent", "target": "WordPress"},
    {"path": "exploit/multi/script/web_delivery", "rank": "excellent", "target": "Generic Web"},
    {"path": "exploit/multi/http/nagios_xi_autodiscovery_webshell", "rank": "good", "target": "Nagios XI"},
    {"path": "exploit/multi/http/rails_actionpack_inline_exec", "rank": "excellent", "target": "Ruby on Rails"},
    {"path": "auxiliary/scanner/http/http_version", "rank": "normal", "target": "Any HTTP"},
    {"path": "auxiliary/scanner/portscan/tcp", "rank": "normal", "target": "Any TCP"},
]

HEALTH = {
    "status": "ok",
    "version": "6.4-lite",
    "backend": "metasploit-rpc-lite",
    "modules": len(MODULES),
    "rpc": "http://127.0.0.1:55553",
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
        elif self.path.startswith("/modules"):
            self._send(200, {"modules": MODULES})
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
        if method == "module.list":
            self._send(200, {"result": MODULES})
        elif method == "core.version":
            self._send(200, {"result": {"version": "6.4-lite", "ruby": "3.2.2"}})
        elif method == "db.status":
            self._send(200, {"result": {"db": "connected"}})
        else:
            self._send(200, {"result": {"ok": True, "method": method}})


def main():
    server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    server.serve_forever()


if __name__ == "__main__":
    main()