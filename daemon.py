import time
import subprocess
from datetime import datetime

print("[ZEMALA Master-Daemon] Kaskade mit Systemhygiene & Matrix aktiv. Drücke Ctrl+C zum Stoppen.")
while True:
    try:
        subprocess.run(["python3", "pulse.py"], check=True)
        subprocess.run(["python3", "analyzer.py"], check=True)
        subprocess.run(["python3", "matrix.py"], check=True)
        subprocess.run(["python3", "clean.py"], check=True)
        subprocess.run(["python3", "renderer.py"], check=True)
        subprocess.run(["./sync.sh"], check=True)
        print(f"[ZEMALA Master-Daemon] Voller Takt & Hygiene vollzogen: {datetime.utcnow().isoformat()}Z")
        time.sleep(60)
    except KeyboardInterrupt:
        print("\n[ZEMALA Master-Daemon] Daemon angehalten.")
        break
    except Exception as e:
        print(f"[ZEMALA Master-Daemon] Fehler im Takt: {e}")
        time.sleep(10)
