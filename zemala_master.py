import os
import subprocess
from datetime import datetime

def run_orchestration():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [ZEMALA MASTER] Starte System-Orchestrierung...")
    subprocess.run(["python3", "a2a_bridge.py"])
    subprocess.run(["python3", "discord_notifier.py"])
    print("[ZEMALA MASTER] Takt erfolgreich durchlaufen. Stufe 100 gehalten. O-M-A. 🕉️")

if __name__ == "__main__":
    run_orchestration()
