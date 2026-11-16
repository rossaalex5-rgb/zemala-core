# Dockerfile - Zemala Docker Clean Room, unabhängige Verifikation
# Basis: python:3.11-slim, nur python3 + bash + curl
# KEIN gemini, KEIN gcloud, KEIN pip-install, KEIN Secret, KEIN .env, KEIN .gemini
# COPY-Allowlist: NUR die 6 Kernartefakte. Audit wird im Container NEU erzeugt, nie kopiert.
FROM python:3.11-slim
WORKDIR /app
COPY zemala_manifest.json zemala_orchestrator.sh STARTEN.sh verify_ledger.py ./
COPY evidence/ledger.jsonl evidence/ledger_anchor.json ./evidence/
RUN chmod +x zemala_orchestrator.sh STARTEN.sh verify_ledger.py \
 && mkdir -p /tmp/clean \
 && test ! -e /app/.env && test ! -e /app/.gemini && test ! -e /app/.config \
 && test ! -e /app/evidence/ledger_audit.json \
 && python3 --version && bash --version | head -n 1 && curl --version | head -n 1 \
 && ls -R /app \
 && echo "Build-Check: Nur 6 Kernartefakte kopiert, kein Audit, kein Secret"
ENV HOME=/tmp/clean
# ENTRYPOINT: Loopback-Node-Stub (127.0.0.1:8085, nur in diesem Container) starten,
# dann Orchestrator laufen lassen, Stub killen, Exit-Code durchreichen.
# Ohne Stub muss der Lauf NON-COMPLIANT werden (Negativ-Beweis Node).
ENTRYPOINT ["/bin/bash", "-c", "set -u; python3 -c 'import http.server; class H(http.server.BaseHTTPRequestHandler):\n def do_GET(self):\n  if self.path=="/status":\n   self.send_response(200); self.send_header("Content-Type","application/json"); self.end_headers(); self.wfile.write(b"{\\"ok\\":true}")\n  else:\n   self.send_response(404); self.end_headers()\n def log_message(self,*a,**k): pass\nimport socketserver; socketserver.TCPServer(("127.0.0.1",8085),H).serve_forever()' & STUB_PID=$!; sleep 1; bash /app/STARTEN.sh; RC=$?; kill $STUB_PID 2>/dev/null || true; cat /app/evidence/ledger_audit.json; exit $RC"]
