"""Server locale che salva su disco i dati inviati dal browser con POST /save?name=...; serve a raccogliere i fotogrammi dei video.

Uso: python -I tools/collector.py porta cartella
"""
import os
import re
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

FOLDER = sys.argv[2]


class Handler(BaseHTTPRequestHandler):
    def cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.send_header("Access-Control-Allow-Private-Network", "true")

    def do_OPTIONS(self):
        self.send_response(204)
        self.cors()
        self.end_headers()

    def do_GET(self):
        # Da pagine che non possono fare POST (CSP): /add?name=...&d=pezzo aggiunge in coda al file, una richiesta per immagine
        q = parse_qs(urlparse(self.path).query)
        if urlparse(self.path).path == "/add" and "name" in q:
            name = re.sub(r"[^\w.-]", "_", q["name"][0])
            with open(os.path.join(FOLDER, name), "a", encoding="utf8") as h:
                h.write(q.get("d", [""])[0])
        self.send_response(200)
        self.cors()
        self.send_header("Content-Type", "image/gif")
        self.end_headers()
        self.wfile.write(b"GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;")

    def do_POST(self):
        name = re.sub(r"[^\w.-]", "_", parse_qs(urlparse(self.path).query).get("name", ["frame"])[0])
        body = self.rfile.read(int(self.headers.get("Content-Length", 0)))
        with open(os.path.join(FOLDER, name), "wb") as h:
            h.write(body)
        self.send_response(200)
        self.cors()
        self.end_headers()
        self.wfile.write(f"salvato {name} {len(body)}".encode())


os.makedirs(FOLDER, exist_ok=True)
HTTPServer(("127.0.0.1", int(sys.argv[1])), Handler).serve_forever()
