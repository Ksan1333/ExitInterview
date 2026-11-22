#!/usr/bin/env python3
"""The same room server on your own computer, with rooms kept in memory.

    python3 server/local_server.py [port]        (default 8080; set EI_KEY to require a key)

Used by the automatic two-player checks, and as a spare if AWS cannot be used.
"""
import json
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import lambda_function as room

STORE = room.MemStore()
LOCK = threading.Lock()


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def _send(self, body):
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("content-type", "application/json")
        self.send_header("content-length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        self._send({"ok": True, "name": "exit-interview"})

    def do_POST(self):
        raw = self.rfile.read(int(self.headers.get("content-length") or 0))
        try:
            q = json.loads(raw.decode("utf-8"))
        except ValueError:
            q = None
        with LOCK:
            body = room.handle(q, STORE)
        self._send(body)

    def log_message(self, fmt, *args):
        pass


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    print("room server on http://0.0.0.0:%d  (Ctrl+C to stop)" % port, flush=True)
    ThreadingHTTPServer(("0.0.0.0", port), Handler).serve_forever()
