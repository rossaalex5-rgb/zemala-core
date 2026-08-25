import time
import subprocess
from datetime import datetime

print("[ZEMALA Daemon] Vollständiger Kaskaden-Herzschlag (Pulse + Analyzer + Renderer) aktiv. Drücke Ctrl+C zum Stoppen.")
while True:
    try:
        subprocess.run(["python3", "pulse.py"], check=True)
        subprocess.run(["python3", "analyzer.py"], check=True)
        subprocess.run(["python3", "renderer.py"], check=True)
        subprocess.run(["./sync.sh"], check=True)
        print(f"[ZEMALA Daemon] Voller Takt vollzogen: {datetime.utcnow().isoformat()}Z")
        time.sleep(60)
    except KeyboardInterrupt:
        print("\n[ZEMALA Daemon] Daemon angehalten.")
        break
    except Exception as e:
        print(f"[ZEMALA Daemon] Fehler im Takt: {e}")
        time.sleep(10)
