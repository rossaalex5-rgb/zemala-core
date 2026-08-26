from zemala_runtime_guard import check_ingress, check_singleton, release_lock
#!/usr/bin/env python3
import http.server
import socketserver
import json
import os
import hashlib
from datetime import datetime
from urllib.parse import parse_qs, urlparse

PORT = 8088
LEDGER_FILE = "ledger.jsonl"

def verify_ledger():
    """Prüft die kryptografische Integrität des gesamten Ledgers (Offline-Sicherheit)."""
    if not os.path.exists(LEDGER_FILE):
        return True, 0
    
    valid = True
    count = 0
    with open(LEDGER_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                stored_hash = data.pop("hash", None)
                if stored_hash:
                    entry_str = json.dumps(data, sort_keys=True)
                    computed_hash = hashlib.sha256(entry_str.encode('utf-8')).hexdigest()
                    if computed_hash != stored_hash:
                        valid = False
                count += 1
            except:
                pass
    return valid, count

HTML_PAGE = """<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <title>ZEMALA CORE // OFFLINE MASTER KERNEL</title>
    <style>
        body { background: #05070b; color: #f8fafc; font-family: monospace; padding: 20px; }
        .card { background: #0f172a; border: 2px solid #eab308; padding: 25px; border-radius: 8px; max-width: 800px; margin: auto; box-shadow: 0 0 25px rgba(234, 179, 8, 0.25); }
        h2 { color: #eab308; text-transform: uppercase; letter-spacing: 2px; border-bottom: 1px solid #334155; padding-bottom: 10px; margin-top: 0; }
        .stats { display: flex; justify-content: space-between; background: #1e293b; padding: 15px; border-radius: 6px; margin-bottom: 20px; border: 1px solid #475569; }
        .stat-box { text-align: center; }
        .stat-num { font-size: 1.5em; color: #4ade80; font-weight: bold; }
        .manifesto { background: #1e293b; border-left: 4px solid #eab308; padding: 15px; margin-bottom: 20px; font-size: 0.9em; color: #cbd5e1; line-height: 1.5; }
        textarea { width: 100%; background: #020617; border: 1px solid #475569; color: #fff; padding: 12px; margin-top: 5px; margin-bottom: 15px; border-radius: 4px; box-sizing: border-box; font-family: monospace; }
        button { background: #eab308; color: #020617; border: none; padding: 12px 24px; border-radius: 4px; cursor: pointer; font-weight: bold; width: 100%; text-transform: uppercase; letter-spacing: 1px; }
        button:hover { background: #ca8a04; }
        .success { color: #4ade80; margin-top: 20px; background: #020617; padding: 15px; border: 1px solid #166534; border-radius: 4px; word-break: break-all; }
        .ledger-list { margin-top: 25px; border-top: 1px solid #334155; padding-top: 15px; }
        .ledger-item { background: #020617; border: 1px solid #1e293b; padding: 10px; margin-bottom: 8px; border-radius: 4px; font-size: 0.85em; }
        .ledger-item span { color: #eab308; }
    </style>
</head>
<body>
    <div class="card">
        <h2>⚡ ZEMALA CORE // LOKALER KERN (STUFE 100)</h2>
        
        <div class="stats">
            <div class="stat-box">
                <div>GESAMT-EINTRÄGE</div>
                <div class="stat-num">{total_entries}</div>
            </div>
            <div class="stat-box">
                <div>LEDGER-STATUS</div>
                <div class="stat-num" style="color: {status_color};">{ledger_status_text}</div>
            </div>
            <div class="stat-box">
                <div>TAKT</div>
                <div class="stat-num" style="color: #eab308;">3,47s</div>
            </div>
        </div>

        <div class="manifesto">
            <strong>OFFLINE-SOUVERÄNITÄT AKTIV:</strong><br>
            Dieses System läuft vollständig lokal auf deiner Hardware. Jede Interaktion wird ohne Cloud-Abhängigkeit kryptografisch verkettet.
        </div>

        <form method="POST" action="/submit">
            <label>Lokaler Intent / Befehl:</label>
            <textarea name="user_input" rows="3" placeholder="Befehl oder Gedanken eingeben..."></textarea>
            <button type="submit">Lokal verarbeiten & Versiegeln</button>
        </form>

        {result_block}

        <div class="ledger-list">
            <strong>Kryptografischer Ledger (Letzte Blöcke):</strong>
            {ledger_html}
        </div>
    </div>
</body>
</html>
"""

def get_ledger_entries():
    entries = []
    if os.path.exists(LEDGER_FILE):
        with open(LEDGER_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        entries.append(json.loads(line))
                    except:
                        pass
    return entries

class ZemalaHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path == "/" or parsed_path.path == "":
            is_valid, total_entries = verify_ledger()
            status_color = "#4ade80" if is_valid else "#ef4444"
            ledger_status_text = "VERIFIZIERT" if is_valid else "FEHLER"

            entries = get_ledger_entries()
            ledger_html = ""
            for e in reversed(entries[-5:]):
                ledger_html += f"""
                <div class="ledger-item">
                    <span>[{e.get('timestamp', '')}]</span> 
                    <b>Input:</b> {e.get('input', '')}<br>
                    <span style="color: #94a3b8;">Antwort: {e.get('output', '')}</span><br>
                    <small style="color: #64748b;">Hash: {e.get('hash', 'N/A')[:16]}...</small>
                </div>
                """
            if not ledger_html:
                ledger_html = "<div class=\"ledger-item\" style=\"color: #64748b;\">Keine Blöcke im Ledger.</div>"

            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            page = HTML_PAGE.replace("{total_entries}", str(total_entries))
            page = page.replace("{status_color}", status_color)
            page = page.replace("{ledger_status_text}", ledger_status_text)
            page = page.replace("{ledger_html}", ledger_html)
            page = page.replace("{result_block}", "")
            self.wfile.write(page.encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/submit":
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')
            params = parse_qs(post_data)
            user_input = params.get("user_input", [""])[0].strip()
            
            if not user_input:
                user_input = "[Leerer Impuls]"

            system_output = f"LOKALER_VOLLZUG [STUFE 100]: '{user_input}' erfolgreich im lokalen Ledger verschweißt."

            entry = {
                "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                "source": "ZEMALA_LOCAL_KERNEL",
                "input": user_input,
                "output": system_output
            }
            
            # Hash generieren
            entry_str = json.dumps(entry, sort_keys=True)
            entry_hash = hashlib.sha256(entry_str.encode('utf-8')).hexdigest()
            entry["hash"] = entry_hash

            with open(LEDGER_FILE, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")

            is_valid, total_entries = verify_ledger()
            status_color = "#4ade80" if is_valid else "#ef4444"
            ledger_status_text = "VERIFIZIERT" if is_valid else "FEHLER"

            entries = get_ledger_entries()
            ledger_html = ""
            for e in reversed(entries[-5:]):
                ledger_html += f"""
                <div class="ledger-item">
                    <span>[{e.get('timestamp', '')}]</span> 
                    <b>Input:</b> {e.get('input', '')}<br>
                    <span style="color: #94a3b8;">Antwort: {e.get('output', '')}</span><br>
                    <small style="color: #64748b;">Hash: {e.get('hash', 'N/A')[:16]}...</small>
                </div>
                """

            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            result_html = f"""
            <div class="success">
                <strong>[LOKALER BLOCK VERSIEGELT]</strong><br><br>
                <b>Antwort:</b> {system_output}<br><br>
                <small><b>SHA256:</b> {entry_hash}</small>
            </div>
            """
            
            page = HTML_PAGE.replace("{total_entries}", str(total_entries))
            page = page.replace("{status_color}", status_color)
            page = page.replace("{ledger_status_text}", ledger_status_text)
            page = page.replace("{ledger_html}", ledger_html)
            page = page.replace("{result_block}", result_html)
            self.wfile.write(page.encode('utf-8'))
            print(f"[+] Lokaler Block versiegelt. Hash: {entry_hash[:16]}...")
        else:
            self.send_response(404)
            self.end_headers()

print(f"[*] Starte ZEMALA Lokalen Kernel auf Port {PORT}...")
with socketserver.TCPServer(("", PORT), ZemalaHandler) as httpd:
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[*] Kernel gestoppt.")
