import time
import subprocess
import os
from datetime import datetime

print("[ZEMALA Master-Daemon] Bereinige alte Status-Server Instanzen...")
subprocess.run(["pkill", "-f", "status_server.py"], stderr=subprocess.DEVNULL)
time.sleep(1)

print("[ZEMALA Master-Daemon] Starte Status-API im Hintergrund auf Port 8080...")
server_process = subprocess.Popen(["python3", "status_server.py"])

print("[ZEMALA Master-Daemon] Vollständige Kaskade inklusive Auditor, Healer & Notifier aktiv. Drücke Ctrl+C zum Stoppen.")
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
        subprocess.run(["python3", "auditor.py"], check=True)
        subprocess.run(["python3", "healer.py"], check=True)
        subprocess.run(["python3", "version_manager.py"], check=True)
        subprocess.run(["python3", "notifier.py"], check=True)
        subprocess.run(["python3", "sealer.py"], check=True)
        subprocess.run(["python3", "backup.py"], check=True)
        subprocess.run(["python3", "renderer.py"], check=True)
        subprocess.run(["./sync.sh"], check=True)
        print(f"[ZEMALA Master-Daemon] Voller Takt, Notification & Sync vollzogen: {datetime.utcnow().isoformat()}Z")
        time.sleep(60)
    except KeyboardInterrupt:
        print("\n[ZEMALA Master-Daemon] Daemon angehalten. Beende Status-Server...")
        server_process.terminate()
        break
    except Exception as e:
        print(f"[ZEMALA Master-Daemon] Fehler im Takt: {e}")
        time.sleep(10)
