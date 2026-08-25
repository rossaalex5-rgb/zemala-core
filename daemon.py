import time
import subprocess
from datetime import datetime

print("[ZEMALA Daemon] Kaskaden-Herzschlag aktiv. Drücke Ctrl+C zum Stoppen.")
while True:
    try:
        subprocess.run(["python3", "pulse.py"], check=True)
        subprocess.run(["./sync.sh"], check=True)
        print(f"[ZEMALA Daemon] Takt vollzogen: {datetime.utcnow().isoformat()}Z")
        time.sleep(60)  # Ein Impuls pro Minute im Datenstrom
    except KeyboardInterrupt:
        print("\n[ZEMALA Daemon] Daemon angehalten.")
        break
