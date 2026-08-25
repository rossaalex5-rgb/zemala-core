import json
from datetime import datetime

def render_status():
    try:
        with open("ledger.jsonl", "r") as f:
            lines = f.readlines()
        
        total_events = len(lines)
        last_event = json.loads(lines[-1]) if lines else {}
        
        html_content = f"""<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ZEMALA Core - Live Status</title>
    <style>
        body {{ background-color: #0b0f19; color: #f8fafc; font-family: monospace; padding: 20px; margin: 0; }}
        .card {{ background: #1e293b; padding: 20px; border-radius: 12px; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.5); max-width: 600px; margin: auto; border: 1px solid #334155; }}
        h1 {{ color: #fbbf24; font-size: 1.4rem; margin-top: 0; }}
        .metric {{ font-size: 1.1rem; margin: 12px 0; border-bottom: 1px solid #334155; padding-bottom: 6px; }}
        .highlight {{ color: #34d399; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="card">
        <h1>⚡ ZEMALA Live-Feld</h1>
        <div class="metric">System-Status: <span class="highlight">Stufe 100 (Aktiv)</span></div>
        <div class="metric">Gesamt-Events im Ledger: <span class="highlight">{total_events}</span></div>
        <div class="metric">Letzter Takt: <span class="highlight">{datetime.utcnow().isoformat()}Z</span></div>
        <div class="metric">Letztes Event: {last_event.get('message', 'N/A')}</div>
    </div>
</body>
</html>
"""
        with open("index.html", "w") as f:
            f.write(html_content)
        print("[ZEMALA Renderer] index.html erfolgreich für den Browser aktualisiert.")
    except Exception as e:
        print(f"[ZEMALA Renderer] Fehler beim Rendern: {e}")

if __name__ == "__main__":
    render_status()
