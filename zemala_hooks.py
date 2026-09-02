import json
from pathlib import Path
from zemala_core import ZemalaLedger

class ZemalaHookManager:
    def __init__(self, ledger: ZemalaLedger):
        self.ledger = ledger
        self.hooks = []

    def register_hook(self, event_type: str, callback_func):
        """Registriert eine lokale Aktion für einen spezifischen Event-Typ."""
        self.hooks.append({"event_type": event_type, "callback": callback_func})

    def process_latest(self):
        """Prüft den letzten Ledger-Eintrag und feuert passende Hooks fehlsicher ab."""
        if not self.ledger.ledger_path.exists():
            return

        last_line = ""
        with open(self.ledger.ledger_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    last_line = line

        if not last_line:
            return

        try:
            entry = json.loads(last_line)
            data = entry.get("data", {})
            event_type = data.get("event_type") or data.get("event")

            # Hooks ausführen
            for hook in self.hooks:
                if hook["event_type"] == event_type or hook["event_type"] == "*":
                    try:
                        # Hook ausführen mit isoliertem Try-Catch (Fail-Safe)
                        hook["callback"](entry)
                    except Exception as e:
                        # Fehler wird als sicheres Event geloggt, bricht aber nie das Ledger ab
                        self.ledger.append({
                            "event_type": "HOOK_ERROR",
                            "error": str(e),
                            "failed_hook": event_type
                        })
        except json.JSONDecodeError:
            pass

# --- BEISPIEL-TEST FÜR LOKALE HOOKS ---
if __name__ == "__main__":
    print("Initializing ZEMALA Hook Manager...")
    ledger = ZemalaLedger("zemala_test.jsonl")
    manager = ZemalaHookManager(ledger)

    # Definieren wir einen lokalen Hook (z.B. für System- oder Smart-Home-Aktionen)
    def local_action_handler(entry):
        print(f"[HOOK TRIGGERD] Reagiere auf Zustand: {entry.get('hash')[:12]}...")
        payload = entry.get("data", {})
        print(f"  -> Verarbeite Payload: {json.dumps(payload)}")

    # Hook registrieren
    manager.register_hook("A2A_COMMUNICATION", local_action_handler)
    manager.register_hook("GENESIS", local_action_handler)

    # Letzten Zustand / Hooks ausführen
    manager.process_latest()
    print("Hooks executed successfully on local edge state.")
