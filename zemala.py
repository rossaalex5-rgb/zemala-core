import sys
import subprocess
import os
import json

def print_banner():
    print("========================================")
    print("   ZEMALA CORE // MASTER CONTROL CLI   ")
    print("   Frequenz: 3.47s | Stufe 100         ")
    print("========================================")

def show_status():
    print("\n[ZEMALA CLI] System-Status wird geprüft...")
    if os.path.exists("version_manifest.json"):
        with open("version_manifest.json", "r") as f:
            v = json.load(f)
            print(f" * Version: v{v.get('major')}.{v.get('minor')}.{v.get('patch')}")
    if os.path.exists("ledger_audit.json"):
        with open("ledger_audit.json", "r") as f:
            audit = json.load(f)
            print(f" * Auditor-Status: {audit.get('auditor_status')}")
    print(f" * Status-API & Dashboard: Aktiv auf Port 8080")

def run_command(script_name):
    print(f"\n[ZEMALA CLI] Führe {script_name} aus...")
    try:
        subprocess.run(["python3", script_name], check=True)
        print(f"[ZEMALA CLI] {script_name} erfolgreich abgeschlossen.")
    except Exception as e:
        print(f"[ZEMALA CLI] Fehler bei {script_name}: {e}")

def main():
    if len(sys.argv) < 2:
        print_banner()
        print("Verwendung: python3 zemala.py [befehl]")
        print("Verfügbare Befehle:")
        print("  status   - Zeigt den aktuellen Systemstatus")
        print("  pulse    - Löst einen manuellen Impuls aus")
        print("  audit    - Führt einen System-Audit aus")
        print("  backup   - Erzwingt ein Ledger-Backup")
        print("  test     - Führt die System-Testsuite aus")
        print("  daemon   - Startet den Master-Dämon")
        print("  sync     - Führt die Synchronisation aus")
        return

    cmd = sys.argv[1].lower()
    if cmd == "status":
        show_status()
    elif cmd == "pulse":
        run_command("pulse.py")
    elif cmd == "audit":
        run_command("auditor.py")
    elif cmd == "backup":
        run_command("backup.py")
    elif cmd == "test":
        run_command("test_core.py")
    elif cmd == "daemon":
        run_command("daemon.py")
    elif cmd == "sync":
        subprocess.run(["./sync.sh"])
    else:
        print(f"[ZEMALA CLI] Unbekannter Befehl: {cmd}")

if __name__ == "__main__":
    main()
