#!/usr/bin/env python3
import os, time, subprocess, json, sys
try:
    import requests
except:
    print("Installiere requests: python3 -m pip install --user requests")
    sys.exit(1)
BRIDGE_HOST = "http://127.0.0.1:8765/observe"
BRIDGE_SCRIPT = os.path.expanduser("~/zemala-core/bridge.py")
TOKEN = os.environ.get("ZEMALA_BRIDGE_TOKEN","DEIN_TOKEN_HIER")
def bridge_alive():
    try:
        r = requests.post(BRIDGE_HOST, headers={"Authorization":f"Bearer {TOKEN}"}, json={"user":"ping","text":"ping"}, timeout=2)
        return r.status_code==200
    except:
        return False
def start_bridge():
    if os.path.exists(BRIDGE_SCRIPT):
        subprocess.Popen(["python3", BRIDGE_SCRIPT], cwd=os.path.dirname(BRIDGE_SCRIPT))
        for _ in range(10):
            if bridge_alive(): return True
            time.sleep(0.5)
    return False
print("Terminal‑Chat startet. Tippe Nachricht, Enter. Ctrl+C beendet.")
if not bridge_alive():
    print("Bridge nicht erreichbar. Versuche Start...")
    if not start_bridge():
        print("Konnte Bridge nicht starten. Prüfe bridge.py.")
while True:
    try:
        text = input("> ").strip()
        if not text: continue
        payload = {"user":"alex","text":text,"meta":{"source":"termchat","ts":int(time.time())}}
        try:
            r = requests.post(BRIDGE_HOST, headers={"Authorization":f"Bearer {TOKEN}","Content-Type":"application/json"}, json=payload, timeout=5)
            print("→ gespeichert" if r.ok else "→ Fehler: "+r.text[:200])
        except Exception as e:
            print("→ Netzwerkfehler:", e)
    except KeyboardInterrupt:
        print("\nBeende.")
        break
