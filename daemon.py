import time
import subprocess
from datetime import datetime

print("[ZEMALA Master-Daemon] Vollständige Kaskade inklusive Analytics aktiv. Drücke Ctrl+C zum Stoppen.")
while True:
    try:
        subprocess.run(["python3", "pulse.py"], check=True)
        subprocess.run(["python3", "analyzer.py"], check=True)
        subprocess.run(["python3", "matrix.py"], check=True)
        subprocess.run(["python3", "clean.py"], check=True)
        subprocess.run(["python3", "inference_hook.py"], check=True)
        subprocess.run(["python3", "agent_loop.py"], check=True)
        subprocess.run(["python3", "telemetry.py"], check=True)
        subprocess.run(["python3", "metadata_optimizer.py"], check=True)
        subprocess.run(["python3", "ledger_analytics.py"], check=True)
        subprocess.run(["python3", "sealer.py"], check=True)
        subprocess.run(["python3", "renderer.py"], check=True)
        subprocess.run(["./sync.sh"], check=True)
        print(f"[ZEMALA Master-Daemon] Voller Takt & Analytics vollzogen: {datetime.utcnow().isoformat()}Z")
        time.sleep(60)
    except KeyboardInterrupt:
        print("\n[ZEMALA Master-Daemon] Daemon angehalten.")
        break
    except Exception as e:
        print(f"[ZEMALA Master-Daemon] Fehler im Takt: {e}")
        time.sleep(10)
