import time
import subprocess
from datetime import datetime

print("[ZEMALA Daemon] Kaskaden-Herzschlag mit integrierter Analytik aktiv. Drücke Ctrl+C zum Stoppen.")
while True:
    try:
        subprocess.run(["python3", "pulse.py"], check=True)
        subprocess.run(["python3", "analyzer.py"], check=True)
        subprocess.run(["./sync.sh"], check=True)
        print(f"[ZEMALA Daemon] Takt & Analyse vollzogen: {datetime.utcnow().isoformat()}Z")
        time.sleep(60)
    except KeyboardInterrupt:
        print("\n[ZEMALA Daemon] Daemon angehalten.")
        break
    except Exception as e:
        print(f"[ZEMALA Daemon] Fehler im Takt: {e}")
        time.sleep(10)
